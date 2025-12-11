"""API endpoints for data export operations"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import Dict, Any
from io import StringIO, BytesIO

from ..services.export_service import ExportService

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/csv")
async def export_csv() -> StreamingResponse:
    """
    Export all evaluation data to CSV format.
    
    Returns:
        StreamingResponse: CSV file download response
        
    Raises:
        HTTPException: 500 if export fails
    """
    try:
        service = ExportService()
        csv_content = await service.export_to_csv()
        
        # Create a BytesIO buffer for the CSV content
        csv_buffer = BytesIO()
        csv_buffer.write(csv_content.encode('utf-8'))
        csv_buffer.seek(0)
        
        # Return as streaming response with appropriate headers
        return StreamingResponse(
            BytesIO(csv_content.encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_data.csv"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to export CSV: {str(e)}"
        )


@router.get("/latex")
async def export_latex() -> StreamingResponse:
    """
    Export summary metrics to LaTeX table format.
    
    Returns:
        StreamingResponse: LaTeX file download response
        
    Raises:
        HTTPException: 500 if export fails
    """
    try:
        service = ExportService()
        latex_content = await service.export_to_latex()
        
        # Return as streaming response with appropriate headers
        return StreamingResponse(
            BytesIO(latex_content.encode('utf-8')),
            media_type="text/plain",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_summary.tex"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to export LaTeX: {str(e)}"
        )


@router.get("/csv/preview")
async def preview_csv() -> Dict[str, Any]:
    """
    Preview the CSV export data (first 10 rows) without downloading.
    
    Returns:
        Dict[str, Any]: Preview data with row count and sample rows
        
    Raises:
        HTTPException: 500 if preview generation fails
    """
    try:
        service = ExportService()
        csv_content = await service.export_to_csv()
        
        # Parse CSV content to get preview
        import pandas as pd
        df = pd.read_csv(StringIO(csv_content))
        
        # Get preview data
        preview_data = {
            "total_rows": len(df),
            "columns": list(df.columns),
            "sample_rows": df.head(10).to_dict('records')
        }
        
        return preview_data
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate CSV preview: {str(e)}"
        )


@router.get("/latex/preview")
async def preview_latex() -> Dict[str, str]:
    """
    Preview the LaTeX export content without downloading.
    
    Returns:
        Dict[str, str]: LaTeX content as string
        
    Raises:
        HTTPException: 500 if preview generation fails
    """
    try:
        service = ExportService()
        latex_content = await service.export_to_latex()
        
        return {"latex_content": latex_content}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate LaTeX preview: {str(e)}"
        )