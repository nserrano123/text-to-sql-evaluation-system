"""API endpoints for chart generation operations"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import io
from typing import Dict, Any

from ..repositories.execution_accuracy_repository import ExecutionAccuracyRepository
from ..repositories.component_matching_repository import ComponentMatchingRepository
from ..repositories.time_to_answer_repository import TimeToAnswerRepository
from ..services.chart_service import ChartService

router = APIRouter(prefix="/api/charts", tags=["charts"])


@router.post("/execution-accuracy")
async def generate_execution_accuracy_chart() -> StreamingResponse:
    """
    Generate and return a PNG chart showing Execution Accuracy (EX) percentage.
    
    Returns:
        StreamingResponse: PNG image with 300 DPI resolution and Spanish labels
        
    Raises:
        HTTPException: 422 if no data available, 500 if generation fails
    """
    try:
        # Get execution accuracy data
        repository = ExecutionAccuracyRepository()
        records = repository.get_all()
        
        if not records:
            raise HTTPException(
                status_code=422, 
                detail="No execution accuracy data available for chart generation"
            )
        
        # Generate chart
        chart_service = ChartService()
        chart_data = chart_service.generate_ex_chart(records)
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(chart_data),
            media_type="image/png",
            headers={
                "Content-Disposition": "attachment; filename=execution_accuracy_chart.png",
                "Content-Length": str(len(chart_data))
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate execution accuracy chart: {str(e)}"
        )


@router.post("/component-matching")
async def generate_component_matching_chart() -> StreamingResponse:
    """
    Generate and return a PNG chart comparing F1 scores for each SQL component.
    
    Returns:
        StreamingResponse: PNG image with 300 DPI resolution and Spanish labels
        
    Raises:
        HTTPException: 422 if no data available, 500 if generation fails
    """
    try:
        # Get component matching data
        repository = ComponentMatchingRepository()
        records = repository.get_all()
        
        if not records:
            raise HTTPException(
                status_code=422, 
                detail="No component matching data available for chart generation"
            )
        
        # Generate chart
        chart_service = ChartService()
        chart_data = chart_service.generate_component_chart(records)
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(chart_data),
            media_type="image/png",
            headers={
                "Content-Disposition": "attachment; filename=component_matching_chart.png",
                "Content-Length": str(len(chart_data))
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate component matching chart: {str(e)}"
        )


@router.post("/time-distribution")
async def generate_time_distribution_chart() -> StreamingResponse:
    """
    Generate and return a PNG histogram showing Time-to-Answer (TTA) distribution.
    
    Returns:
        StreamingResponse: PNG image with 300 DPI resolution and Spanish labels
        
    Raises:
        HTTPException: 422 if no data available, 500 if generation fails
    """
    try:
        # Get time to answer data
        repository = TimeToAnswerRepository()
        records = repository.get_all()
        
        if not records:
            raise HTTPException(
                status_code=422, 
                detail="No time to answer data available for chart generation"
            )
        
        # Generate chart
        chart_service = ChartService()
        chart_data = chart_service.generate_tta_histogram(records)
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(chart_data),
            media_type="image/png",
            headers={
                "Content-Disposition": "attachment; filename=time_distribution_chart.png",
                "Content-Length": str(len(chart_data))
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate time distribution chart: {str(e)}"
        )


@router.get("/execution-accuracy/base64")
async def get_execution_accuracy_chart_base64() -> Dict[str, Any]:
    """
    Generate and return Execution Accuracy chart as base64 string for web display.
    
    Returns:
        Dict[str, Any]: Dictionary containing base64 encoded image and metadata
        
    Raises:
        HTTPException: 422 if no data available, 500 if generation fails
    """
    try:
        # Get execution accuracy data
        repository = ExecutionAccuracyRepository()
        records = repository.get_all()
        
        if not records:
            raise HTTPException(
                status_code=422, 
                detail="No execution accuracy data available for chart generation"
            )
        
        # Generate chart
        chart_service = ChartService()
        chart_data = chart_service.generate_ex_chart(records)
        base64_data = chart_service.chart_to_base64(chart_data)
        
        # Calculate EX percentage for metadata
        correct_count = sum(1 for record in records if record.is_correct)
        total_count = len(records)
        ex_percentage = (correct_count / total_count) * 100
        
        return {
            "image_data": base64_data,
            "content_type": "image/png",
            "filename": "execution_accuracy_chart.png",
            "metadata": {
                "execution_accuracy": round(ex_percentage, 2),
                "total_evaluations": total_count,
                "correct_evaluations": correct_count
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate execution accuracy chart: {str(e)}"
        )


@router.get("/component-matching/base64")
async def get_component_matching_chart_base64() -> Dict[str, Any]:
    """
    Generate and return Component Matching chart as base64 string for web display.
    
    Returns:
        Dict[str, Any]: Dictionary containing base64 encoded image and metadata
        
    Raises:
        HTTPException: 422 if no data available, 500 if generation fails
    """
    try:
        # Get component matching data
        repository = ComponentMatchingRepository()
        records = repository.get_all()
        
        if not records:
            raise HTTPException(
                status_code=422, 
                detail="No component matching data available for chart generation"
            )
        
        # Generate chart
        chart_service = ChartService()
        chart_data = chart_service.generate_component_chart(records)
        base64_data = chart_service.chart_to_base64(chart_data)
        
        # Calculate component scores for metadata
        components = {
            'SELECT': [],
            'WHERE': [],
            'GROUP BY': [],
            'ORDER BY': [],
            'KEYWORDS': []
        }
        
        for record in records:
            components['SELECT'].append(record.select_correct)
            components['WHERE'].append(record.where_correct)
            components['GROUP BY'].append(record.group_by_correct)
            components['ORDER BY'].append(record.order_by_correct)
            components['KEYWORDS'].append(record.keywords_correct)
        
        component_scores = {}
        for component, values in components.items():
            if values:
                accuracy = (sum(values) / len(values)) * 100
                component_scores[component] = round(accuracy, 2)
            else:
                component_scores[component] = 0.0
        
        return {
            "image_data": base64_data,
            "content_type": "image/png",
            "filename": "component_matching_chart.png",
            "metadata": {
                "component_scores": component_scores,
                "total_evaluations": len(records)
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate component matching chart: {str(e)}"
        )


@router.get("/time-distribution/base64")
async def get_time_distribution_chart_base64() -> Dict[str, Any]:
    """
    Generate and return Time Distribution chart as base64 string for web display.
    
    Returns:
        Dict[str, Any]: Dictionary containing base64 encoded image and metadata
        
    Raises:
        HTTPException: 422 if no data available, 500 if generation fails
    """
    try:
        # Get time to answer data
        repository = TimeToAnswerRepository()
        records = repository.get_all()
        
        if not records:
            raise HTTPException(
                status_code=422, 
                detail="No time to answer data available for chart generation"
            )
        
        # Generate chart
        chart_service = ChartService()
        chart_data = chart_service.generate_tta_histogram(records)
        base64_data = chart_service.chart_to_base64(chart_data)
        
        # Calculate statistics for metadata
        durations = [record.duration_seconds for record in records]
        mean_tta = sum(durations) / len(durations)
        median_tta = sorted(durations)[len(durations) // 2]
        
        return {
            "image_data": base64_data,
            "content_type": "image/png",
            "filename": "time_distribution_chart.png",
            "metadata": {
                "mean_tta": round(mean_tta, 2),
                "median_tta": round(median_tta, 2),
                "min_tta": round(min(durations), 2),
                "max_tta": round(max(durations), 2),
                "total_evaluations": len(records)
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate time distribution chart: {str(e)}"
        )