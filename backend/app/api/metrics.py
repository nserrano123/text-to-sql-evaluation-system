"""API endpoints for metrics operations"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..models.metrics_summary import MetricsSummary
from ..repositories.execution_accuracy_repository import ExecutionAccuracyRepository
from ..repositories.time_to_answer_repository import TimeToAnswerRepository
from ..repositories.component_matching_repository import ComponentMatchingRepository
from ..repositories.evaluation_repository import EvaluationRepository
from ..services.execution_accuracy_service import ExecutionAccuracyService
from ..services.time_to_answer_service import TimeToAnswerService
from ..services.component_matching_service import ComponentMatchingService
from ..services.metrics_summary_service import MetricsSummaryService

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/execution-accuracy", response_model=Dict[str, float])
async def get_execution_accuracy() -> Dict[str, float]:
    """
    Calculate and return the current Execution Accuracy (EX) percentage.
    
    Returns:
        Dict[str, float]: Dictionary containing the EX percentage
        
    Raises:
        HTTPException: 500 if calculation fails
    """
    try:
        repository = ExecutionAccuracyRepository()
        service = ExecutionAccuracyService(repository)
        
        # Get all execution accuracy records
        records = repository.get_all()
        
        # Calculate EX percentage
        ex_percentage = service.calculate_ex(records)
        
        return {"execution_accuracy": ex_percentage}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate execution accuracy: {str(e)}")


@router.get("/time-to-answer", response_model=Dict[str, float])
async def get_time_to_answer() -> Dict[str, float]:
    """
    Calculate and return the average Time-to-Answer (TTA) in seconds.
    
    Returns:
        Dict[str, float]: Dictionary containing the average TTA
        
    Raises:
        HTTPException: 500 if calculation fails
    """
    try:
        repository = TimeToAnswerRepository()
        service = TimeToAnswerService(repository)
        
        # Get all time to answer records
        records = repository.get_all()
        
        # Calculate average TTA
        average_tta = service.calculate_average_tta(records)
        
        return {"average_time_to_answer": average_tta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate time to answer: {str(e)}")


@router.get("/component-matching", response_model=Dict[str, Any])
async def get_component_matching() -> Dict[str, Any]:
    """
    Calculate and return F1 scores for each SQL component.
    
    Returns:
        Dict[str, Any]: Dictionary containing F1 scores per component
        
    Raises:
        HTTPException: 500 if calculation fails
    """
    try:
        repository = ComponentMatchingRepository()
        service = ComponentMatchingService(repository)
        
        # Get all component matching records
        records = repository.get_all()
        
        # Calculate F1 scores for each component
        component_scores = service.calculate_component_f1_scores(records)
        
        return {"component_scores": component_scores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate component matching: {str(e)}")


@router.get("/summary", response_model=MetricsSummary)
async def get_metrics_summary() -> MetricsSummary:
    """
    Get a comprehensive summary of all evaluation metrics.
    
    Returns:
        MetricsSummary: Object containing all aggregated metrics
        
    Raises:
        HTTPException: 500 if calculation fails
    """
    try:
        # Initialize repositories
        evaluation_repository = EvaluationRepository()
        execution_accuracy_repository = ExecutionAccuracyRepository()
        time_to_answer_repository = TimeToAnswerRepository()
        component_matching_repository = ComponentMatchingRepository()
        
        # Initialize services
        execution_accuracy_service = ExecutionAccuracyService(execution_accuracy_repository)
        time_to_answer_service = TimeToAnswerService(time_to_answer_repository)
        component_matching_service = ComponentMatchingService(component_matching_repository)
        
        # Initialize metrics summary service
        metrics_summary_service = MetricsSummaryService(
            evaluation_repository,
            execution_accuracy_service,
            time_to_answer_service,
            component_matching_service
        )
        
        # Get aggregated metrics summary
        summary = await metrics_summary_service.get_metrics_summary()
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate metrics summary: {str(e)}")