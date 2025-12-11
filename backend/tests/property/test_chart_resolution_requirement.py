"""
Property-based tests for chart resolution requirements.

**Feature: text-to-sql-evaluation, Property 22: Chart resolution requirement**
**Validates: Requirements 8.4**
"""

import pytest
from hypothesis import given, strategies as st, settings
import io
from PIL import Image
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.chart_service import ChartService
from app.models.execution_accuracy import ExecutionAccuracy
from app.models.component_matching import ComponentMatching
from app.models.time_to_answer import TimeToAnswer


# Strategies for generating test data
@st.composite
def execution_accuracy_strategy(draw):
    """Generate ExecutionAccuracy objects for testing."""
    return ExecutionAccuracy(
        id=uuid4(),
        evaluation_id=uuid4(),
        results_match=draw(st.one_of(st.booleans(), st.none())),
        is_correct=draw(st.booleans()),
        evaluator_notes=draw(st.one_of(st.text(max_size=100), st.none())),
        created_at=datetime.now()
    )


@st.composite
def component_matching_strategy(draw):
    """Generate ComponentMatching objects for testing."""
    return ComponentMatching(
        id=uuid4(),
        evaluation_id=uuid4(),
        select_correct=draw(st.booleans()),
        where_correct=draw(st.booleans()),
        group_by_correct=draw(st.booleans()),
        order_by_correct=draw(st.booleans()),
        keywords_correct=draw(st.booleans()),
        f1_score=draw(st.one_of(st.floats(min_value=0.0, max_value=1.0), st.none())),
        evaluator_notes=draw(st.one_of(st.text(max_size=100), st.none())),
        created_at=datetime.now()
    )


@st.composite
def time_to_answer_strategy(draw):
    """Generate TimeToAnswer objects for testing."""
    start_time = datetime.now() - timedelta(seconds=draw(st.integers(min_value=1, max_value=3600)))
    end_time = start_time + timedelta(seconds=draw(st.integers(min_value=1, max_value=1800)))
    duration_seconds = (end_time - start_time).total_seconds()
    
    return TimeToAnswer(
        id=uuid4(),
        evaluation_id=uuid4(),
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration_seconds,
        created_at=datetime.now()
    )


class TestChartResolutionRequirement:
    """Test that generated charts meet the 300 DPI resolution requirement."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.chart_service = ChartService()
    
    def _check_image_resolution(self, chart_data: bytes, min_dpi: int = 300):
        """
        Helper method to check if image meets DPI requirements.
        
        Args:
            chart_data: PNG image data
            min_dpi: Minimum required DPI
            
        Returns:
            bool: True if image meets DPI requirement
        """
        image_buffer = io.BytesIO(chart_data)
        with Image.open(image_buffer) as img:
            # Get DPI info from image
            dpi = img.info.get('dpi', (72, 72))  # Default to 72 DPI if not set
            
            # DPI can be a tuple (x_dpi, y_dpi) or a single value
            # Allow small tolerance for floating point precision (299.99 should pass for 300)
            tolerance = 0.1
            if isinstance(dpi, tuple):
                x_dpi, y_dpi = dpi
                return x_dpi >= (min_dpi - tolerance) and y_dpi >= (min_dpi - tolerance)
            else:
                return dpi >= (min_dpi - tolerance)
    
    @given(st.lists(execution_accuracy_strategy(), min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_ex_chart_meets_dpi_requirement(self, execution_accuracy_records):
        """
        **Feature: text-to-sql-evaluation, Property 22: Chart resolution requirement**
        
        For any generated EX chart PNG, the resolution should be at least 300 DPI.
        """
        # Generate chart
        chart_data = self.chart_service.generate_ex_chart(execution_accuracy_records)
        
        # Verify DPI requirement
        assert self._check_image_resolution(chart_data, min_dpi=300), \
            "EX chart does not meet 300 DPI requirement"
    
    @given(st.lists(component_matching_strategy(), min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_component_chart_meets_dpi_requirement(self, component_matching_records):
        """
        **Feature: text-to-sql-evaluation, Property 22: Chart resolution requirement**
        
        For any generated component chart PNG, the resolution should be at least 300 DPI.
        """
        # Generate chart
        chart_data = self.chart_service.generate_component_chart(component_matching_records)
        
        # Verify DPI requirement
        assert self._check_image_resolution(chart_data, min_dpi=300), \
            "Component chart does not meet 300 DPI requirement"
    
    @given(st.lists(time_to_answer_strategy(), min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_tta_histogram_meets_dpi_requirement(self, time_to_answer_records):
        """
        **Feature: text-to-sql-evaluation, Property 22: Chart resolution requirement**
        
        For any generated TTA histogram PNG, the resolution should be at least 300 DPI.
        """
        # Generate chart
        chart_data = self.chart_service.generate_tta_histogram(time_to_answer_records)
        
        # Verify DPI requirement
        assert self._check_image_resolution(chart_data, min_dpi=300), \
            "TTA histogram does not meet 300 DPI requirement"
    
    def test_chart_service_dpi_configuration(self):
        """Test that ChartService is configured with 300 DPI."""
        import matplotlib
        
        # Check that matplotlib is configured for 300 DPI
        assert matplotlib.rcParams['figure.dpi'] == 300, \
            "ChartService not configured with 300 DPI for figure.dpi"
        assert matplotlib.rcParams['savefig.dpi'] == 300, \
            "ChartService not configured with 300 DPI for savefig.dpi"