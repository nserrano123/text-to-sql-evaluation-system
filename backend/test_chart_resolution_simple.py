#!/usr/bin/env python3
"""
Simple test for chart resolution requirement without complex dependencies.
"""

import sys
import os
import io
from PIL import Image
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

def check_image_resolution(chart_data, min_dpi=300):
    """Check if image meets DPI requirements."""
    image_buffer = io.BytesIO(chart_data)
    with Image.open(image_buffer) as img:
        dpi = img.info.get('dpi', (72, 72))
        tolerance = 0.1
        if isinstance(dpi, tuple):
            x_dpi, y_dpi = dpi
            return x_dpi >= (min_dpi - tolerance) and y_dpi >= (min_dpi - tolerance)
        else:
            return dpi >= (min_dpi - tolerance)

def test_chart_resolution_requirement():
    """
    **Feature: text-to-sql-evaluation, Property 22: Chart resolution requirement**
    Test that generated charts meet the 300 DPI resolution requirement.
    """
    print("Testing Property 22: Chart resolution requirement")
    print("**Feature: text-to-sql-evaluation, Property 22: Chart resolution requirement**")
    
    # Import chart service directly
    from app.services.chart_service import ChartService
    
    chart_service = ChartService()
    
    # Test 1: Check matplotlib configuration
    print("\n1. Testing matplotlib DPI configuration...")
    import matplotlib
    
    figure_dpi = matplotlib.rcParams['figure.dpi']
    savefig_dpi = matplotlib.rcParams['savefig.dpi']
    
    print(f"   figure.dpi: {figure_dpi}")
    print(f"   savefig.dpi: {savefig_dpi}")
    
    assert figure_dpi == 300, f"Expected figure.dpi=300, got {figure_dpi}"
    assert savefig_dpi == 300, f"Expected savefig.dpi=300, got {savefig_dpi}"
    print("   ✓ Matplotlib DPI configuration correct")
    
    # Test 2: EX chart DPI
    print("\n2. Testing EX chart DPI...")
    test_data = [
        MockExecutionAccuracy(True),
        MockExecutionAccuracy(False),
        MockExecutionAccuracy(True)
    ]
    
    chart_data = chart_service.generate_ex_chart(test_data)
    assert isinstance(chart_data, bytes), "Chart data should be bytes"
    assert len(chart_data) > 0, "Chart data should not be empty"
    
    # Check DPI
    meets_dpi = check_image_resolution(chart_data, 300)
    print(f"   Chart data size: {len(chart_data)} bytes")
    
    # Get actual DPI for debugging
    image_buffer = io.BytesIO(chart_data)
    with Image.open(image_buffer) as img:
        actual_dpi = img.info.get('dpi', (72, 72))
        print(f"   Actual DPI: {actual_dpi}")
    
    assert meets_dpi, "EX chart does not meet 300 DPI requirement"
    print("   ✓ EX chart meets 300 DPI requirement")
    
    # Test 3: Component chart DPI
    print("\n3. Testing Component chart DPI...")
    component_data = [
        MockComponentMatching(True, False, True, False, True),
        MockComponentMatching(False, True, False, True, False)
    ]
    
    chart_data = chart_service.generate_component_chart(component_data)
    assert isinstance(chart_data, bytes), "Chart data should be bytes"
    assert len(chart_data) > 0, "Chart data should not be empty"
    
    meets_dpi = check_image_resolution(chart_data, 300)
    print(f"   Chart data size: {len(chart_data)} bytes")
    
    # Get actual DPI for debugging
    image_buffer = io.BytesIO(chart_data)
    with Image.open(image_buffer) as img:
        actual_dpi = img.info.get('dpi', (72, 72))
        print(f"   Actual DPI: {actual_dpi}")
    
    assert meets_dpi, "Component chart does not meet 300 DPI requirement"
    print("   ✓ Component chart meets 300 DPI requirement")
    
    # Test 4: TTA histogram DPI
    print("\n4. Testing TTA histogram DPI...")
    start_time = datetime.now() - timedelta(seconds=100)
    end_time = start_time + timedelta(seconds=50)
    tta_data = [
        MockTimeToAnswer(start_time, end_time, 50.0),
        MockTimeToAnswer(start_time, end_time + timedelta(seconds=30), 80.0)
    ]
    
    chart_data = chart_service.generate_tta_histogram(tta_data)
    assert isinstance(chart_data, bytes), "Chart data should be bytes"
    assert len(chart_data) > 0, "Chart data should not be empty"
    
    meets_dpi = check_image_resolution(chart_data, 300)
    print(f"   Chart data size: {len(chart_data)} bytes")
    
    # Get actual DPI for debugging
    image_buffer = io.BytesIO(chart_data)
    with Image.open(image_buffer) as img:
        actual_dpi = img.info.get('dpi', (72, 72))
        print(f"   Actual DPI: {actual_dpi}")
    
    assert meets_dpi, "TTA histogram does not meet 300 DPI requirement"
    print("   ✓ TTA histogram meets 300 DPI requirement")
    
    return True

def main():
    """Run the chart resolution test."""
    try:
        success = test_chart_resolution_requirement()
        if success:
            print("\n🎉 Property 22: Chart resolution requirement - PASSED")
            print("**Validates: Requirements 8.4**")
            return 0
        else:
            print("\n❌ Property 22: Chart resolution requirement - FAILED")
            return 1
    except Exception as e:
        print(f"\n❌ Property 22: Chart resolution requirement - FAILED")
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())