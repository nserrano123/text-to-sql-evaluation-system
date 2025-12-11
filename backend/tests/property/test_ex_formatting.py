"""Property-based test for EX formatting"""

import pytest
from hypothesis import given, strategies as st, settings
from uuid import uuid4
from datetime import datetime
import re

from app.models.execution_accuracy import ExecutionAccuracy
from app.services.execution_accuracy_service import ExecutionAccuracyService
from app.repositories.execution_accuracy_repository import ExecutionAccuracyRepository


# Strategy for generating ExecutionAccuracy records
def execution_accuracy_strategy():
    """Generate ExecutionAccuracy records with random is_correct values"""
    return st.builds(
        ExecutionAccuracy,
        id=st.just(uuid4()),
        evaluation_id=st.just(uuid4()),
        results_match=st.one_of(st.none(), st.booleans()),
        is_correct=st.booleans(),
        evaluator_notes=st.one_of(st.none(), st.text()),
        created_at=st.just(datetime.now())
    )


class TestEXFormatting:
    """Property-based tests for EX formatting"""
    
    def setup_method(self):
        """Set up test dependencies"""
        # Create a mock repository for testing
        self.repository = ExecutionAccuracyRepository(None)  # We won't use the actual DB
        self.service = ExecutionAccuracyService(self.repository)
    
    @given(st.lists(execution_accuracy_strategy(), min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_ex_formatting_two_decimal_places(self, execution_accuracy_records):
        """
        **Feature: text-to-sql-evaluation, Property 7: EX formatting**
        **Validates: Requirements 3.3**
        
        For any calculated EX value, when displayed, it should be formatted 
        with exactly two decimal places
        """
        # Calculate EX using the service
        ex_result = self.service.calculate_ex(execution_accuracy_records)
        
        # Convert to string to check formatting
        ex_str = str(ex_result)
        
        # Check that the result is a valid float
        assert isinstance(ex_result, float), f"EX result should be float, got {type(ex_result)}"
        
        # Check that when converted to string, it has at most 2 decimal places
        # This regex matches numbers with 0, 1, or 2 decimal places
        decimal_pattern = r'^\d+(\.\d{1,2})?$'
        assert re.match(decimal_pattern, ex_str), (
            f"EX result {ex_str} should have at most 2 decimal places"
        )
        
        # Additional check: if there are decimal places, there should be exactly 1 or 2
        if '.' in ex_str:
            decimal_part = ex_str.split('.')[1]
            assert len(decimal_part) <= 2, (
                f"EX result {ex_str} should have at most 2 decimal places, "
                f"but has {len(decimal_part)}"
            )
    
    def test_ex_formatting_specific_cases(self):
        """Test specific cases that should result in exact decimal formatting"""
        
        # Test case: 1/3 should be 33.33 (not 33.333...)
        records_one_third = [
            ExecutionAccuracy(id=uuid4(), evaluation_id=uuid4(), is_correct=True, created_at=datetime.now()),
            ExecutionAccuracy(id=uuid4(), evaluation_id=uuid4(), is_correct=False, created_at=datetime.now()),
            ExecutionAccuracy(id=uuid4(), evaluation_id=uuid4(), is_correct=False, created_at=datetime.now()),
        ]
        result = self.service.calculate_ex(records_one_third)
        assert result == 33.33, f"1/3 should be formatted as 33.33, got {result}"
        
        # Test case: 2/3 should be 66.67 (not 66.666...)
        records_two_thirds = [
            ExecutionAccuracy(id=uuid4(), evaluation_id=uuid4(), is_correct=True, created_at=datetime.now()),
            ExecutionAccuracy(id=uuid4(), evaluation_id=uuid4(), is_correct=True, created_at=datetime.now()),
            ExecutionAccuracy(id=uuid4(), evaluation_id=uuid4(), is_correct=False, created_at=datetime.now()),
        ]
        result = self.service.calculate_ex(records_two_thirds)
        assert result == 66.67, f"2/3 should be formatted as 66.67, got {result}"
        
        # Test case: 1/7 should be 14.29 (not 14.285714...)
        records_one_seventh = [
            ExecutionAccuracy(id=uuid4(), evaluation_id=uuid4(), is_correct=True, created_at=datetime.now())
        ] + [
            ExecutionAccuracy(id=uuid4(), evaluation_id=uuid4(), is_correct=False, created_at=datetime.now())
            for _ in range(6)
        ]
        result = self.service.calculate_ex(records_one_seventh)
        assert result == 14.29, f"1/7 should be formatted as 14.29, got {result}"
        
        # Test case: Perfect scores should be 100.0 or 100.00
        records_perfect = [
            ExecutionAccuracy(id=uuid4(), evaluation_id=uuid4(), is_correct=True, created_at=datetime.now())
            for _ in range(5)
        ]
        result = self.service.calculate_ex(records_perfect)
        assert result == 100.0, f"Perfect score should be 100.0, got {result}"
        
        # Test case: Zero score should be 0.0 or 0.00
        records_zero = [
            ExecutionAccuracy(id=uuid4(), evaluation_id=uuid4(), is_correct=False, created_at=datetime.now())
            for _ in range(5)
        ]
        result = self.service.calculate_ex(records_zero)
        assert result == 0.0, f"Zero score should be 0.0, got {result}"
    
    def test_ex_formatting_precision_consistency(self):
        """Test that the formatting is consistent and precise"""
        
        # Create a case that would result in many decimal places without rounding
        # 1/6 = 0.16666... should become 16.67
        records = [
            ExecutionAccuracy(id=uuid4(), evaluation_id=uuid4(), is_correct=True, created_at=datetime.now())
        ] + [
            ExecutionAccuracy(id=uuid4(), evaluation_id=uuid4(), is_correct=False, created_at=datetime.now())
            for _ in range(5)
        ]
        
        result = self.service.calculate_ex(records)
        
        # Should be exactly 16.67 (rounded from 16.666...)
        assert result == 16.67, f"1/6 should be formatted as 16.67, got {result}"
        
        # Verify it's actually rounded, not truncated
        # If it were truncated, it would be 16.66
        assert result != 16.66, "Result should be rounded, not truncated"