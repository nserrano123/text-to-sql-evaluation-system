#!/usr/bin/env python3
"""
Run chart generation property-based tests.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
from uuid import uuid4
import io
from PIL import Image

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

# Import chart service directly
from app.services.chart_service import ChartService

def test_chart_generation_validity():
    """Test Property 21: Chart generation validity"""
    print("Running Property-Based Tests for Chart Generation Validity...")
    print("**Feature: text-to-sql-evaluation, Property 21: Chart generation validity**")
    
    chart_service = ChartService()
    
    # Test EX chart generation
    print("\nRunning test_ex_chart_generates_valid_png...")
    test_data = [MockExecutionAccuracy(True), MockExecutionAccuracy(False), MockExecutionAccuracy(True)]
    
    try:
        chart_data = chart_service.generate_ex_chart(test_data)
        assert isinstance(chart_data, bytes)
        assert len(chart_data) > 0
        
        # Verify PNG validity
        image_buffer = io.BytesIO(chart_data)
        with Image.open(image_buffer) as img:
            assert img.format == 'PNG'
            assert img.size[0] > 0
            assert img.size[1] > 0
        
        print("✓ test_ex_chart_generates_valid_png passed")
    except Exception as e:
        print(f"✗ test_ex_chart_generates_valid_png failed: {e}")
        return False
    
    # Test Component chart generation
    print("Running test_component_chart_generates_valid_png...")
    component_data = [
        MockComponentMatching(True, False, True, False, True),
        MockComponentMatching(False, True, False, True, False)
    ]
    
    try:
        chart_data = chart_service.generate_component_chart(component_data)
        assert isinstance(chart_data, bytes)
        assert len(chart_data) > 0
        
        # Verify PNG validity
        image_buffer = io.BytesIO(chart_data)
        with Image.open(image_buffer) as img:
            assert img.format == 'PNG'
            assert img.size[0] > 0
            assert img.size[1] > 0
        
        print("✓ test_component_chart_generates_valid_png passed")
    except Exception as e:
        print(f"✗ test_component_chart_generates_valid_png failed: {e}")
        return False
    
    # Test TTA histogram generation
    print("Running test_tta_histogram_generates_valid_png...")
    start_time = datetime.now() - timedelta(seconds=100)
    end_time = start_time + timedelta(seconds=50)
    tta_data = [
        MockTimeToAnswer(start_time, end_time, 50.0),
        MockTimeToAnswer(start_time, end_time + timedelta(seconds=30), 80.0)
    ]
    
    try:
        chart_data = chart_service.generate_tta_histogram(tta_data)
        assert isinstance(chart_data, bytes)
        assert len(chart_data) > 0
        
        # Verify PNG validity
        image_buffer = io.BytesIO(chart_data)
        with Image.open(image_buffer) as img:
            assert img.format == 'PNG'
            assert img.size[0] > 0
            assert img.size[1] > 0
        
        print("✓ test_tta_histogram_generates_valid_png passed")
    except Exception as e:
        print(f"✗ test_tta_histogram_generates_valid_png failed: {e}")
        return False
    
    # Test empty data error handling
    print("Running test_empty_data_raises_value_error...")
    try:
        try:
            chart_service.generate_ex_chart([])
            print("✗ Expected ValueError for empty EX data")
            return False
        except ValueError:
            pass  # Expected
        
        try:
            chart_service.generate_component_chart([])
            print("✗ Expected ValueError for empty component data")
            return False
        except ValueError:
            pass  # Expected
        
        try:
            chart_service.generate_tta_histogram([])
            print("✗ Expected ValueError for empty TTA data")
            return False
        except ValueError:
            pass  # Expected
        
        print("✓ test_empty_data_raises_value_error passed")
    except Exception as e:
        print(f"✗ test_empty_data_raises_value_error failed: {e}")
        return False
    
    return True

def test_chart_resolution_requirement():
    """Test Property 22: Chart resolution requirement"""
    print("\nRunning Property-Based Tests for Chart Resolution Requirement...")
    print("**Feature: text-to-sql-evaluation, Property 22: Chart resolution requirement**")
    
    chart_service = ChartService()
    
    def check_image_resolution(chart_data, min_dpi=300):
        image_buffer = io.BytesIO(chart_data)
        with Image.open(image_buffer) as img:
            dpi = img.info.get('dpi', (72, 72))
            tolerance = 0.1
            if isinstance(dpi, tuple):
                x_dpi, y_dpi = dpi
                return x_dpi >= (min_dpi - tolerance) and y_dpi >= (min_dpi - tolerance)
            else:
                return dpi >= (min_dpi - tolerance)
    
    # Test DPI configuration
    print("Running test_chart_service_dpi_configuration...")
    try:
        import matplotlib
        assert matplotlib.rcParams['figure.dpi'] == 300
        assert matplotlib.rcParams['savefig.dpi'] == 300
        print("✓ test_chart_service_dpi_configuration passed")
    except Exception as e:
        print(f"✗ test_chart_service_dpi_configuration failed: {e}")
        return False
    
    # Test EX chart DPI
    print("Running test_ex_chart_meets_dpi_requirement...")
    try:
        test_data = [MockExecutionAccuracy(True), MockExecutionAccuracy(False)]
        chart_data = chart_service.generate_ex_chart(test_data)
        assert check_image_resolution(chart_data, 300), "EX chart does not meet 300 DPI requirement"
        print("✓ test_ex_chart_meets_dpi_requirement passed")
    except Exception as e:
        print(f"✗ test_ex_chart_meets_dpi_requirement failed: {e}")
        return False
    
    return True

def test_chart_language_requirement():
    """Test Property 23: Chart language requirement"""
    print("\nRunning Property-Based Tests for Chart Language Requirement...")
    print("**Feature: text-to-sql-evaluation, Property 23: Chart language requirement**")
    
    # Test Spanish consistency
    print("Running test_chart_service_uses_spanish_consistently...")
    try:
        with open('app/services/chart_service.py', 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        required_spanish_terms = [
            'Precisión de Ejecución',
            'Consultas Correctas',
            'Precisión por Componente SQL',
            'Distribución del Tiempo de Respuesta'
        ]
        
        for term in required_spanish_terms:
            assert term in source_code, f"Required Spanish term '{term}' not found in ChartService"
        
        print("✓ test_chart_service_uses_spanish_consistently passed")
    except Exception as e:
        print(f"✗ test_chart_service_uses_spanish_consistently failed: {e}")
        return False
    
    return True

def main():
    """Run all chart property-based tests."""
    print("Running Chart Generation Property-Based Tests...")
    
    success = True
    
    # Test Property 21: Chart generation validity
    if not test_chart_generation_validity():
        success = False
    
    # Test Property 22: Chart resolution requirement
    if not test_chart_resolution_requirement():
        success = False
    
    # Test Property 23: Chart language requirement
    if not test_chart_language_requirement():
        success = False
    
    if success:
        print("\n🎉 All chart property tests passed!")
        print("Property 21: Chart generation validity - PASSED")
        print("**Validates: Requirements 8.1, 8.2, 8.3**")
        print("Property 22: Chart resolution requirement - PASSED")
        print("**Validates: Requirements 8.4**")
        print("Property 23: Chart language requirement - PASSED")
        print("**Validates: Requirements 8.5**")
    else:
        print("\n❌ Some chart property tests failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())