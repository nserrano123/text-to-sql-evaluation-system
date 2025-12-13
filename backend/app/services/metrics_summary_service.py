"""Service for aggregating all metrics into a summary"""

from ..models.metrics_summary import MetricsSummary
from ..repositories.evaluation_repository import EvaluationRepository
from .execution_accuracy_service import ExecutionAccuracyService
from .time_to_answer_service import TimeToAnswerService
from .component_matching_service import ComponentMatchingService


class MetricsSummaryService:
    """Service for aggregating all evaluation metrics"""
    
    def __init__(
        self,
        evaluation_repository: EvaluationRepository,
        execution_accuracy_service: ExecutionAccuracyService,
        time_to_answer_service: TimeToAnswerService,
        component_matching_service: ComponentMatchingService
    ):
        self.evaluation_repository = evaluation_repository
        self.execution_accuracy_service = execution_accuracy_service
        self.time_to_answer_service = time_to_answer_service
        self.component_matching_service = component_matching_service
    
    def get_metrics_summary(self) -> MetricsSummary:
        """
        Aggregate all metrics into a single summary object.
        
        Returns:
            MetricsSummary: Object containing all aggregated metrics
        """
        # Get total and completed evaluation counts
        all_evaluations = self.evaluation_repository.get_all()
        total_evaluations = len(all_evaluations)
        
        # For completed evaluations, we need to check which ones have associated metrics
        execution_accuracy_records = self.execution_accuracy_service.repository.get_all()
        completed_evaluations = len(execution_accuracy_records)
        
        # Calculate individual metrics
        execution_accuracy = self.execution_accuracy_service.calculate_ex(execution_accuracy_records)
        
        time_to_answer_records = self.time_to_answer_service.repository.get_all()
        average_time_to_answer = self.time_to_answer_service.calculate_average_tta(time_to_answer_records)
        
        component_matching_records = self.component_matching_service.repository.get_all()
        component_scores = self.component_matching_service.calculate_component_f1_scores(component_matching_records)
        
        return MetricsSummary(
            execution_accuracy=execution_accuracy,
            average_time_to_answer=average_time_to_answer,
            component_scores=component_scores,
            total_evaluations=total_evaluations,
            completed_evaluations=completed_evaluations
        )