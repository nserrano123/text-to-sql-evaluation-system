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
    
    async def get_metrics_summary(self) -> MetricsSummary:
        """
        Aggregate all metrics into a single summary object.
        
        Returns:
            MetricsSummary: Object containing all aggregated metrics
        """
        # Get total and completed evaluation counts
        all_evaluations = await self.evaluation_repository.get_all()
        total_evaluations = len(all_evaluations)
        
        # For completed evaluations, we need to check which ones have associated metrics
        execution_accuracy_records = await self.execution_accuracy_service.get_all_execution_accuracy_records()
        completed_evaluations = len(execution_accuracy_records)
        
        # Calculate individual metrics
        execution_accuracy = await self.execution_accuracy_service.calculate_current_ex()
        average_time_to_answer = await self.time_to_answer_service.calculate_current_average_tta()
        component_scores = await self.component_matching_service.calculate_current_component_f1_scores()
        
        return MetricsSummary(
            execution_accuracy=execution_accuracy,
            average_time_to_answer=average_time_to_answer,
            component_scores=component_scores,
            total_evaluations=total_evaluations,
            completed_evaluations=completed_evaluations
        )