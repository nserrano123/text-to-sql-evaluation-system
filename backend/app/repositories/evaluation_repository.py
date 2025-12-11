"""Repository for evaluations table operations"""

from typing import List, Optional
from uuid import UUID
from supabase import Client
from app.database import get_supabase_client
from app.models.evaluation import Evaluation, EvaluationCreate


class EvaluationRepository:
    """Repository class for evaluations table CRUD operations"""
    
    def __init__(self, client: Optional[Client] = None):
        """Initialize repository with Supabase client"""
        self.client = client or get_supabase_client()
        self.table_name = 'evaluations'
    
    def create(self, evaluation: EvaluationCreate) -> Evaluation:
        """Create a new evaluation record"""
        try:
            # Verify that the gold_query_id exists
            gold_query_check = self.client.table('gold_queries').select('id').eq(
                'id', str(evaluation.gold_query_id)
            ).execute()
            
            if not gold_query_check.data:
                raise ValueError(f"Gold query with ID {evaluation.gold_query_id} does not exist")
            
            result = self.client.table(self.table_name).insert(
                evaluation.model_dump()
            ).execute()
            
            if not result.data:
                raise ValueError("Failed to create evaluation - no data returned")
            
            return Evaluation(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to create evaluation: {str(e)}")
    
    def get_by_id(self, evaluation_id: UUID) -> Optional[Evaluation]:
        """Get an evaluation by its ID"""
        try:
            result = self.client.table(self.table_name).select("*").eq(
                'id', str(evaluation_id)
            ).execute()
            
            if not result.data:
                return None
            
            return Evaluation(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to get evaluation by ID: {str(e)}")
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Evaluation]:
        """Get all evaluations with optional pagination"""
        try:
            query = self.client.table(self.table_name).select("*").order('evaluation_date', desc=True)
            
            if limit is not None:
                query = query.limit(limit)
            
            if offset is not None:
                query = query.offset(offset)
            
            result = query.execute()
            
            return [Evaluation(**row) for row in result.data]
        except Exception as e:
            raise RuntimeError(f"Failed to get all evaluations: {str(e)}")
    
    def update(self, evaluation_id: UUID, evaluation_data: dict) -> Optional[Evaluation]:
        """Update an evaluation record"""
        try:
            # First check if the evaluation exists
            existing = self.get_by_id(evaluation_id)
            if not existing:
                return None
            
            # If updating gold_query_id, verify it exists
            if 'gold_query_id' in evaluation_data:
                gold_query_check = self.client.table('gold_queries').select('id').eq(
                    'id', str(evaluation_data['gold_query_id'])
                ).execute()
                
                if not gold_query_check.data:
                    raise ValueError(f"Gold query with ID {evaluation_data['gold_query_id']} does not exist")
            
            result = self.client.table(self.table_name).update(
                evaluation_data
            ).eq('id', str(evaluation_id)).execute()
            
            if not result.data:
                return None
            
            return Evaluation(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to update evaluation: {str(e)}")
    
    def delete(self, evaluation_id: UUID) -> bool:
        """Delete an evaluation record"""
        try:
            # First check if the evaluation exists
            existing = self.get_by_id(evaluation_id)
            if not existing:
                return False
            
            result = self.client.table(self.table_name).delete().eq(
                'id', str(evaluation_id)
            ).execute()
            
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete evaluation: {str(e)}")
    
    def get_by_gold_query_id(self, gold_query_id: UUID) -> List[Evaluation]:
        """Get all evaluations for a specific gold query"""
        try:
            result = self.client.table(self.table_name).select("*").eq(
                'gold_query_id', str(gold_query_id)
            ).order('evaluation_date', desc=True).execute()
            
            return [Evaluation(**row) for row in result.data]
        except Exception as e:
            raise RuntimeError(f"Failed to get evaluations by gold query ID: {str(e)}")
    
    def count_total(self) -> int:
        """Get total count of evaluations"""
        try:
            result = self.client.table(self.table_name).select(
                'id', count='exact'
            ).execute()
            
            return result.count or 0
        except Exception as e:
            raise RuntimeError(f"Failed to count evaluations: {str(e)}")
    
    def exists_for_gold_query(self, gold_query_id: UUID) -> bool:
        """Check if any evaluation exists for a given gold query"""
        try:
            result = self.client.table(self.table_name).select('id').eq(
                'gold_query_id', str(gold_query_id)
            ).limit(1).execute()
            
            return len(result.data) > 0
        except Exception as e:
            raise RuntimeError(f"Failed to check evaluation existence: {str(e)}")