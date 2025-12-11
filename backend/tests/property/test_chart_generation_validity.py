"""
Property-based tests for chart generation validity.

**Feature: text-to-sql-evaluation, Property 21: Chart generation validity**
**Validates: Requirements 8.1, 8.2, 8.3**
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


class TestChartGenerationValidity:
    """Test that chart generation produces valid PNG files."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.chart_service = ChartService()
    
    @given(st.lists(execution_accuracy_strategy(), min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_ex_chart_generates_valid_png(self, execution_accuracy_records):
        """
        **Feature: text-to-sql-evaluation, Property 21: Chart generation validity**
        
        For any list of ExecutionAccuracy records, generating an EX chart should 
        produce a valid PNG file that can be opened and read.
        """
        # Generate chart
        chart_data = self.chart_service.generate_ex_chart(execution_accuracy_records)
        
        # Verify it's valid PNG data
        assert isinstance(chart_data, bytes)
        assert len(chart_data) > 0
        
        # Verify it can be opened as a valid image
        image_buffer = io.BytesIO(chart_data)
        with Image.open(image_buffer) as img:
            assert img.format == 'PNG'
            assert img.size[0] > 0  # Width > 0
            assert img.size[1] > 0  # Height > 0
    
    @given(st.lists(component_matching_strategy(), min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_component_chart_generates_valid_png(self, component_matching_records):
        """
        **Feature: text-to-sql-evaluation, Property 21: Chart generation validity**
        
        For any list of ComponentMatching records, generating a component chart should 
        produce a valid PNG file that can be opened and read.
        """
        # Generate chart
        chart_data = self.chart_service.generate_component_chart(component_matching_records)
        
        # Verify it's valid PNG data
        assert isinstance(chart_data, bytes)
        assert len(chart_data) > 0
        
        # Verify it can be opened as a valid image
        image_buffer = io.BytesIO(chart_data)
        with Image.open(image_buffer) as img:
            assert img.format == 'PNG'
            assert img.size[0] > 0  # Width > 0
            assert img.size[1] > 0  # Height > 0
    
    @given(st.lists(time_to_answer_strategy(), min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_tta_histogram_generates_valid_png(self, time_to_answer_records):
        """
        **Feature: text-to-sql-evaluation, Property 21: Chart generation validity**
        
        For any list of TimeToAnswer records, generating a TTA histogram should 
        produce a valid PNG file that can be opened and read.
        """
        # Generate chart
        chart_data = self.chart_service.generate_tta_histogram(time_to_answer_records)
        
        # Verify it's valid PNG data
        assert isinstance(chart_data, bytes)
        assert len(chart_data) > 0
        
        # Verify it can be opened as a valid image
        image_buffer = io.BytesIO(chart_data)
        with Image.open(image_buffer) as img:
            assert img.format == 'PNG'
            assert img.size[0] > 0  # Width > 0
            assert img.size[1] > 0  # Height > 0
    
    def test_empty_data_raises_value_error(self):
        """Test that empty data raises appropriate errors."""
        with pytest.raises(ValueError, match="No execution accuracy data available"):
            self.chart_service.generate_ex_chart([])
        
        with pytest.raises(ValueError, match="No component matching data available"):
            self.chart_service.generate_component_chart([])
        
        with pytest.raises(ValueError, match="No time to answer data available"):
            self.chart_service.generate_tta_histogram([])