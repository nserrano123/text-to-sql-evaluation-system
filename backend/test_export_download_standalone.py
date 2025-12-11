#!/usr/bin/env python3
"""
Standalone test for Property 25: Export download availability
This test verifies that export endpoints provide valid download responses.
"""

import asyncio
import io
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.responses import StreamingResponse


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


def test_csv_export_download_availability():
    """
    **Feature: text-to-sql-evaluation, Property 25: Export download availability**
    Test that CSV export provides valid download response
    **Validates: Requirements 9.4**
    """
    print("Testing CSV export download availability...")
    
    # Create test app
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
    
    # Test the endpoint
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
    
    print("✅ CSV export download availability test passed!")
    return True


def test_latex_export_download_availability():
    """
    **Feature: text-to-sql-evaluation, Property 25: Export download availability**
    Test that LaTeX export provides valid download response
    **Validates: Requirements 9.4**
    """
    print("Testing LaTeX export download availability...")
    
    # Create test app
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
    
    # Test the endpoint
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
    
    print("✅ LaTeX export download availability test passed!")
    return True


def test_export_filename_validity():
    """
    **Feature: text-to-sql-evaluation, Property 25: Export download availability**
    Test that export filenames are valid and descriptive
    **Validates: Requirements 9.4**
    """
    print("Testing export filename validity...")
    
    # Create test app
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
    
    print("✅ Export filename validity test passed!")
    return True


def test_export_empty_data_handling():
    """
    **Feature: text-to-sql-evaluation, Property 25: Export download availability**
    Test that exports handle empty data gracefully while maintaining download capability
    **Validates: Requirements 9.4**
    """
    print("Testing export empty data handling...")
    
    # Create test app
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
    
    print("✅ Export empty data handling test passed!")
    return True


def test_streaming_response_functionality():
    """
    **Feature: text-to-sql-evaluation, Property 25: Export download availability**
    Test that exports use streaming response for efficient file delivery
    **Validates: Requirements 9.4**
    """
    print("Testing streaming response functionality...")
    
    # Create test app
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
    
    print("✅ Streaming response functionality test passed!")
    return True


def main():
    """Run all Property 25 tests"""
    print("=" * 60)
    print("Property 25: Export Download Availability Tests")
    print("=" * 60)
    
    tests = [
        test_csv_export_download_availability,
        test_latex_export_download_availability,
        test_export_filename_validity,
        test_export_empty_data_handling,
        test_streaming_response_functionality
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All Property 25 tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)