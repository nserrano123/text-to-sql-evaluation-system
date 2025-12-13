"""API endpoints for evaluations operations"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..models.evaluation import Evaluation, EvaluationCreate, CompleteEvaluationCreate
from ..repositories.evaluation_repository import EvaluationRepository
from ..services.evaluation_service import EvaluationService

router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])


@router.get("/", response_model=List[Evaluation])
async def get_all_evaluations(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of records to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of records to skip")
) -> List[Evaluation]:
    """
    Get all evaluations with optional pagination.
    
    Args:
        limit: Maximum number of records to return (1-1000)
        offset: Number of records to skip for pagination
        
    Returns:
        List[Evaluation]: List of evaluation records
        
    Raises:
        HTTPException: 500 if database operation fails
    """
    try:
        repository = EvaluationRepository()
        return repository.get_all(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve evaluations: {str(e)}")


@router.get("/{evaluation_id}", response_model=Evaluation)
async def get_evaluation_by_id(evaluation_id: UUID) -> Evaluation:
    """
    Get a specific evaluation by its ID.
    
    Args:
        evaluation_id: UUID of the evaluation to retrieve
        
    Returns:
        Evaluation: The requested evaluation record
        
    Raises:
        HTTPException: 404 if evaluation not found, 500 if database operation fails
    """
    try:
        repository = EvaluationRepository()
        evaluation = repository.get_by_id(evaluation_id)
        
        if not evaluation:
            raise HTTPException(status_code=404, detail=f"Evaluation with ID {evaluation_id} not found")
        
        return evaluation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve evaluation: {str(e)}")


@router.post("/", response_model=Evaluation, status_code=201)
async def create_evaluation(evaluation_data: CompleteEvaluationCreate) -> Evaluation:
    """
    Create a new complete evaluation record with all related metrics.
    
    This endpoint creates:
    - The main evaluation record
    - Execution accuracy record with time tracking (Requirements 4.1, 4.2)
    - Time to answer record
    - Component matching record
    
    Args:
        evaluation_data: Complete evaluation data including time tracking
        
    Returns:
        Evaluation: The created evaluation record
        
    Raises:
        HTTPException: 400 if validation fails or foreign key constraint violated, 
                      500 if database operation fails
    """
    try:
        service = EvaluationService()
        return service.create_complete_evaluation(evaluation_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create evaluation: {str(e)}")


@router.post("/simple", response_model=Evaluation, status_code=201)
async def create_simple_evaluation(evaluation_data: EvaluationCreate) -> Evaluation:
    """
    Create a simple evaluation record (without metrics).
    
    Args:
        evaluation_data: Basic evaluation data to create
        
    Returns:
        Evaluation: The created evaluation record
        
    Raises:
        HTTPException: 400 if validation fails or foreign key constraint violated, 
                      500 if database operation fails
    """
    try:
        repository = EvaluationRepository()
        return repository.create(evaluation_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create evaluation: {str(e)}")


@router.put("/{evaluation_id}", response_model=Evaluation)
async def update_evaluation(
    evaluation_id: UUID, 
    evaluation_data: Dict[str, Any]
) -> Evaluation:
    """
    Update an existing evaluation record.
    
    Args:
        evaluation_id: UUID of the evaluation to update
        evaluation_data: Dictionary containing fields to update
        
    Returns:
        Evaluation: The updated evaluation record
        
    Raises:
        HTTPException: 404 if evaluation not found, 400 if validation fails,
                      500 if database operation fails
    """
    try:
        repository = EvaluationRepository()
        updated_evaluation = repository.update(evaluation_id, evaluation_data)
        
        if not updated_evaluation:
            raise HTTPException(status_code=404, detail=f"Evaluation with ID {evaluation_id} not found")
        
        return updated_evaluation
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update evaluation: {str(e)}")


@router.delete("/{evaluation_id}", status_code=204)
async def delete_evaluation(evaluation_id: UUID) -> None:
    """
    Delete an evaluation record.
    
    Args:
        evaluation_id: UUID of the evaluation to delete
        
    Raises:
        HTTPException: 404 if evaluation not found, 500 if database operation fails
    """
    try:
        repository = EvaluationRepository()
        success = repository.delete(evaluation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Evaluation with ID {evaluation_id} not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete evaluation: {str(e)}")