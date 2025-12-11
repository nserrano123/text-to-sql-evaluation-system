"""Repository for execution_accuracy table operations"""

from typing import List, Optional
from uuid import UUID
from supabase import Client
from app.database import get_supabase_client
from app.models.execution_accuracy import ExecutionAccuracy, ExecutionAccuracyCreate


class ExecutionAccuracyRepository:
    """Repository class for execution_accuracy table CRUD operations"""
    
    def __init__(self, client: Optional[Client] = None):
        """Initialize repository with Supabase client"""
        self.client = client or get_supabase_client()
        self.table_name = 'execution_accuracy'
    
    def create(self, execution_accuracy: ExecutionAccuracyCreate) -> ExecutionAccuracy:
        """Create a new execution accuracy record"""
        try:
            # Verify that the evaluation_id exists
            evaluation_check = self.client.table('evaluations').select('id').eq(
                'id', str(execution_accuracy.evaluation_id)
            ).execute()
            
            if not evaluation_check.data:
                raise ValueError(f"Evaluation with ID {execution_accuracy.evaluation_id} does not exist")
            
            result = self.client.table(self.table_name).insert(
                execution_accuracy.model_dump()
            ).execute()
            
            if not result.data:
                raise ValueError("Failed to create execution accuracy record - no data returned")
            
            return ExecutionAccuracy(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to create execution accuracy record: {str(e)}")
    
    def get_by_id(self, execution_accuracy_id: UUID) -> Optional[ExecutionAccuracy]:
        """Get an execution accuracy record by its ID"""
        try:
            result = self.client.table(self.table_name).select("*").eq(
                'id', str(execution_accuracy_id)
            ).execute()
            
            if not result.data:
                return None
            
            return ExecutionAccuracy(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to get execution accuracy by ID: {str(e)}")
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ExecutionAccuracy]:
        """Get all execution accuracy records with optional pagination"""
        try:
            query = self.client.table(self.table_name).select("*").order('created_at', desc=True)
            
            if limit is not None:
                query = query.limit(limit)
            
            if offset is not None:
                query = query.offset(offset)
            
            result = query.execute()
            
            return [ExecutionAccuracy(**row) for row in result.data]
        except Exception as e:
            raise RuntimeError(f"Failed to get all execution accuracy records: {str(e)}")
    
    def update(self, execution_accuracy_id: UUID, execution_accuracy_data: dict) -> Optional[ExecutionAccuracy]:
        """Update an execution accuracy record"""
        try:
            # First check if the record exists
            existing = self.get_by_id(execution_accuracy_id)
            if not existing:
                return None
            
            # If updating evaluation_id, verify it exists
            if 'evaluation_id' in execution_accuracy_data:
                evaluation_check = self.client.table('evaluations').select('id').eq(
                    'id', str(execution_accuracy_data['evaluation_id'])
                ).execute()
                
                if not evaluation_check.data:
                    raise ValueError(f"Evaluation with ID {execution_accuracy_data['evaluation_id']} does not exist")
            
            result = self.client.table(self.table_name).update(
                execution_accuracy_data
            ).eq('id', str(execution_accuracy_id)).execute()
            
            if not result.data:
                return None
            
            return ExecutionAccuracy(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to update execution accuracy record: {str(e)}")
    
    def delete(self, execution_accuracy_id: UUID) -> bool:
        """Delete an execution accuracy record"""
        try:
            # First check if the record exists
            existing = self.get_by_id(execution_accuracy_id)
            if not existing:
                return False
            
            result = self.client.table(self.table_name).delete().eq(
                'id', str(execution_accuracy_id)
            ).execute()
            
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete execution accuracy record: {str(e)}")
    
    def get_by_evaluation_id(self, evaluation_id: UUID) -> Optional[ExecutionAccuracy]:
        """Get execution accuracy record for a specific evaluation"""
        try:
            result = self.client.table(self.table_name).select("*").eq(
                'evaluation_id', str(evaluation_id)
            ).execute()
            
            if not result.data:
                return None
            
            return ExecutionAccuracy(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to get execution accuracy by evaluation ID: {str(e)}")
    
    def count_correct(self) -> int:
        """Get count of correct evaluations (is_correct = true)"""
        try:
            result = self.client.table(self.table_name).select(
                'id', count='exact'
            ).eq('is_correct', True).execute()
            
            return result.count or 0
        except Exception as e:
            raise RuntimeError(f"Failed to count correct evaluations: {str(e)}")
    
    def count_total(self) -> int:
        """Get total count of execution accuracy records"""
        try:
            result = self.client.table(self.table_name).select(
                'id', count='exact'
            ).execute()
            
            return result.count or 0
        except Exception as e:
            raise RuntimeError(f"Failed to count execution accuracy records: {str(e)}")