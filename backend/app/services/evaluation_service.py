"""Service for handling complete evaluation operations"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from ..models.evaluation import Evaluation, EvaluationCreate, CompleteEvaluationCreate
from ..models.execution_accuracy import ExecutionAccuracyCreate
from ..models.time_to_answer import TimeToAnswerCreate
from ..models.component_matching import ComponentMatchingCreate
from ..repositories.evaluation_repository import EvaluationRepository
from ..repositories.execution_accuracy_repository import ExecutionAccuracyRepository
from ..repositories.time_to_answer_repository import TimeToAnswerRepository
from ..repositories.component_matching_repository import ComponentMatchingRepository


class EvaluationService:
    """Service for handling complete evaluation operations"""
    
    def __init__(
        self,
        evaluation_repo: Optional[EvaluationRepository] = None,
        execution_accuracy_repo: Optional[ExecutionAccuracyRepository] = None,
        time_to_answer_repo: Optional[TimeToAnswerRepository] = None,
        component_matching_repo: Optional[ComponentMatchingRepository] = None
    ):
        self.evaluation_repo = evaluation_repo or EvaluationRepository()
        self.execution_accuracy_repo = execution_accuracy_repo or ExecutionAccuracyRepository()
        self.time_to_answer_repo = time_to_answer_repo or TimeToAnswerRepository()
        self.component_matching_repo = component_matching_repo or ComponentMatchingRepository()
    
    def create_complete_evaluation(self, evaluation_data: CompleteEvaluationCreate) -> Evaluation:
        """
        Create a complete evaluation with all related metrics.
        
        This method handles the creation of:
        1. The main evaluation record
        2. Execution accuracy record
        3. Time to answer record
        4. Component matching record
        
        Args:
            evaluation_data: Complete evaluation data
            
        Returns:
            Evaluation: The created evaluation record
            
        Raises:
            ValueError: If validation fails or foreign key constraints are violated
            RuntimeError: If database operations fail
        """
        try:
            # Create the main evaluation record
            evaluation_create = EvaluationCreate(
                gold_query_id=evaluation_data.gold_query_id,
                generated_sql=evaluation_data.generated_sql
            )
            
            evaluation = self.evaluation_repo.create(evaluation_create)
            
            # Create execution accuracy record
            execution_accuracy_create = ExecutionAccuracyCreate(
                evaluation_id=evaluation.id,
                results_match=evaluation_data.execution_accuracy.results_match,
                is_correct=evaluation_data.execution_accuracy.is_correct,
                evaluator_notes=evaluation_data.execution_accuracy.evaluator_notes
            )
            
            self.execution_accuracy_repo.create(execution_accuracy_create)
            
            # Create time to answer record
            time_to_answer_create = TimeToAnswerCreate(
                evaluation_id=evaluation.id,
                start_time=evaluation_data.time_to_answer.start_time,
                end_time=evaluation_data.time_to_answer.end_time,
                duration_seconds=evaluation_data.time_to_answer.duration_seconds
            )
            
            self.time_to_answer_repo.create(time_to_answer_create)
            
            # Create component matching record
            component_matching_create = ComponentMatchingCreate(
                evaluation_id=evaluation.id,
                select_correct=evaluation_data.component_matching.select_correct,
                where_correct=evaluation_data.component_matching.where_correct,
                group_by_correct=evaluation_data.component_matching.group_by_correct,
                order_by_correct=evaluation_data.component_matching.order_by_correct,
                keywords_correct=evaluation_data.component_matching.keywords_correct,
                f1_score=evaluation_data.component_matching.f1_score,
                evaluator_notes=evaluation_data.component_matching.evaluator_notes
            )
            
            self.component_matching_repo.create(component_matching_create)
            
            return evaluation
            
        except Exception as e:
            # If any step fails, we should ideally rollback the transaction
            # For now, we'll re-raise the exception
            raise RuntimeError(f"Failed to create complete evaluation: {str(e)}")