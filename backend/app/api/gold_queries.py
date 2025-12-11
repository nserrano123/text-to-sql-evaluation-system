"""API endpoints for gold_queries operations"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from ..models.gold_query import GoldQuery, GoldQueryCreate
from ..repositories.gold_query_repository import GoldQueryRepository

router = APIRouter(prefix="/api/gold-queries", tags=["gold-queries"])


@router.get("/", response_model=List[GoldQuery])
async def get_all_gold_queries(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of records to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of records to skip")
) -> List[GoldQuery]:
    """
    Get all gold queries with optional pagination.
    
    Args:
        limit: Maximum number of records to return (1-1000)
        offset: Number of records to skip for pagination
        
    Returns:
        List[GoldQuery]: List of gold query records
        
    Raises:
        HTTPException: 500 if database operation fails
    """
    try:
        repository = GoldQueryRepository()
        return repository.get_all(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve gold queries: {str(e)}")


@router.get("/pending", response_model=List[GoldQuery])
async def get_pending_gold_queries() -> List[GoldQuery]:
    """
    Get gold queries that have no associated evaluations (pending evaluation).
    
    Returns:
        List[GoldQuery]: List of gold queries without evaluations
        
    Raises:
        HTTPException: 500 if database operation fails
    """
    try:
        repository = GoldQueryRepository()
        return repository.get_pending()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve pending gold queries: {str(e)}")


@router.get("/{gold_query_id}", response_model=GoldQuery)
async def get_gold_query_by_id(gold_query_id: UUID) -> GoldQuery:
    """
    Get a specific gold query by its ID.
    
    Args:
        gold_query_id: UUID of the gold query to retrieve
        
    Returns:
        GoldQuery: The requested gold query record
        
    Raises:
        HTTPException: 404 if gold query not found, 500 if database operation fails
    """
    try:
        repository = GoldQueryRepository()
        gold_query = repository.get_by_id(gold_query_id)
        
        if not gold_query:
            raise HTTPException(status_code=404, detail=f"Gold query with ID {gold_query_id} not found")
        
        return gold_query
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve gold query: {str(e)}")


@router.post("/", response_model=GoldQuery, status_code=201)
async def create_gold_query(gold_query_data: GoldQueryCreate) -> GoldQuery:
    """
    Create a new gold query record.
    
    Args:
        gold_query_data: Gold query data to create
        
    Returns:
        GoldQuery: The created gold query record
        
    Raises:
        HTTPException: 400 if validation fails, 500 if database operation fails
    """
    try:
        repository = GoldQueryRepository()
        return repository.create(gold_query_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create gold query: {str(e)}")