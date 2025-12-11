"""Repository for gold_queries table operations"""

from typing import List, Optional
from uuid import UUID
from supabase import Client
from app.database import get_supabase_client
from app.models.gold_query import GoldQuery, GoldQueryCreate


class GoldQueryRepository:
    """Repository class for gold_queries table CRUD operations"""
    
    def __init__(self, client: Optional[Client] = None):
        """Initialize repository with Supabase client"""
        self.client = client or get_supabase_client()
        self.table_name = 'gold_queries'
    
    def create(self, gold_query: GoldQueryCreate) -> GoldQuery:
        """Create a new gold query record"""
        try:
            result = self.client.table(self.table_name).insert(
                gold_query.model_dump()
            ).execute()
            
            if not result.data:
                raise ValueError("Failed to create gold query - no data returned")
            
            return GoldQuery(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to create gold query: {str(e)}")
    
    def get_by_id(self, gold_query_id: UUID) -> Optional[GoldQuery]:
        """Get a gold query by its ID"""
        try:
            result = self.client.table(self.table_name).select("*").eq(
                'id', str(gold_query_id)
            ).execute()
            
            if not result.data:
                return None
            
            return GoldQuery(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to get gold query by ID: {str(e)}")
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[GoldQuery]:
        """Get all gold queries with optional pagination"""
        try:
            query = self.client.table(self.table_name).select("*").order('created_at', desc=True)
            
            if limit is not None:
                query = query.limit(limit)
            
            if offset is not None:
                query = query.offset(offset)
            
            result = query.execute()
            
            return [GoldQuery(**row) for row in result.data]
        except Exception as e:
            raise RuntimeError(f"Failed to get all gold queries: {str(e)}")
    
    def get_pending(self) -> List[GoldQuery]:
        """Get gold queries that have no associated evaluations (pending evaluation)"""
        try:
            # Use a left join to find gold_queries without evaluations
            result = self.client.rpc('get_pending_gold_queries').execute()
            
            if not result.data:
                # Fallback: get all gold queries and filter manually
                # This is less efficient but works if the RPC function doesn't exist
                all_queries = self.get_all()
                pending_queries = []
                
                for query in all_queries:
                    # Check if this query has any evaluations
                    eval_result = self.client.table('evaluations').select('id').eq(
                        'gold_query_id', str(query.id)
                    ).limit(1).execute()
                    
                    if not eval_result.data:
                        pending_queries.append(query)
                
                return pending_queries
            
            return [GoldQuery(**row) for row in result.data]
        except Exception as e:
            # Fallback to manual filtering if RPC fails
            try:
                all_queries = self.get_all()
                pending_queries = []
                
                for query in all_queries:
                    # Check if this query has any evaluations
                    eval_result = self.client.table('evaluations').select('id').eq(
                        'gold_query_id', str(query.id)
                    ).limit(1).execute()
                    
                    if not eval_result.data:
                        pending_queries.append(query)
                
                return pending_queries
            except Exception as fallback_e:
                raise RuntimeError(f"Failed to get pending gold queries: {str(e)}, fallback error: {str(fallback_e)}")
    
    def count_total(self) -> int:
        """Get total count of gold queries"""
        try:
            result = self.client.table(self.table_name).select(
                'id', count='exact'
            ).execute()
            
            return result.count or 0
        except Exception as e:
            raise RuntimeError(f"Failed to count gold queries: {str(e)}")
    
    def count_pending(self) -> int:
        """Get count of pending gold queries"""
        try:
            pending_queries = self.get_pending()
            return len(pending_queries)
        except Exception as e:
            raise RuntimeError(f"Failed to count pending gold queries: {str(e)}")