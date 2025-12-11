"""Service for Execution Accuracy (EX) metric calculations"""

from typing import List
from ..models.execution_accuracy import ExecutionAccuracy
from ..repositories.execution_accuracy_repository import ExecutionAccuracyRepository


class ExecutionAccuracyService:
    """Service for calculating Execution Accuracy metrics"""
    
    def __init__(self, repository: ExecutionAccuracyRepository):
        self.repository = repository
    
    def calculate_ex(self, execution_accuracy_records: List[ExecutionAccuracy]) -> float:
        """
        Calculate Execution Accuracy (EX) percentage.
        
        Formula: (consultas correctas / total) × 100
        
        Args:
            execution_accuracy_records: List of ExecutionAccuracy records
            
        Returns:
            float: EX percentage formatted to 2 decimal places
        """
        if not execution_accuracy_records:
            return 0.0
        
        correct_count = sum(1 for record in execution_accuracy_records if record.is_correct)
        total_count = len(execution_accuracy_records)
        
        ex_percentage = (correct_count / total_count) * 100
        
        # Format to 2 decimal places as required
        return round(ex_percentage, 2)
    
    async def get_all_execution_accuracy_records(self) -> List[ExecutionAccuracy]:
        """Get all execution accuracy records from the repository"""
        return await self.repository.get_all()
    
    async def calculate_current_ex(self) -> float:
        """Calculate current EX based on all records in the database"""
        records = await self.get_all_execution_accuracy_records()
        return self.calculate_ex(records)