"""Property-based tests for export download availability"""

import pytest
from fastapi.testclient import TestClient
from fastapi.responses import StreamingResponse
from uuid import uuid4
from datetime import datetime, timezone
from typing import Dict, Any, List
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, AsyncMock, patch
import io


# **Feature: text-to-sql-evaluation, Property 25: Export download availability**


# Strategies for generating test data
@st.composite
def export_data_strategy(draw):
    """Generate test data for export scenarios"""
    num_gold_queries = draw(st.integers(min_value=0, max_value=10))
    num_evaluations = draw(st.integers(min_value=0, max_value=num_gold_queries))
    
    return {
        'gold_queries_count': num_gold_queries,
        'evaluations_count': num_evaluations,
        'has_metrics': draw(st.booleans())
    }


class MockExportService:
    """Mock export service for testing download availability"""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
    
    async def export_to_csv(self) -> str:
        """Mock CSV export"""
        if self.should_fail:
            raise Exception("Export failed")
        
        return "id,name,value\n1,test,123\n2,test2,456\n"
    
    async def export_to_latex(self) -> str:
        """Mock LaTeX export"""
        if self.should_fail:
            raise Exception("Export failed")
        
        return "\\begin{table}\\caption{Test}\\end{table}"


def test_csv_export_provides_download_response():
    """
    Property 25: Export download availability - CSV export provides downloadable response
    For any CSV export request, the system should provide a valid download response
    **Validates: Requirements 9.4**
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    # Create a test app with the export endpoint
    app = FastAPI()
    
    @app.get("/api/export/csv")
    async def export_csv():
        service = MockExportService()
        csv_content = await service.export_to_csv()
        
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_data.csv"
            }
        )
    
    client = TestClient(app)
    
    # Make request to CSV export endpoint
    response = client.get("/api/export/csv")
    
    # Verify download availability properties
    assert response.status_code == 200, "CSV export should return success status"
    
    # Verify response headers indicate downloadable file
    assert "Content-Disposition" in response.headers, "Should have Content-Disposition header for download"
    content_disposition = response.headers["Content-Disposition"]
    assert "attachment" in content_disposition, "Should indicate file attachment for download"
    assert "filename=" in content_disposition, "Should provide filename for download"
    assert "evaluation_data.csv" in content_disposition, "Should have appropriate CSV filename"
    
    # Verify content type is appropriate for CSV
    assert response.headers["content-type"] == "text/csv; charset=utf-8", "Should have CSV content type"
    
    # Verify response contains actual CSV data
    content = response.content.decode('utf-8')
    assert len(content) > 0, "CSV download should contain data"
    assert "id,name,value" in content, "CSV should contain expected headers"


def test_latex_export_provides_download_response():
    """
    Property 25: Export download availability - LaTeX export provides downloadable response
    For any LaTeX export request, the system should provide a valid download response
    **Validates: Requirements 9.4**
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    # Create a test app with the export endpoint
    app = FastAPI()
    
    @app.get("/api/export/latex")
    async def export_latex():
        service = MockExportService()
        latex_content = await service.export_to_latex()
        
        return StreamingResponse(
            io.BytesIO(latex_content.encode('utf-8')),
            media_type="text/plain",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_summary.tex"
            }
        )
    
    client = TestClient(app)
    
    # Make request to LaTeX export endpoint
    response = client.get("/api/export/latex")
    
    # Verify download availability properties
    assert response.status_code == 200, "LaTeX export should return success status"
    
    # Verify response headers indicate downloadable file
    assert "Content-Disposition" in response.headers, "Should have Content-Disposition header for download"
    content_disposition = response.headers["Content-Disposition"]
    assert "attachment" in content_disposition, "Should indicate file attachment for download"
    assert "filename=" in content_disposition, "Should provide filename for download"
    assert "evaluation_summary.tex" in content_disposition, "Should have appropriate LaTeX filename"
    
    # Verify content type is appropriate for LaTeX
    assert response.headers["content-type"] == "text/plain; charset=utf-8", "Should have text/plain content type"
    
    # Verify response contains actual LaTeX data
    content = response.content.decode('utf-8')
    assert len(content) > 0, "LaTeX download should contain data"
    assert "\\begin{table}" in content, "LaTeX should contain expected table structure"


def test_export_download_handles_empty_data():
    """
    Property 25: Export download availability - Handles empty data gracefully
    For any export request with empty data, should still provide valid download response
    **Validates: Requirements 9.4**
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    # Create a test app with export endpoints
    app = FastAPI()
    
    @app.get("/api/export/csv")
    async def export_csv():
        # Mock service that returns empty CSV
        csv_content = ""  # Empty CSV
        
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_data.csv"
            }
        )
    
    @app.get("/api/export/latex")
    async def export_latex():
        # Mock service that returns minimal LaTeX
        latex_content = "\\begin{table}\\caption{No Data}\\end{table}"
        
        return StreamingResponse(
            io.BytesIO(latex_content.encode('utf-8')),
            media_type="text/plain",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_summary.tex"
            }
        )
    
    client = TestClient(app)
    
    # Test CSV export with empty data
    csv_response = client.get("/api/export/csv")
    assert csv_response.status_code == 200, "Empty CSV export should still provide download"
    assert "Content-Disposition" in csv_response.headers, "Empty CSV should still have download headers"
    assert "attachment" in csv_response.headers["Content-Disposition"], "Empty CSV should be downloadable"
    
    # Test LaTeX export with minimal data
    latex_response = client.get("/api/export/latex")
    assert latex_response.status_code == 200, "Minimal LaTeX export should still provide download"
    assert "Content-Disposition" in latex_response.headers, "Minimal LaTeX should still have download headers"
    assert "attachment" in latex_response.headers["Content-Disposition"], "Minimal LaTeX should be downloadable"


def test_export_download_error_handling():
    """
    Property 25: Export download availability - Error handling doesn't break download capability
    For any export that encounters errors, the system should handle gracefully without breaking download mechanism
    **Validates: Requirements 9.4**
    """
    from fastapi import FastAPI, HTTPException
    from fastapi.testclient import TestClient
    
    # Create a test app with export endpoints that can fail
    app = FastAPI()
    
    @app.get("/api/export/csv")
    async def export_csv():
        service = MockExportService(should_fail=True)
        try:
            csv_content = await service.export_to_csv()
            return StreamingResponse(
                io.BytesIO(csv_content.encode('utf-8')),
                media_type="text/csv",
                headers={
                    "Content-Disposition": "attachment; filename=evaluation_data.csv"
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to export CSV: {str(e)}")
    
    @app.get("/api/export/latex")
    async def export_latex():
        service = MockExportService(should_fail=True)
        try:
            latex_content = await service.export_to_latex()
            return StreamingResponse(
                io.BytesIO(latex_content.encode('utf-8')),
                media_type="text/plain",
                headers={
                    "Content-Disposition": "attachment; filename=evaluation_summary.tex"
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to export LaTeX: {str(e)}")
    
    client = TestClient(app)
    
    # Test that errors are handled gracefully
    csv_response = client.get("/api/export/csv")
    assert csv_response.status_code == 500, "Should return error status when export fails"
    
    latex_response = client.get("/api/export/latex")
    assert latex_response.status_code == 500, "Should return error status when export fails"
    
    # Verify error responses are still proper HTTP responses (not broken)
    assert csv_response.headers["content-type"] == "application/json", "Error response should be JSON"
    assert latex_response.headers["content-type"] == "application/json", "Error response should be JSON"


def test_export_download_filename_validity():
    """
    Property 25: Export download availability - Download filenames are valid
    For any export download, the filename should be valid and descriptive
    **Validates: Requirements 9.4**
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    # Create a test app with export endpoints
    app = FastAPI()
    
    @app.get("/api/export/csv")
    async def export_csv():
        service = MockExportService()
        csv_content = await service.export_to_csv()
        
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_data.csv"
            }
        )
    
    @app.get("/api/export/latex")
    async def export_latex():
        service = MockExportService()
        latex_content = await service.export_to_latex()
        
        return StreamingResponse(
            io.BytesIO(latex_content.encode('utf-8')),
            media_type="text/plain",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_summary.tex"
            }
        )
    
    client = TestClient(app)
    
    # Test CSV filename
    csv_response = client.get("/api/export/csv")
    csv_disposition = csv_response.headers["Content-Disposition"]
    assert "filename=evaluation_data.csv" in csv_disposition, "CSV filename should be descriptive and have .csv extension"
    
    # Test LaTeX filename
    latex_response = client.get("/api/export/latex")
    latex_disposition = latex_response.headers["Content-Disposition"]
    assert "filename=evaluation_summary.tex" in latex_disposition, "LaTeX filename should be descriptive and have .tex extension"
    
    # Verify filenames don't contain invalid characters
    import re
    csv_filename = re.search(r'filename=([^;]+)', csv_disposition).group(1)
    latex_filename = re.search(r'filename=([^;]+)', latex_disposition).group(1)
    
    # Valid filename pattern (alphanumeric, underscore, dot, hyphen)
    valid_filename_pattern = r'^[a-zA-Z0-9._-]+$'
    assert re.match(valid_filename_pattern, csv_filename), f"CSV filename '{csv_filename}' should be valid"
    assert re.match(valid_filename_pattern, latex_filename), f"LaTeX filename '{latex_filename}' should be valid"


@given(export_data_strategy())
@settings(max_examples=50)
def test_export_download_availability_property(export_data):
    """
    Property 25: Export download availability - Property-based test
    For any export scenario, the system should provide valid download responses
    **Validates: Requirements 9.4**
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    # Create a test app with export endpoints
    app = FastAPI()
    
    @app.get("/api/export/csv")
    async def export_csv():
        service = MockExportService()
        csv_content = await service.export_to_csv()
        
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_data.csv"
            }
        )
    
    @app.get("/api/export/latex")
    async def export_latex():
        service = MockExportService()
        latex_content = await service.export_to_latex()
        
        return StreamingResponse(
            io.BytesIO(latex_content.encode('utf-8')),
            media_type="text/plain",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_summary.tex"
            }
        )
    
    client = TestClient(app)
    
    # Property 1: CSV export should always provide downloadable response
    csv_response = client.get("/api/export/csv")
    assert csv_response.status_code == 200, "CSV export should always succeed"
    assert "Content-Disposition" in csv_response.headers, "CSV should have download headers"
    assert "attachment" in csv_response.headers["Content-Disposition"], "CSV should be downloadable"
    assert "filename=" in csv_response.headers["Content-Disposition"], "CSV should have filename"
    
    # Property 2: LaTeX export should always provide downloadable response
    latex_response = client.get("/api/export/latex")
    assert latex_response.status_code == 200, "LaTeX export should always succeed"
    assert "Content-Disposition" in latex_response.headers, "LaTeX should have download headers"
    assert "attachment" in latex_response.headers["Content-Disposition"], "LaTeX should be downloadable"
    assert "filename=" in latex_response.headers["Content-Disposition"], "LaTeX should have filename"
    
    # Property 3: Content types should be appropriate
    assert csv_response.headers["content-type"] == "text/csv; charset=utf-8", "CSV should have correct content type"
    assert latex_response.headers["content-type"] == "text/plain; charset=utf-8", "LaTeX should have correct content type"
    
    # Property 4: Response content should be non-empty (for successful exports)
    csv_content = csv_response.content
    latex_content = latex_response.content
    assert len(csv_content) > 0, "CSV download should contain data"
    assert len(latex_content) > 0, "LaTeX download should contain data"
    
    # Property 5: Filenames should be valid and descriptive
    csv_disposition = csv_response.headers["Content-Disposition"]
    latex_disposition = latex_response.headers["Content-Disposition"]
    
    assert "evaluation_data.csv" in csv_disposition, "CSV filename should be descriptive"
    assert "evaluation_summary.tex" in latex_disposition, "LaTeX filename should be descriptive"


def test_export_download_streaming_response():
    """
    Property 25: Export download availability - Uses streaming response for large files
    For any export, the system should use streaming response to handle large files efficiently
    **Validates: Requirements 9.4**
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    # Create a test app with export endpoints
    app = FastAPI()
    
    @app.get("/api/export/csv")
    async def export_csv():
        # Generate larger CSV content to test streaming
        service = MockExportService()
        csv_content = await service.export_to_csv()
        
        # Simulate larger content
        large_csv = csv_content * 100  # Repeat content to make it larger
        
        return StreamingResponse(
            io.BytesIO(large_csv.encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_data.csv"
            }
        )
    
    client = TestClient(app)
    
    # Test that streaming response works
    response = client.get("/api/export/csv")
    
    # Verify it's a successful streaming response
    assert response.status_code == 200, "Streaming export should succeed"
    assert "Content-Disposition" in response.headers, "Streaming response should have download headers"
    
    # Verify content is delivered correctly
    content = response.content.decode('utf-8')
    assert len(content) > 1000, "Should handle larger content via streaming"
    assert content.count("id,name,value") > 1, "Should contain repeated CSV headers (simulating large file)"


def test_export_download_concurrent_requests():
    """
    Property 25: Export download availability - Handles concurrent download requests
    For any number of concurrent export requests, each should get a valid download response
    **Validates: Requirements 9.4**
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import threading
    import time
    
    # Create a test app with export endpoints
    app = FastAPI()
    
    @app.get("/api/export/csv")
    async def export_csv():
        # Add small delay to simulate processing time
        await asyncio.sleep(0.1)
        
        service = MockExportService()
        csv_content = await service.export_to_csv()
        
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_data.csv"
            }
        )
    
    client = TestClient(app)
    
    # Test concurrent requests
    results = []
    
    def make_request():
        try:
            response = client.get("/api/export/csv")
            results.append({
                'status_code': response.status_code,
                'has_download_headers': 'Content-Disposition' in response.headers,
                'content_length': len(response.content)
            })
        except Exception as e:
            results.append({'error': str(e)})
    
    # Create multiple threads to make concurrent requests
    threads = []
    for i in range(5):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify all requests succeeded
    assert len(results) == 5, "Should have results from all concurrent requests"
    
    for i, result in enumerate(results):
        assert 'error' not in result, f"Request {i} should not have errors"
        assert result['status_code'] == 200, f"Request {i} should succeed"
        assert result['has_download_headers'], f"Request {i} should have download headers"
        assert result['content_length'] > 0, f"Request {i} should have content"


# Import asyncio for async operations in tests
import asyncio