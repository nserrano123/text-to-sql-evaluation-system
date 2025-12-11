"""Repository for component_matching table operations"""

from typing import List, Optional, Dict
from uuid import UUID
from supabase import Client
from app.database import get_supabase_client
from app.models.component_matching import ComponentMatching, ComponentMatchingCreate


class ComponentMatchingRepository:
    """Repository class for component_matching table CRUD operations"""
    
    def __init__(self, client: Optional[Client] = None):
        """Initialize repository with Supabase client"""
        self.client = client or get_supabase_client()
        self.table_name = 'component_matching'
    
    def create(self, component_matching: ComponentMatchingCreate) -> ComponentMatching:
        """Create a new component matching record"""
        try:
            # Verify that the evaluation_id exists
            evaluation_check = self.client.table('evaluations').select('id').eq(
                'id', str(component_matching.evaluation_id)
            ).execute()
            
            if not evaluation_check.data:
                raise ValueError(f"Evaluation with ID {component_matching.evaluation_id} does not exist")
            
            result = self.client.table(self.table_name).insert(
                component_matching.model_dump()
            ).execute()
            
            if not result.data:
                raise ValueError("Failed to create component matching record - no data returned")
            
            return ComponentMatching(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to create component matching record: {str(e)}")
    
    def get_by_id(self, component_matching_id: UUID) -> Optional[ComponentMatching]:
        """Get a component matching record by its ID"""
        try:
            result = self.client.table(self.table_name).select("*").eq(
                'id', str(component_matching_id)
            ).execute()
            
            if not result.data:
                return None
            
            return ComponentMatching(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to get component matching by ID: {str(e)}")
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ComponentMatching]:
        """Get all component matching records with optional pagination"""
        try:
            query = self.client.table(self.table_name).select("*").order('created_at', desc=True)
            
            if limit is not None:
                query = query.limit(limit)
            
            if offset is not None:
                query = query.offset(offset)
            
            result = query.execute()
            
            return [ComponentMatching(**row) for row in result.data]
        except Exception as e:
            raise RuntimeError(f"Failed to get all component matching records: {str(e)}")
    
    def update(self, component_matching_id: UUID, component_matching_data: dict) -> Optional[ComponentMatching]:
        """Update a component matching record"""
        try:
            # First check if the record exists
            existing = self.get_by_id(component_matching_id)
            if not existing:
                return None
            
            # If updating evaluation_id, verify it exists
            if 'evaluation_id' in component_matching_data:
                evaluation_check = self.client.table('evaluations').select('id').eq(
                    'id', str(component_matching_data['evaluation_id'])
                ).execute()
                
                if not evaluation_check.data:
                    raise ValueError(f"Evaluation with ID {component_matching_data['evaluation_id']} does not exist")
            
            result = self.client.table(self.table_name).update(
                component_matching_data
            ).eq('id', str(component_matching_id)).execute()
            
            if not result.data:
                return None
            
            return ComponentMatching(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to update component matching record: {str(e)}")
    
    def delete(self, component_matching_id: UUID) -> bool:
        """Delete a component matching record"""
        try:
            # First check if the record exists
            existing = self.get_by_id(component_matching_id)
            if not existing:
                return False
            
            result = self.client.table(self.table_name).delete().eq(
                'id', str(component_matching_id)
            ).execute()
            
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete component matching record: {str(e)}")
    
    def get_by_evaluation_id(self, evaluation_id: UUID) -> Optional[ComponentMatching]:
        """Get component matching record for a specific evaluation"""
        try:
            result = self.client.table(self.table_name).select("*").eq(
                'evaluation_id', str(evaluation_id)
            ).execute()
            
            if not result.data:
                return None
            
            return ComponentMatching(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to get component matching by evaluation ID: {str(e)}")
    
    def get_component_averages(self) -> Dict[str, float]:
        """Get average scores for each component across all evaluations"""
        try:
            result = self.client.table(self.table_name).select(
                'select_correct, where_correct, group_by_correct, order_by_correct, keywords_correct'
            ).execute()
            
            if not result.data:
                return {
                    'select': 0.0,
                    'where': 0.0,
                    'group_by': 0.0,
                    'order_by': 0.0,
                    'keywords': 0.0
                }
            
            total_records = len(result.data)
            
            # Count true values for each component
            select_correct = sum(1 for row in result.data if row['select_correct'])
            where_correct = sum(1 for row in result.data if row['where_correct'])
            group_by_correct = sum(1 for row in result.data if row['group_by_correct'])
            order_by_correct = sum(1 for row in result.data if row['order_by_correct'])
            keywords_correct = sum(1 for row in result.data if row['keywords_correct'])
            
            return {
                'select': select_correct / total_records,
                'where': where_correct / total_records,
                'group_by': group_by_correct / total_records,
                'order_by': order_by_correct / total_records,
                'keywords': keywords_correct / total_records
            }
        except Exception as e:
            raise RuntimeError(f"Failed to calculate component averages: {str(e)}")
    
    def get_average_f1_score(self) -> float:
        """Get average F1 score across all records that have F1 scores"""
        try:
            result = self.client.table(self.table_name).select('f1_score').not_.is_('f1_score', 'null').execute()
            
            if not result.data:
                return 0.0
            
            f1_scores = [row['f1_score'] for row in result.data if row['f1_score'] is not None]
            
            if not f1_scores:
                return 0.0
            
            return sum(f1_scores) / len(f1_scores)
        except Exception as e:
            raise RuntimeError(f"Failed to calculate average F1 score: {str(e)}")
    
    def count_total(self) -> int:
        """Get total count of component matching records"""
        try:
            result = self.client.table(self.table_name).select(
                'id', count='exact'
            ).execute()
            
            return result.count or 0
        except Exception as e:
            raise RuntimeError(f"Failed to count component matching records: {str(e)}")