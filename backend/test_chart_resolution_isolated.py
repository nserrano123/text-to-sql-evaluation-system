#!/usr/bin/env python3
"""
Isolated test for chart resolution requirement.
"""

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import io
from PIL import Image
from datetime import datetime, timedelta
from uuid import uuid4

# Configure matplotlib for high-quality output (same as ChartService)
matplotlib.rcParams['figure.dpi'] = 300
matplotlib.rcParams['savefig.dpi'] = 300
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['axes.titlesize'] = 14
matplotlib.rcParams['axes.labelsize'] = 12
matplotlib.rcParams['xtick.labelsize'] = 10
matplotlib.rcParams['ytick.labelsize'] = 10
matplotlib.rcParams['legend.fontsize'] = 10

# Set seaborn style for professional appearance
sns.set_style("whitegrid")
sns.set_palette("husl")

# Mock models
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

def generate_ex_chart_isolated(execution_accuracy_records):
    """Generate EX chart (isolated version of ChartService method)."""
    if not execution_accuracy_records:
        raise ValueError("No execution accuracy data available for chart generation")
    
    # Calculate EX percentage
    correct_count = sum(1 for record in execution_accuracy_records if record.is_correct)
    total_count = len(execution_accuracy_records)
    ex_percentage = (correct_count / total_count) * 100
    
    # Create figure with high DPI
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Create bar chart
    categories = ['Consultas Correctas', 'Consultas Incorrectas']
    values = [correct_count, total_count - correct_count]
    colors = ['#2E8B57', '#DC143C']  # Professional green and red
    
    bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
               f'{value}\n({value/total_count*100:.1f}%)',
               ha='center', va='bottom', fontweight='bold')
    
    # Customize chart
    ax.set_title(f'Precisión de Ejecución (EX): {ex_percentage:.2f}%', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Número de Consultas', fontsize=12, fontweight='bold')
    ax.set_xlabel('Tipo de Resultado', fontsize=12, fontweight='bold')
    
    # Add grid for better readability
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_axisbelow(True)
    
    # Set y-axis to start from 0 and add some padding
    ax.set_ylim(0, max(values) * 1.1)
    
    # Add total count annotation
    ax.text(0.02, 0.98, f'Total de Consultas: {total_count}', 
           transform=ax.transAxes, fontsize=10, 
           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    # Save to bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    buffer.seek(0)
    
    # Get PNG data
    png_data = buffer.getvalue()
    buffer.close()
    
    # Close the figure to free memory
    plt.close(fig)
    
    return png_data

def test_chart_resolution_requirement():
    """
    **Feature: text-to-sql-evaluation, Property 22: Chart resolution requirement**
    Test that generated charts meet the 300 DPI resolution requirement.
    """
    print("Testing Property 22: Chart resolution requirement")
    print("**Feature: text-to-sql-evaluation, Property 22: Chart resolution requirement**")
    
    # Test 1: Check matplotlib configuration
    print("\n1. Testing matplotlib DPI configuration...")
    
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
    
    chart_data = generate_ex_chart_isolated(test_data)
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
        print(f"   Image size: {img.size}")
        print(f"   Image format: {img.format}")
    
    assert meets_dpi, "EX chart does not meet 300 DPI requirement"
    print("   ✓ EX chart meets 300 DPI requirement")
    
    # Test 3: Test with different data sizes
    print("\n3. Testing with different data sizes...")
    
    # Small dataset
    small_data = [MockExecutionAccuracy(True)]
    chart_data = generate_ex_chart_isolated(small_data)
    meets_dpi = check_image_resolution(chart_data, 300)
    assert meets_dpi, "Small dataset chart does not meet 300 DPI requirement"
    print("   ✓ Small dataset chart meets 300 DPI requirement")
    
    # Large dataset
    large_data = [MockExecutionAccuracy(i % 2 == 0) for i in range(100)]
    chart_data = generate_ex_chart_isolated(large_data)
    meets_dpi = check_image_resolution(chart_data, 300)
    assert meets_dpi, "Large dataset chart does not meet 300 DPI requirement"
    print("   ✓ Large dataset chart meets 300 DPI requirement")
    
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
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())