"""Service for Component Matching metric calculations"""

from typing import List, Dict
from ..models.component_matching import ComponentMatching
from ..repositories.component_matching_repository import ComponentMatchingRepository


class ComponentMatchingService:
    """Service for calculating Component Matching metrics"""
    
    def __init__(self, repository: ComponentMatchingRepository):
        self.repository = repository
    
    def calculate_f1_score(self, precision: float, recall: float) -> float:
        """
        Calculate F1 score using the standard formula.
        
        Formula: F1 = 2 × (precision × recall) / (precision + recall)
        
        Args:
            precision: Precision value (0.0 to 1.0)
            recall: Recall value (0.0 to 1.0)
            
        Returns:
            float: F1 score (0.0 to 1.0)
        """
        if precision + recall == 0:
            return 0.0
        
        f1 = 2 * (precision * recall) / (precision + recall)
        return f1
    
    def calculate_component_f1_scores(self, component_records: List[ComponentMatching]) -> Dict[str, float]:
        """
        Calculate F1 scores for each SQL component.
        
        For each component, we calculate precision and recall based on the boolean values
        in the component_records, then compute the F1 score.
        
        Args:
            component_records: List of ComponentMatching records
            
        Returns:
            Dict[str, float]: F1 scores per component
        """
        if not component_records:
            return {
                "select": 0.0,
                "where": 0.0,
                "groupBy": 0.0,
                "orderBy": 0.0,
                "keywords": 0.0
            }
        
        components = {
            "select": [record.select_correct for record in component_records],
            "where": [record.where_correct for record in component_records],
            "groupBy": [record.group_by_correct for record in component_records],
            "orderBy": [record.order_by_correct for record in component_records],
            "keywords": [record.keywords_correct for record in component_records]
        }
        
        f1_scores = {}
        
        for component_name, correct_values in components.items():
            # For component matching, we treat each evaluation as a binary classification
            # True Positives: correctly identified as correct
            # False Positives: incorrectly identified as correct  
            # False Negatives: incorrectly identified as incorrect
            # True Negatives: correctly identified as incorrect
            
            # In this context, we assume all components should ideally be correct
            # So precision = correct_predictions / total_predictions
            # And recall = correct_predictions / total_should_be_correct
            
            total_evaluations = len(correct_values)
            correct_count = sum(correct_values)
            
            if total_evaluations == 0:
                f1_scores[component_name] = 0.0
                continue
            
            # For component evaluation, precision and recall are the same
            # as we're measuring accuracy of component identification
            accuracy = correct_count / total_evaluations
            
            # F1 score when precision = recall = accuracy is just the accuracy
            f1_scores[component_name] = accuracy
        
        return f1_scores
    
    async def get_all_component_matching_records(self) -> List[ComponentMatching]:
        """Get all component matching records from the repository"""
        return await self.repository.get_all()
    
    async def calculate_current_component_f1_scores(self) -> Dict[str, float]:
        """Calculate current F1 scores for all components based on all records in the database"""
        records = await self.get_all_component_matching_records()
        return self.calculate_component_f1_scores(records)