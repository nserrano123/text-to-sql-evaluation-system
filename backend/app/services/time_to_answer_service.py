"""Service for Time-to-Answer (TTA) metric calculations"""

from typing import List
from datetime import datetime
from ..models.time_to_answer import TimeToAnswer
from ..repositories.time_to_answer_repository import TimeToAnswerRepository


class TimeToAnswerService:
    """Service for calculating Time-to-Answer metrics"""
    
    def __init__(self, repository: TimeToAnswerRepository):
        self.repository = repository
    
    def calculate_tta(self, start_time: datetime, end_time: datetime) -> float:
        """
        Calculate Time-to-Answer (TTA) as the difference between end_time and start_time.
        
        Args:
            start_time: Timestamp when evaluation started
            end_time: Timestamp when evaluation completed
            
        Returns:
            float: Duration in seconds
        """
        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        
        duration = (end_time - start_time).total_seconds()
        return duration
    
    def calculate_average_tta(self, time_to_answer_records: List[TimeToAnswer]) -> float:
        """
        Calculate average Time-to-Answer from a list of TTA records.
        
        Args:
            time_to_answer_records: List of TimeToAnswer records
            
        Returns:
            float: Average duration in seconds
        """
        if not time_to_answer_records:
            return 0.0
        
        total_duration = sum(record.duration_seconds for record in time_to_answer_records)
        average_duration = total_duration / len(time_to_answer_records)
        
        return average_duration
    
    async def get_all_time_to_answer_records(self) -> List[TimeToAnswer]:
        """Get all time to answer records from the repository"""
        return await self.repository.get_all()
    
    async def calculate_current_average_tta(self) -> float:
        """Calculate current average TTA based on all records in the database"""
        records = await self.get_all_time_to_answer_records()
        return self.calculate_average_tta(records)