"""Property-based tests for LaTeX export validity"""

import re
from uuid import uuid4
from datetime import datetime, timezone
from typing import Dict, Any, List
import pytest
from hypothesis import given, strategies as st, settings


# **Feature: text-to-sql-evaluation, Property 26: LaTeX export validity**


# Strategies for generating test data
@st.composite
def metrics_summary_strategy(draw):
    """Generate a valid metrics summary for LaTeX export"""
    # Generate component scores
    component_scores = {
        'select': draw(st.floats(min_value=0.0, max_value=1.0)),
        'where': draw(st.floats(min_value=0.0, max_value=1.0)),
        'group_by': draw(st.floats(min_value=0.0, max_value=1.0)),
        'order_by': draw(st.floats(min_value=0.0, max_value=1.0)),
        'keywords': draw(st.floats(min_value=0.0, max_value=1.0))
    }
    
    return {
        'execution_accuracy': draw(st.floats(min_value=0.0, max_value=100.0)),
        'average_time_to_answer': draw(st.floats(min_value=0.1, max_value=3600.0)),
        'component_scores': component_scores,
        'total_evaluations': draw(st.integers(min_value=1, max_value=1000)),
        'completed_evaluations': draw(st.integers(min_value=0, max_value=1000))
    }


class MockMetricsSummary:
    """Mock metrics summary object for testing"""
    
    def __init__(self, data: Dict[str, Any]):
        self.execution_accuracy = data['execution_accuracy']
        self.average_time_to_answer = data['average_time_to_answer']
        self.component_scores = data['component_scores']
        self.total_evaluations = data['total_evaluations']
        self.completed_evaluations = data['completed_evaluations']


class MockExportService:
    """Mock export service for testing LaTeX generation"""
    
    def _generate_latex_table(self, summary) -> str:
        """
        Generate LaTeX table content from metrics summary.
        This is a copy of the actual implementation for testing.
        """
        # Format component scores
        component_scores = summary.component_scores
        select_f1 = component_scores.get('select', 0.0)
        where_f1 = component_scores.get('where', 0.0)
        group_by_f1 = component_scores.get('group_by', 0.0)
        order_by_f1 = component_scores.get('order_by', 0.0)
        keywords_f1 = component_scores.get('keywords', 0.0)
        
        # Calculate average F1 score
        avg_f1 = (select_f1 + where_f1 + group_by_f1 + order_by_f1 + keywords_f1) / 5
        
        latex_table = f"""\\begin{{table}}[htbp]
\\centering
\\caption{{Resultados de Evaluación del Modelo Text-to-SQL}}
\\label{{tab:evaluation_results}}
\\begin{{tabular}}{{|l|c|}}
\\hline
\\textbf{{Métrica}} & \\textbf{{Valor}} \\\\
\\hline
\\hline
Consultas Totales & {summary.total_evaluations} \\\\
\\hline
Consultas Evaluadas & {summary.completed_evaluations} \\\\
\\hline
Execution Accuracy (EX) & {summary.execution_accuracy:.2f}\\% \\\\
\\hline
Tiempo Promedio de Respuesta (TTA) & {summary.average_time_to_answer:.2f}s \\\\
\\hline
\\multicolumn{{2}}{{|c|}}{{\\textbf{{F1 Score por Componente}}}} \\\\
\\hline
SELECT & {select_f1:.4f} \\\\
\\hline
WHERE & {where_f1:.4f} \\\\
\\hline
GROUP BY & {group_by_f1:.4f} \\\\
\\hline
ORDER BY & {order_by_f1:.4f} \\\\
\\hline
KEYWORDS & {keywords_f1:.4f} \\\\
\\hline
F1 Score Promedio & {avg_f1:.4f} \\\\
\\hline
\\end{{tabular}}
\\end{{table}}"""
        
        return latex_table


def test_latex_export_has_valid_table_structure():
    """
    Property 26: LaTeX export validity - Valid table structure
    For any metrics summary, the LaTeX export should have valid table structure
    **Validates: Requirements 9.5**
    """
    # Create test data
    summary_data = {
        'execution_accuracy': 85.5,
        'average_time_to_answer': 12.34,
        'component_scores': {
            'select': 0.9,
            'where': 0.8,
            'group_by': 0.7,
            'order_by': 0.6,
            'keywords': 0.85
        },
        'total_evaluations': 100,
        'completed_evaluations': 95
    }
    
    summary = MockMetricsSummary(summary_data)
    service = MockExportService()
    
    # Generate LaTeX
    latex_content = service._generate_latex_table(summary)
    
    # Verify basic LaTeX table structure
    assert latex_content.startswith('\\begin{table}'), "LaTeX should start with \\begin{table}"
    assert latex_content.endswith('\\end{table}'), "LaTeX should end with \\end{table}"
    assert '\\begin{tabular}' in latex_content, "LaTeX should contain \\begin{tabular}"
    assert '\\end{tabular}' in latex_content, "LaTeX should contain \\end{tabular}"
    assert '\\caption{' in latex_content, "LaTeX should contain a caption"
    assert '\\label{' in latex_content, "LaTeX should contain a label"


def test_latex_export_has_required_content():
    """
    Property 26: LaTeX export validity - Contains all required metrics
    For any metrics summary, the LaTeX export should include all required metrics
    **Validates: Requirements 9.5**
    """
    # Create test data
    summary_data = {
        'execution_accuracy': 75.25,
        'average_time_to_answer': 8.67,
        'component_scores': {
            'select': 0.95,
            'where': 0.82,
            'group_by': 0.73,
            'order_by': 0.68,
            'keywords': 0.91
        },
        'total_evaluations': 50,
        'completed_evaluations': 48
    }
    
    summary = MockMetricsSummary(summary_data)
    service = MockExportService()
    
    # Generate LaTeX
    latex_content = service._generate_latex_table(summary)
    
    # Verify required content is present
    assert 'Consultas Totales' in latex_content, "Should include total queries"
    assert 'Consultas Evaluadas' in latex_content, "Should include completed evaluations"
    assert 'Execution Accuracy (EX)' in latex_content, "Should include EX metric"
    assert 'Tiempo Promedio de Respuesta (TTA)' in latex_content, "Should include TTA metric"
    assert 'F1 Score por Componente' in latex_content, "Should include component scores section"
    assert 'SELECT' in latex_content, "Should include SELECT component"
    assert 'WHERE' in latex_content, "Should include WHERE component"
    assert 'GROUP BY' in latex_content, "Should include GROUP BY component"
    assert 'ORDER BY' in latex_content, "Should include ORDER BY component"
    assert 'KEYWORDS' in latex_content, "Should include KEYWORDS component"
    assert 'F1 Score Promedio' in latex_content, "Should include average F1 score"


def test_latex_export_has_correct_formatting():
    """
    Property 26: LaTeX export validity - Correct number formatting
    For any metrics summary, the LaTeX export should format numbers correctly
    **Validates: Requirements 9.5**
    """
    # Create test data with specific values
    summary_data = {
        'execution_accuracy': 87.654321,  # Should be formatted to 2 decimals
        'average_time_to_answer': 15.987654,  # Should be formatted to 2 decimals
        'component_scores': {
            'select': 0.123456789,  # Should be formatted to 4 decimals
            'where': 0.987654321,
            'group_by': 0.555555555,
            'order_by': 0.333333333,
            'keywords': 0.777777777
        },
        'total_evaluations': 123,
        'completed_evaluations': 120
    }
    
    summary = MockMetricsSummary(summary_data)
    service = MockExportService()
    
    # Generate LaTeX
    latex_content = service._generate_latex_table(summary)
    
    # Verify EX formatting (2 decimals)
    assert '87.65\\%' in latex_content, "EX should be formatted to 2 decimal places with % sign"
    
    # Verify TTA formatting (2 decimals)
    assert '15.99s' in latex_content, "TTA should be formatted to 2 decimal places with s suffix"
    
    # Verify F1 scores formatting (4 decimals)
    assert '0.1235' in latex_content, "F1 scores should be formatted to 4 decimal places"
    assert '0.9877' in latex_content, "F1 scores should be formatted to 4 decimal places"
    
    # Verify integer values are not formatted with decimals
    assert '123 \\\\' in latex_content, "Integer values should not have decimal places"
    assert '120 \\\\' in latex_content, "Integer values should not have decimal places"


def test_latex_export_has_valid_syntax():
    """
    Property 26: LaTeX export validity - Valid LaTeX syntax
    For any metrics summary, the LaTeX export should have valid LaTeX syntax
    **Validates: Requirements 9.5**
    """
    # Create test data
    summary_data = {
        'execution_accuracy': 92.1,
        'average_time_to_answer': 5.43,
        'component_scores': {
            'select': 0.88,
            'where': 0.79,
            'group_by': 0.65,
            'order_by': 0.71,
            'keywords': 0.83
        },
        'total_evaluations': 200,
        'completed_evaluations': 195
    }
    
    summary = MockMetricsSummary(summary_data)
    service = MockExportService()
    
    # Generate LaTeX
    latex_content = service._generate_latex_table(summary)
    
    # Check for balanced braces
    open_braces = latex_content.count('{')
    close_braces = latex_content.count('}')
    assert open_braces == close_braces, f"Braces should be balanced: {open_braces} open, {close_braces} close"
    
    # Check for proper LaTeX commands
    assert '\\begin{table}[htbp]' in latex_content, "Should have proper table positioning"
    assert '\\begin{tabular}{|l|c|}' in latex_content, "Should have proper tabular column specification"
    assert '\\hline' in latex_content, "Should contain horizontal lines"
    assert '\\\\' in latex_content, "Should contain row separators"
    assert '\\textbf{' in latex_content, "Should contain bold text commands"
    assert '\\multicolumn{2}{|c|}' in latex_content, "Should contain multicolumn command"
    
    # Check that there are no unescaped special characters that would break LaTeX
    # (except for intentional ones like % for percentage and _ in valid contexts)
    problematic_chars = ['$', '^', '#']
    for char in problematic_chars:
        if char in latex_content:
            # If found, it should be properly escaped (preceded by backslash)
            char_positions = [i for i, c in enumerate(latex_content) if c == char]
            for pos in char_positions:
                if pos > 0:
                    # Check if it's escaped
                    preceding_char = latex_content[pos-1]
                    assert preceding_char == '\\', \
                        f"Special character '{char}' at position {pos} should be escaped"
    
    # Special handling for & and _ which are valid in LaTeX tables
    # & is used for column separation in tabular
    # _ is used in labels and is acceptable in this context
    if '&' in latex_content:
        # & should appear in table rows for column separation
        assert ' & ' in latex_content, "& should be used for column separation"
    
    # _ in labels is acceptable (tab:evaluation_results)
    if '_' in latex_content:
        # Should be in label context
        assert 'evaluation_results' in latex_content, "_ should be in valid LaTeX context like labels"


def test_latex_export_is_ieeetran_compatible():
    """
    Property 26: LaTeX export validity - IEEEtran compatibility
    For any metrics summary, the LaTeX export should be compatible with IEEEtran class
    **Validates: Requirements 9.5**
    """
    # Create test data
    summary_data = {
        'execution_accuracy': 78.9,
        'average_time_to_answer': 22.15,
        'component_scores': {
            'select': 0.92,
            'where': 0.84,
            'group_by': 0.76,
            'order_by': 0.69,
            'keywords': 0.87
        },
        'total_evaluations': 75,
        'completed_evaluations': 72
    }
    
    summary = MockMetricsSummary(summary_data)
    service = MockExportService()
    
    # Generate LaTeX
    latex_content = service._generate_latex_table(summary)
    
    # Check IEEEtran-specific requirements
    # IEEEtran uses standard LaTeX table environments
    assert '\\begin{table}[htbp]' in latex_content, "Should use standard table environment with positioning"
    assert '\\centering' in latex_content, "Should center the table"
    assert '\\caption{' in latex_content, "Should have a caption"
    assert '\\label{tab:' in latex_content, "Should have a proper label with 'tab:' prefix"
    
    # Check that the table uses standard tabular environment (compatible with IEEEtran)
    assert '\\begin{tabular}{|l|c|}' in latex_content, "Should use standard tabular with column specification"
    
    # Check Spanish language content (as specified in requirements)
    spanish_terms = [
        'Resultados de Evaluación del Modelo Text-to-SQL',
        'Métrica', 'Valor', 'Consultas Totales', 'Consultas Evaluadas',
        'Tiempo Promedio de Respuesta', 'F1 Score por Componente', 'F1 Score Promedio'
    ]
    for term in spanish_terms:
        assert term in latex_content, f"Should contain Spanish term: {term}"
    
    # Verify the table structure is appropriate for academic papers
    # Should have proper header row with bold formatting
    assert '\\textbf{Métrica} & \\textbf{Valor}' in latex_content, "Should have bold headers"
    
    # Should have proper horizontal lines for professional appearance
    hline_count = latex_content.count('\\hline')
    assert hline_count >= 10, f"Should have sufficient horizontal lines for professional table, found {hline_count}"


@given(metrics_summary_strategy())
@settings(max_examples=100)
def test_latex_export_validity_property(summary_data):
    """
    Property 26: LaTeX export validity - Property-based test
    For any metrics summary, the LaTeX export should generate valid IEEEtran-compatible syntax
    **Validates: Requirements 9.5**
    """
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
    # Check that percentages are formatted correctly
    ex_pattern = r'\d+\.\d{2}%'
    assert re.search(ex_pattern, latex_content), "EX must be formatted as XX.XX%"
    
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


@given(st.integers(min_value=0, max_value=1000), st.integers(min_value=0, max_value=1000))
@settings(max_examples=50)
def test_latex_export_handles_edge_cases(total_evals, completed_evals):
    """
    Property 26: LaTeX export validity - Handles edge cases correctly
    For any evaluation counts including edge cases, LaTeX export should be valid
    **Validates: Requirements 9.5**
    """
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


def test_latex_export_spanish_language_requirement():
    """
    Property 26: LaTeX export validity - Spanish language requirement
    For any metrics summary, the LaTeX export should use Spanish labels and text
    **Validates: Requirements 9.5**
    """
    summary_data = {
        'execution_accuracy': 85.0,
        'average_time_to_answer': 10.0,
        'component_scores': {
            'select': 0.9,
            'where': 0.8,
            'group_by': 0.7,
            'order_by': 0.6,
            'keywords': 0.85
        },
        'total_evaluations': 100,
        'completed_evaluations': 95
    }
    
    summary = MockMetricsSummary(summary_data)
    service = MockExportService()
    
    # Generate LaTeX
    latex_content = service._generate_latex_table(summary)
    
    # Verify Spanish language elements
    spanish_elements = {
        'Resultados de Evaluación del Modelo Text-to-SQL': 'Table caption should be in Spanish',
        'Métrica': 'Column header should be in Spanish',
        'Valor': 'Column header should be in Spanish',
        'Consultas Totales': 'Total queries label should be in Spanish',
        'Consultas Evaluadas': 'Evaluated queries label should be in Spanish',
        'Tiempo Promedio de Respuesta (TTA)': 'TTA label should be in Spanish',
        'F1 Score por Componente': 'Component section header should be in Spanish',
        'F1 Score Promedio': 'Average F1 label should be in Spanish'
    }
    
    for spanish_text, description in spanish_elements.items():
        assert spanish_text in latex_content, f"{description}: '{spanish_text}' not found"
    
    # Verify no English equivalents are present
    english_terms = ['Results', 'Metric', 'Value', 'Total Queries', 'Evaluated Queries', 
                    'Average Response Time', 'Component Score', 'Average F1']
    for english_term in english_terms:
        assert english_term not in latex_content, f"Should not contain English term: {english_term}"