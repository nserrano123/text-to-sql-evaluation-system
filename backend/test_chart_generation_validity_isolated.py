#!/usr/bin/env python3
"""
Isolated test for chart generation validity (Property 21).

**Feature: text-to-sql-evaluation, Property 21: Chart generation validity**
**Validates: Requirements 8.1, 8.2, 8.3**
"""

import sys
import os
import io
from datetime import datetime, timedelta
from uuid import uuid4

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock models to avoid database dependencies
class MockExecutionAccuracy:
    def __init__(self, is_correct, results_match=None, evaluator_notes=None):
        self.id = uuid4()
        self.evaluation_id = uuid4()
        self.results_match = results_match
        self.is_correct = is_correct
        self.evaluator_notes = evaluator_notes
        self.created_at = datetime.now()

class MockComponentMatching:
    def __init__(self, select_correct, where_correct, group_by_correct, 
                 order_by_correct, keywords_correct, f1_score=None, evaluator_notes=None):
        self.id = uuid4()
        self.evaluation_id = uuid4()
        self.select_correct = select_correct
        self.where_correct = where_correct
        self.group_by_correct = group_by_correct
        self.order_by_correct = order_by_correct
        self.keywords_correct = keywords_correct
        self.f1_score = f1_score
        self.evaluator_notes = evaluator_notes
        self.created_at = datetime.now()

class MockTimeToAnswer:
    def __init__(self, start_time, end_time, duration_seconds):
        self.id = uuid4()
        self.evaluation_id = uuid4()
        self.start_time = start_time
        self.end_time = end_time
        self.duration_seconds = duration_seconds
        self.created_at = datetime.now()

def test_chart_generation_validity():
    """
    Test Property 21: Chart generation validity
    
    For any request to generate charts (EX bar chart, component F1 bar chart, TTA histogram), 
    a valid PNG file should be generated.
    """
    print("Testing Property 21: Chart generation validity")
    print("**Feature: text-to-sql-evaluation, Property 21: Chart generation validity**")
    print("**Validates: Requirements 8.1, 8.2, 8.3**")
    
    # Import chart service directly without database dependencies
    try:
        # Temporarily mock the database connection to avoid import errors
        import app.database
        app.database.get_supabase_client = lambda: None
        
        from app.services.chart_service import ChartService
    except Exception as e:
        print(f"Failed to import ChartService: {e}")
        return False
    
    chart_service = ChartService()
    
    # Test 1: EX chart generation (Requirement 8.1)
    print("\n1. Testing EX chart generation...")
    try:
        # Create test data with various scenarios
        test_cases = [
            # Case 1: Mixed results
            [MockExecutionAccuracy(True), MockExecutionAccuracy(False), MockExecutionAccuracy(True)],
            # Case 2: All correct
            [MockExecutionAccuracy(True), MockExecutionAccuracy(True)],
            # Case 3: All incorrect
            [MockExecutionAccuracy(False), MockExecutionAccuracy(False)],
            # Case 4: Single evaluation
            [MockExecutionAccuracy(True)]
        ]
        
        for i, test_data in enumerate(test_cases, 1):
            chart_data = chart_service.generate_ex_chart(test_data)
            
            # Verify it's valid PNG data
            assert isinstance(chart_data, bytes), f"Case {i}: Chart data should be bytes"
            assert len(chart_data) > 0, f"Case {i}: Chart data should not be empty"
            
            # Verify it can be opened as a valid image
            try:
                from PIL import Image
                image_buffer = io.BytesIO(chart_data)
                with Image.open(image_buffer) as img:
                    assert img.format == 'PNG', f"Case {i}: Should be PNG format"
                    assert img.size[0] > 0, f"Case {i}: Width should be > 0"
                    assert img.size[1] > 0, f"Case {i}: Height should be > 0"
            except ImportError:
                # If PIL is not available, just check that we have PNG header
                assert chart_data.startswith(b'\x89PNG'), f"Case {i}: Should have PNG header"
            
            print(f"   ✓ Case {i}: EX chart generated successfully")
        
        print("   ✓ EX chart generation test passed")
    except Exception as e:
        print(f"   ✗ EX chart generation test failed: {e}")
        return False
    
    # Test 2: Component chart generation (Requirement 8.2)
    print("\n2. Testing Component chart generation...")
    try:
        test_cases = [
            # Case 1: Mixed component results
            [
                MockComponentMatching(True, False, True, False, True),
                MockComponentMatching(False, True, False, True, False),
                MockComponentMatching(True, True, True, True, True)
            ],
            # Case 2: All components correct
            [MockComponentMatching(True, True, True, True, True)],
            # Case 3: All components incorrect
            [MockComponentMatching(False, False, False, False, False)],
            # Case 4: Single evaluation
            [MockComponentMatching(True, False, True, False, True)]
        ]
        
        for i, test_data in enumerate(test_cases, 1):
            chart_data = chart_service.generate_component_chart(test_data)
            
            # Verify it's valid PNG data
            assert isinstance(chart_data, bytes), f"Case {i}: Chart data should be bytes"
            assert len(chart_data) > 0, f"Case {i}: Chart data should not be empty"
            
            # Verify PNG format
            try:
                from PIL import Image
                image_buffer = io.BytesIO(chart_data)
                with Image.open(image_buffer) as img:
                    assert img.format == 'PNG', f"Case {i}: Should be PNG format"
                    assert img.size[0] > 0, f"Case {i}: Width should be > 0"
                    assert img.size[1] > 0, f"Case {i}: Height should be > 0"
            except ImportError:
                assert chart_data.startswith(b'\x89PNG'), f"Case {i}: Should have PNG header"
            
            print(f"   ✓ Case {i}: Component chart generated successfully")
        
        print("   ✓ Component chart generation test passed")
    except Exception as e:
        print(f"   ✗ Component chart generation test failed: {e}")
        return False
    
    # Test 3: TTA histogram generation (Requirement 8.3)
    print("\n3. Testing TTA histogram generation...")
    try:
        base_time = datetime.now() - timedelta(seconds=1000)
        test_cases = [
            # Case 1: Various durations
            [
                MockTimeToAnswer(base_time, base_time + timedelta(seconds=50), 50.0),
                MockTimeToAnswer(base_time, base_time + timedelta(seconds=80), 80.0),
                MockTimeToAnswer(base_time, base_time + timedelta(seconds=120), 120.0)
            ],
            # Case 2: Short durations
            [
                MockTimeToAnswer(base_time, base_time + timedelta(seconds=5), 5.0),
                MockTimeToAnswer(base_time, base_time + timedelta(seconds=10), 10.0)
            ],
            # Case 3: Long durations
            [
                MockTimeToAnswer(base_time, base_time + timedelta(seconds=300), 300.0),
                MockTimeToAnswer(base_time, base_time + timedelta(seconds=600), 600.0)
            ],
            # Case 4: Single evaluation
            [MockTimeToAnswer(base_time, base_time + timedelta(seconds=45), 45.0)]
        ]
        
        for i, test_data in enumerate(test_cases, 1):
            chart_data = chart_service.generate_tta_histogram(test_data)
            
            # Verify it's valid PNG data
            assert isinstance(chart_data, bytes), f"Case {i}: Chart data should be bytes"
            assert len(chart_data) > 0, f"Case {i}: Chart data should not be empty"
            
            # Verify PNG format
            try:
                from PIL import Image
                image_buffer = io.BytesIO(chart_data)
                with Image.open(image_buffer) as img:
                    assert img.format == 'PNG', f"Case {i}: Should be PNG format"
                    assert img.size[0] > 0, f"Case {i}: Width should be > 0"
                    assert img.size[1] > 0, f"Case {i}: Height should be > 0"
            except ImportError:
                assert chart_data.startswith(b'\x89PNG'), f"Case {i}: Should have PNG header"
            
            print(f"   ✓ Case {i}: TTA histogram generated successfully")
        
        print("   ✓ TTA histogram generation test passed")
    except Exception as e:
        print(f"   ✗ TTA histogram generation test failed: {e}")
        return False
    
    # Test 4: Error handling for empty data
    print("\n4. Testing error handling for empty data...")
    try:
        # Test empty EX data
        try:
            chart_service.generate_ex_chart([])
            print("   ✗ Expected ValueError for empty EX data")
            return False
        except ValueError as e:
            assert "No execution accuracy data available" in str(e)
            print("   ✓ Empty EX data raises appropriate ValueError")
        
        # Test empty component data
        try:
            chart_service.generate_component_chart([])
            print("   ✗ Expected ValueError for empty component data")
            return False
        except ValueError as e:
            assert "No component matching data available" in str(e)
            print("   ✓ Empty component data raises appropriate ValueError")
        
        # Test empty TTA data
        try:
            chart_service.generate_tta_histogram([])
            print("   ✗ Expected ValueError for empty TTA data")
            return False
        except ValueError as e:
            assert "No time to answer data available" in str(e)
            print("   ✓ Empty TTA data raises appropriate ValueError")
        
        print("   ✓ Error handling test passed")
    except Exception as e:
        print(f"   ✗ Error handling test failed: {e}")
        return False
    
    return True

def main():
    """Run the chart generation validity test."""
    print("Running Chart Generation Validity Property Test...")
    print("=" * 60)
    
    success = test_chart_generation_validity()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Property 21: Chart generation validity - PASSED")
        print("**Validates: Requirements 8.1, 8.2, 8.3**")
        print("\nAll chart types (EX, Component, TTA) generate valid PNG files.")
    else:
        print("❌ Property 21: Chart generation validity - FAILED")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())