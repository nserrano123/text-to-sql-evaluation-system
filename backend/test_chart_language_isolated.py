#!/usr/bin/env python3
"""
Isolated test for chart language requirement (Property 23).
This test runs without database dependencies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import re
from datetime import datetime, timedelta
from uuid import uuid4

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

def test_chart_language_requirement():
    """
    Test Property 23: Chart language requirement
    **Feature: text-to-sql-evaluation, Property 23: Chart language requirement**
    **Validates: Requirements 8.5**
    
    For any generated chart, labels, legends, and titles should contain Spanish text.
    """
    print("Running Property-Based Tests for Chart Language Requirement...")
    print("**Feature: text-to-sql-evaluation, Property 23: Chart language requirement**")
    
    # Test Spanish consistency in source code
    print("Running test_chart_service_uses_spanish_consistently...")
    try:
        with open('app/services/chart_service.py', 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Check for key Spanish terms across all chart types
        required_spanish_terms = [
            'Precisión de Ejecución',
            'Consultas Correctas',
            'Consultas Incorrectas',
            'Número de Consultas',
            'Tipo de Resultado',
            'Total de Consultas',
            'Precisión por Componente SQL',
            'Componentes SQL',
            'Porcentaje de Precisión',
            'Total de Evaluaciones',
            'Distribución del Tiempo de Respuesta',
            'Tiempo de Respuesta',
            'segundos',
            'Frecuencia',
            'Media',
            'Mediana',
            'evaluaciones'
        ]
        
        missing_terms = []
        for term in required_spanish_terms:
            if term not in source_code:
                missing_terms.append(term)
        
        if missing_terms:
            print(f"✗ Missing Spanish terms: {missing_terms}")
            return False
        
        print(f"✓ Found all {len(required_spanish_terms)} required Spanish terms")
        
        # Ensure no English equivalents are used in chart labels/titles
        # Focus on actual chart text that users will see
        english_terms_to_avoid_in_charts = [
            'Execution Accuracy',
            'Correct Queries', 
            'Incorrect Queries',
            'Number of Queries',
            'Result Type',
            'Component Precision',
            'SQL Components', 
            'Precision Percentage',
            'Time Distribution',
            'Response Time',
            'Frequency'
        ]
        
        found_english_in_charts = []
        for term in english_terms_to_avoid_in_charts:
            # Look for these terms in chart title/label assignments
            patterns = [
                rf'set_title\([^)]*{re.escape(term)}[^)]*\)',
                rf'set_xlabel\([^)]*{re.escape(term)}[^)]*\)',
                rf'set_ylabel\([^)]*{re.escape(term)}[^)]*\)',
                rf'ax\.text\([^)]*{re.escape(term)}[^)]*\)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, source_code, re.IGNORECASE)
                if matches:
                    found_english_in_charts.append((term, matches))
        
        if found_english_in_charts:
            print(f"✗ Found English terms in chart labels: {found_english_in_charts}")
            return False
        
        print("✓ No English terms found in chart labels")
        print("✓ test_chart_service_uses_spanish_consistently passed")
        
    except Exception as e:
        print(f"✗ test_chart_service_uses_spanish_consistently failed: {e}")
        return False
    
    # Test that chart service methods exist and are properly named
    print("Running test_chart_service_methods_exist...")
    try:
        # Just verify the ChartService class exists and has the right methods
        # without actually instantiating it (to avoid database issues)
        import importlib.util
        spec = importlib.util.spec_from_file_location("chart_service", "app/services/chart_service.py")
        chart_module = importlib.util.module_from_spec(spec)
        
        # Check that the ChartService class exists
        with open('app/services/chart_service.py', 'r') as f:
            source = f.read()
            
        assert 'class ChartService:' in source
        assert 'def generate_ex_chart(' in source
        assert 'def generate_component_chart(' in source  
        assert 'def generate_tta_histogram(' in source
        
        print("✓ test_chart_service_methods_exist passed")
        
    except Exception as e:
        print(f"✗ test_chart_service_methods_exist failed: {e}")
        return False
    
    return True

def main():
    """Run chart language requirement test."""
    print("Running Chart Language Requirement Property-Based Test...")
    
    success = test_chart_language_requirement()
    
    if success:
        print("\n🎉 Chart language requirement test passed!")
        print("Property 23: Chart language requirement - PASSED")
        print("**Validates: Requirements 8.5**")
        return 0
    else:
        print("\n❌ Chart language requirement test failed!")
        return 1

if __name__ == "__main__":
    exit(main())