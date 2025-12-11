"""Repository for time_to_answer table operations"""

from typing import List, Optional
from uuid import UUID
from supabase import Client
from app.database import get_supabase_client
from app.models.time_to_answer import TimeToAnswer, TimeToAnswerCreate


class TimeToAnswerRepository:
    """Repository class for time_to_answer table CRUD operations"""
    
    def __init__(self, client: Optional[Client] = None):
        """Initialize repository with Supabase client"""
        self.client = client or get_supabase_client()
        self.table_name = 'time_to_answer'
    
    def create(self, time_to_answer: TimeToAnswerCreate) -> TimeToAnswer:
        """Create a new time to answer record"""
        try:
            # Verify that the evaluation_id exists
            evaluation_check = self.client.table('evaluations').select('id').eq(
                'id', str(time_to_answer.evaluation_id)
            ).execute()
            
            if not evaluation_check.data:
                raise ValueError(f"Evaluation with ID {time_to_answer.evaluation_id} does not exist")
            
            result = self.client.table(self.table_name).insert(
                time_to_answer.model_dump()
            ).execute()
            
            if not result.data:
                raise ValueError("Failed to create time to answer record - no data returned")
            
            return TimeToAnswer(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to create time to answer record: {str(e)}")
    
    def get_by_id(self, time_to_answer_id: UUID) -> Optional[TimeToAnswer]:
        """Get a time to answer record by its ID"""
        try:
            result = self.client.table(self.table_name).select("*").eq(
                'id', str(time_to_answer_id)
            ).execute()
            
            if not result.data:
                return None
            
            return TimeToAnswer(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to get time to answer by ID: {str(e)}")
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[TimeToAnswer]:
        """Get all time to answer records with optional pagination"""
        try:
            query = self.client.table(self.table_name).select("*").order('created_at', desc=True)
            
            if limit is not None:
                query = query.limit(limit)
            
            if offset is not None:
                query = query.offset(offset)
            
            result = query.execute()
            
            return [TimeToAnswer(**row) for row in result.data]
        except Exception as e:
            raise RuntimeError(f"Failed to get all time to answer records: {str(e)}")
    
    def update(self, time_to_answer_id: UUID, time_to_answer_data: dict) -> Optional[TimeToAnswer]:
        """Update a time to answer record"""
        try:
            # First check if the record exists
            existing = self.get_by_id(time_to_answer_id)
            if not existing:
                return None
            
            # If updating evaluation_id, verify it exists
            if 'evaluation_id' in time_to_answer_data:
                evaluation_check = self.client.table('evaluations').select('id').eq(
                    'id', str(time_to_answer_data['evaluation_id'])
                ).execute()
                
                if not evaluation_check.data:
                    raise ValueError(f"Evaluation with ID {time_to_answer_data['evaluation_id']} does not exist")
            
            result = self.client.table(self.table_name).update(
                time_to_answer_data
            ).eq('id', str(time_to_answer_id)).execute()
            
            if not result.data:
                return None
            
            return TimeToAnswer(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to update time to answer record: {str(e)}")
    
    def delete(self, time_to_answer_id: UUID) -> bool:
        """Delete a time to answer record"""
        try:
            # First check if the record exists
            existing = self.get_by_id(time_to_answer_id)
            if not existing:
                return False
            
            result = self.client.table(self.table_name).delete().eq(
                'id', str(time_to_answer_id)
            ).execute()
            
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete time to answer record: {str(e)}")
    
    def get_by_evaluation_id(self, evaluation_id: UUID) -> Optional[TimeToAnswer]:
        """Get time to answer record for a specific evaluation"""
        try:
            result = self.client.table(self.table_name).select("*").eq(
                'evaluation_id', str(evaluation_id)
            ).execute()
            
            if not result.data:
                return None
            
            return TimeToAnswer(**result.data[0])
        except Exception as e:
            raise RuntimeError(f"Failed to get time to answer by evaluation ID: {str(e)}")
    
    def get_average_duration(self) -> float:
        """Get average duration in seconds across all records"""
        try:
            result = self.client.table(self.table_name).select('duration_seconds').execute()
            
            if not result.data:
                return 0.0
            
            durations = [row['duration_seconds'] for row in result.data]
            return sum(durations) / len(durations)
        except Exception as e:
            raise RuntimeError(f"Failed to calculate average duration: {str(e)}")
    
    def get_all_durations(self) -> List[float]:
        """Get all duration values for statistical analysis"""
        try:
            result = self.client.table(self.table_name).select('duration_seconds').execute()
            
            return [row['duration_seconds'] for row in result.data]
        except Exception as e:
            raise RuntimeError(f"Failed to get all durations: {str(e)}")
    
    def count_total(self) -> int:
        """Get total count of time to answer records"""
        try:
            result = self.client.table(self.table_name).select(
                'id', count='exact'
            ).execute()
            
            return result.count or 0
        except Exception as e:
            raise RuntimeError(f"Failed to count time to answer records: {str(e)}")