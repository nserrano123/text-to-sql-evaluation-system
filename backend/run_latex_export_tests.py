#!/usr/bin/env python3
"""
Run LaTeX export validity property-based tests.

**Feature: text-to-sql-evaluation, Property 26: LaTeX export validity**
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tests.property.test_latex_export_validity import (
    test_latex_export_has_valid_table_structure,
    test_latex_export_has_required_content,
    test_latex_export_has_correct_formatting,
    test_latex_export_has_valid_syntax,
    test_latex_export_is_ieeetran_compatible,
    test_latex_export_spanish_language_requirement,
    MockMetricsSummary,
    MockExportService
)
from hypothesis import given, strategies as st, settings
import random


def test_latex_export_validity_property_manual(summary_data):
    """Manual implementation of the property test without Hypothesis decorator"""
    # Ensure completed_evaluations <= total_evaluations for realistic data
    if summary_data['completed_evaluations'] > summary_data['total_evaluations']:
        summary_data['completed_evaluations'] = summary_data['total_evaluations']
    
    summary = MockMetricsSummary(summary_data)
    service = MockExportService()
    
    # Generate LaTeX
    latex_content = service._generate_latex_table(summary)
    
    # Property 1: Must be a valid string
    assert isinstance(latex_content, str), "LaTeX export must return a string"
    assert len(latex_content) > 0, "LaTeX export must not be empty"
    
    # Property 2: Must have valid LaTeX table structure
    assert latex_content.startswith('\\begin{table}'), "Must start with \\begin{table}"
    assert latex_content.endswith('\\end{table}'), "Must end with \\end{table}"
    assert '\\begin{tabular}' in latex_content, "Must contain \\begin{tabular}"
    assert '\\end{tabular}' in latex_content, "Must contain \\end{tabular}"
    
    # Property 3: Must have balanced braces
    open_braces = latex_content.count('{')
    close_braces = latex_content.count('}')
    assert open_braces == close_braces, f"Braces must be balanced: {open_braces} != {close_braces}"
    
    # Property 4: Must contain all required metrics
    required_content = [
        'Consultas Totales', 'Consultas Evaluadas', 'Execution Accuracy (EX)',
        'Tiempo Promedio de Respuesta (TTA)', 'SELECT', 'WHERE', 'GROUP BY',
        'ORDER BY', 'KEYWORDS', 'F1 Score Promedio'
    ]
    for content in required_content:
        assert content in latex_content, f"Must contain required content: {content}"
    
    # Property 5: Must have proper number formatting
    import re
    # Check that percentages are formatted correctly
    ex_pattern = r'\d+\.\d{2}\\%'
    assert re.search(ex_pattern, latex_content), "EX must be formatted as XX.XX\\%"
    
    # Check that TTA is formatted correctly
    tta_pattern = r'\d+\.\d{2}s'
    assert re.search(tta_pattern, latex_content), "TTA must be formatted as XX.XXs"
    
    # Check that F1 scores are formatted correctly (4 decimal places)
    f1_pattern = r'0\.\d{4}'
    f1_matches = re.findall(f1_pattern, latex_content)
    assert len(f1_matches) >= 5, "Must have at least 5 F1 scores formatted to 4 decimal places"
    
    # Property 6: Must be IEEEtran compatible
    ieeetran_elements = ['\\centering', '\\caption{', '\\label{tab:', '[htbp]']
    for element in ieeetran_elements:
        assert element in latex_content, f"Must contain IEEEtran-compatible element: {element}"
    
    # Property 7: Must have consistent data
    # The values in the LaTeX should correspond to the input data
    assert str(summary_data['total_evaluations']) in latex_content, "Must include correct total evaluations"
    assert str(summary_data['completed_evaluations']) in latex_content, "Must include correct completed evaluations"
    
    # Property 8: Must have proper LaTeX escaping
    # No unescaped special characters that would break LaTeX compilation
    # Check for problematic unescaped characters ($ ^ # but not & and _ which are valid in tables/labels)
    problematic_chars = ['$', '^', '#']
    for char in problematic_chars:
        if char in latex_content:
            char_positions = [i for i, c in enumerate(latex_content) if c == char]
            for pos in char_positions:
                if pos > 0:
                    preceding_char = latex_content[pos-1]
                    assert preceding_char == '\\', f"Special character '{char}' must be escaped"


def test_latex_export_validity_property_runner():
    """Run property-based test for LaTeX export validity with multiple examples"""
    print("Running Property-Based Tests for LaTeX Export Validity...")
    print("**Feature: text-to-sql-evaluation, Property 26: LaTeX export validity**")
    print()
    
    success_count = 0
    total_tests = 100
    
    print(f"Testing {total_tests} random examples...")
    
    for i in range(total_tests):
        try:
            # Generate random test data
            summary_data = {
                'execution_accuracy': random.uniform(0.0, 100.0),
                'average_time_to_answer': random.uniform(0.1, 3600.0),
                'component_scores': {
                    'select': random.uniform(0.0, 1.0),
                    'where': random.uniform(0.0, 1.0),
                    'group_by': random.uniform(0.0, 1.0),
                    'order_by': random.uniform(0.0, 1.0),
                    'keywords': random.uniform(0.0, 1.0)
                },
                'total_evaluations': random.randint(1, 1000),
                'completed_evaluations': random.randint(0, 1000)
            }
            
            # Ensure completed <= total for realistic data
            if summary_data['completed_evaluations'] > summary_data['total_evaluations']:
                summary_data['completed_evaluations'] = summary_data['total_evaluations']
            
            # Run the property test
            test_latex_export_validity_property_manual(summary_data)
            success_count += 1
            
            if (i + 1) % 20 == 0:
                print(f"  Completed {i + 1}/{total_tests} tests...")
                
        except Exception as e:
            print(f"  ✗ Test {i + 1} failed: {e}")
            return False
    
    print(f"✓ All {success_count}/{total_tests} property-based tests passed!")
    return True


def test_latex_export_handles_edge_cases_manual(total_evals, completed_evals):
    """Manual implementation of edge case test without Hypothesis decorator"""
    # Ensure completed <= total for realistic data
    if completed_evals > total_evals:
        completed_evals = total_evals
    
    summary_data = {
        'execution_accuracy': 0.0 if completed_evals == 0 else 50.0,
        'average_time_to_answer': 1.0,
        'component_scores': {
            'select': 0.0,
            'where': 0.0,
            'group_by': 0.0,
            'order_by': 0.0,
            'keywords': 0.0
        },
        'total_evaluations': total_evals,
        'completed_evaluations': completed_evals
    }
    
    summary = MockMetricsSummary(summary_data)
    service = MockExportService()
    
    # Generate LaTeX - should not fail even with edge cases
    latex_content = service._generate_latex_table(summary)
    
    # Should still be valid LaTeX
    assert isinstance(latex_content, str), "Must return string even for edge cases"
    assert '\\begin{table}' in latex_content, "Must have valid table structure for edge cases"
    assert '\\end{table}' in latex_content, "Must have valid table structure for edge cases"
    
    # Should handle zero values gracefully
    assert str(total_evals) in latex_content, "Must include total evaluations even if zero"
    assert str(completed_evals) in latex_content, "Must include completed evaluations even if zero"
    
    # Should format zero F1 scores correctly
    if all(score == 0.0 for score in summary_data['component_scores'].values()):
        assert '0.0000' in latex_content, "Must format zero F1 scores correctly"


def test_edge_cases():
    """Test specific edge cases"""
    print("\nTesting edge cases...")
    
    edge_cases = [
        (0, 0),      # No evaluations
        (1, 0),      # One query, no evaluations
        (1, 1),      # One query, one evaluation
        (100, 100),  # All queries evaluated
        (1000, 500), # Large dataset, half evaluated
    ]
    
    for total, completed in edge_cases:
        try:
            test_latex_export_handles_edge_cases_manual(total, completed)
            print(f"  ✓ Edge case ({total}, {completed}) passed")
        except Exception as e:
            print(f"  ✗ Edge case ({total}, {completed}) failed: {e}")
            return False
    
    return True


def run_all_tests():
    """Run all LaTeX export validity tests"""
    print("Running LaTeX Export Validity Property-Based Tests")
    print("=" * 60)
    
    tests = [
        ("Valid table structure", test_latex_export_has_valid_table_structure),
        ("Required content", test_latex_export_has_required_content),
        ("Correct formatting", test_latex_export_has_correct_formatting),
        ("Valid syntax", test_latex_export_has_valid_syntax),
        ("IEEEtran compatibility", test_latex_export_is_ieeetran_compatible),
        ("Spanish language requirement", test_latex_export_spanish_language_requirement),
    ]
    
    success = True
    
    # Run basic unit tests
    print("Running basic validation tests...")
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"  ✓ {test_name}")
        except Exception as e:
            print(f"  ✗ {test_name}: {e}")
            success = False
    
    if not success:
        print("\nBasic tests failed. Stopping execution.")
        return False
    
    # Run property-based tests
    print("\n" + "=" * 60)
    if not test_latex_export_validity_property_runner():
        success = False
    
    # Run edge case tests
    print("\n" + "=" * 60)
    if not test_edge_cases():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All LaTeX export validity tests passed!")
        print("\nProperty 26 validation complete:")
        print("- LaTeX export generates valid IEEEtran-compatible syntax")
        print("- All required metrics are included in Spanish")
        print("- Proper number formatting is applied")
        print("- Table structure is valid for academic papers")
    else:
        print("✗ Some LaTeX export validity tests failed!")
    
    return success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)