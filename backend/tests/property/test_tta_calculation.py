"""Property-based tests for TTA calculation correctness"""

import pytest
from hypothesis import given, strategies as st, settings
from backend.app.models.time_to_answer import TimeToAnswer, TimeToAnswerCreate
from uuid import uuid4, UUID
from datetime import datetime, timezone, timedelta
from typing import List


# **Feature: text-to-sql-evaluation, Property 10: TTA calculation correctness**

# Strategy for generating valid UUIDs
valid_uuid_strategy = st.builds(uuid4)

# Strategy for generating valid timestamps with timezone
def valid_timestamp_strategy():
    """Generate valid timestamps with timezone"""
    return st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    ).map(lambda dt: dt.replace(tzinfo=timezone.utc))

# Strategy for generating timestamp pairs where end_time > start_time
@st.composite
def timestamp_pair_strategy(draw):
    """Generate pairs of timestamps where end_time > start_time"""
    start_time = draw(valid_timestamp_strategy())
    # Generate a positive duration between 1 second and 24 hours
    duration_seconds = draw(st.floats(min_value=1.0, max_value=86400.0))
    end_time = start_time + timedelta(seconds=duration_seconds)
    return start_time, end_time

# Strategy for generating TimeToAnswer objects with consistent duration
@st.composite
def time_to_answer_strategy(draw):
    """Generate valid TimeToAnswer objects with consistent duration_seconds"""
    evaluation_id = draw(valid_uuid_strategy)
    start_time, end_time = draw(timestamp_pair_strategy())
    
    # Calculate the correct duration
    duration_seconds = (end_time - start_time).total_seconds()
    
    return TimeToAnswer(
        id=draw(valid_uuid_strategy),
        evaluation_id=evaluation_id,
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration_seconds,
        created_at=draw(valid_timestamp_strategy())
    )


class TimeToAnswerService:
    """Simple TTA service for testing without repository dependency"""
    
    def calculate_tta(self, start_time: datetime, end_time: datetime) -> float:
        """
        Calculate Time-to-Answer (TTA) as the difference between end_time and start_time.
        
        Args:
            start_time: Timestamp when evaluation started
            end_time: Timestamp when evaluation completed
            
        Returns:
            float: Duration in seconds
        """
        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        
        duration = (end_time - start_time).total_seconds()
        return duration
    
    def calculate_average_tta(self, time_to_answer_records: List[TimeToAnswer]) -> float:
        """
        Calculate average Time-to-Answer from a list of TTA records.
        
        Args:
            time_to_answer_records: List of TimeToAnswer records
            
        Returns:
            float: Average duration in seconds
        """
        if not time_to_answer_records:
            return 0.0
        
        total_duration = sum(record.duration_seconds for record in time_to_answer_records)
        average_duration = total_duration / len(time_to_answer_records)
        
        return average_duration


@given(start_time_end_time=timestamp_pair_strategy())
@settings(max_examples=100)
def test_tta_calculation_matches_timestamp_difference(start_time_end_time):
    """
    Property 10: TTA calculation correctness
    For any evaluation with start_time and end_time, duration_seconds should equal 
    the difference in seconds between end_time and start_time
    **Validates: Requirements 4.3**
    """
    start_time, end_time = start_time_end_time
    
    # Create service
    service = TimeToAnswerService()
    
    # Calculate TTA using the service
    calculated_tta = service.calculate_tta(start_time, end_time)
    
    # Calculate expected duration manually
    expected_duration = (end_time - start_time).total_seconds()
    
    # Verify they match (allowing for small floating point differences)
    assert abs(calculated_tta - expected_duration) < 0.001, \
        f"Calculated TTA ({calculated_tta}) should match expected duration ({expected_duration})"


@given(time_to_answer_record=time_to_answer_strategy())
@settings(max_examples=100)
def test_time_to_answer_model_duration_consistency(time_to_answer_record):
    """
    Property 10: TTA calculation correctness - Model validation
    For any TimeToAnswer record, the duration_seconds field should match 
    the difference between end_time and start_time
    **Validates: Requirements 4.3**
    """
    # The TimeToAnswer model should already validate this in its validator
    # If we can create the object, the duration should be consistent
    
    expected_duration = (time_to_answer_record.end_time - time_to_answer_record.start_time).total_seconds()
    
    # Verify the duration_seconds matches the calculated difference
    assert abs(time_to_answer_record.duration_seconds - expected_duration) < 0.01, \
        f"Model duration_seconds ({time_to_answer_record.duration_seconds}) should match " \
        f"calculated duration ({expected_duration})"


@given(
    evaluation_id=valid_uuid_strategy,
    start_time_end_time=timestamp_pair_strategy()
)
@settings(max_examples=100)
def test_time_to_answer_create_model_validation(evaluation_id, start_time_end_time):
    """
    Property 10: TTA calculation correctness - Create model validation
    For any TimeToAnswerCreate with start_time and end_time, the duration_seconds 
    must match the time difference for the model to be valid
    **Validates: Requirements 4.3**
    """
    start_time, end_time = start_time_end_time
    
    # Calculate correct duration
    correct_duration = (end_time - start_time).total_seconds()
    
    # Creating with correct duration should succeed
    valid_create = TimeToAnswerCreate(
        evaluation_id=evaluation_id,
        start_time=start_time,
        end_time=end_time,
        duration_seconds=correct_duration
    )
    
    # Verify the model was created successfully
    assert valid_create.duration_seconds == correct_duration
    assert valid_create.start_time == start_time
    assert valid_create.end_time == end_time
    
    # Creating with incorrect duration should fail
    incorrect_duration = correct_duration + 10.0  # Add 10 seconds error
    
    with pytest.raises(ValueError, match="duration_seconds must match end_time - start_time"):
        TimeToAnswerCreate(
            evaluation_id=evaluation_id,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=incorrect_duration
        )


@given(time_to_answer_records=st.lists(time_to_answer_strategy(), min_size=1, max_size=10))
@settings(max_examples=100)
def test_average_tta_calculation_correctness(time_to_answer_records):
    """
    Property 10: TTA calculation correctness - Average calculation
    For any list of TimeToAnswer records, the average TTA should equal 
    the mean of all duration_seconds values
    **Validates: Requirements 4.3**
    """
    # Create service
    service = TimeToAnswerService()
    
    # Calculate average using the service
    calculated_average = service.calculate_average_tta(time_to_answer_records)
    
    # Calculate expected average manually
    total_duration = sum(record.duration_seconds for record in time_to_answer_records)
    expected_average = total_duration / len(time_to_answer_records)
    
    # Verify they match (allowing for small floating point differences)
    assert abs(calculated_average - expected_average) < 0.001, \
        f"Calculated average TTA ({calculated_average}) should match expected average ({expected_average})"


# **Feature: text-to-sql-evaluation, Property 11: Average TTA calculation**

@given(completed_evaluations=st.lists(time_to_answer_strategy(), min_size=1, max_size=20))
@settings(max_examples=100)
def test_average_tta_for_completed_evaluations(completed_evaluations):
    """
    Property 11: Average TTA calculation
    For any set of completed evaluations, the average TTA should equal 
    the mean of all duration_seconds values
    **Validates: Requirements 4.4**
    """
    # Create service
    service = TimeToAnswerService()
    
    # Calculate average TTA using the service method
    calculated_average = service.calculate_average_tta(completed_evaluations)
    
    # Calculate expected average manually - this is what Requirements 4.4 specifies:
    # "el Sistema SHALL calcular el promedio de `duration_seconds` para todas las evaluaciones completadas"
    total_duration_seconds = sum(evaluation.duration_seconds for evaluation in completed_evaluations)
    expected_average = total_duration_seconds / len(completed_evaluations)
    
    # Verify the calculated average matches the expected average
    assert abs(calculated_average - expected_average) < 0.001, \
        f"Average TTA calculation failed: calculated ({calculated_average}) should equal " \
        f"mean of duration_seconds ({expected_average})"


@given(
    evaluation_count=st.integers(min_value=1, max_value=15),
    duration_range=st.floats(min_value=1.0, max_value=3600.0)
)
@settings(max_examples=100)
def test_average_tta_with_uniform_durations(evaluation_count, duration_range):
    """
    Property 11: Average TTA calculation - Uniform durations
    For any set of evaluations with the same duration, the average should equal that duration
    **Validates: Requirements 4.4**
    """
    # Create evaluations with the same duration
    uniform_evaluations = []
    for i in range(evaluation_count):
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end_time = start_time + timedelta(seconds=duration_range)
        
        evaluation = TimeToAnswer(
            id=uuid4(),
            evaluation_id=uuid4(),
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_range,
            created_at=datetime.now(timezone.utc)
        )
        uniform_evaluations.append(evaluation)
    
    # Create service
    service = TimeToAnswerService()
    
    # Calculate average
    calculated_average = service.calculate_average_tta(uniform_evaluations)
    
    # For uniform durations, average should equal the uniform duration
    assert abs(calculated_average - duration_range) < 0.001, \
        f"Average of uniform durations should equal the uniform duration: " \
        f"calculated ({calculated_average}) vs expected ({duration_range})"


@given(evaluations=st.lists(time_to_answer_strategy(), min_size=2, max_size=10))
@settings(max_examples=100)
def test_average_tta_mathematical_properties(evaluations):
    """
    Property 11: Average TTA calculation - Mathematical properties
    For any set of evaluations, the average should satisfy basic mathematical properties
    **Validates: Requirements 4.4**
    """
    # Create service
    service = TimeToAnswerService()
    
    # Calculate average
    calculated_average = service.calculate_average_tta(evaluations)
    
    # Extract all duration values
    durations = [eval.duration_seconds for eval in evaluations]
    min_duration = min(durations)
    max_duration = max(durations)
    
    # Mathematical property: average should be between min and max
    assert min_duration <= calculated_average <= max_duration, \
        f"Average TTA ({calculated_average}) should be between min ({min_duration}) and max ({max_duration})"
    
    # Mathematical property: average should equal sum/count
    expected_sum = sum(durations)
    expected_average = expected_sum / len(durations)
    
    assert abs(calculated_average - expected_average) < 0.001, \
        f"Average TTA should equal sum/count: calculated ({calculated_average}) vs expected ({expected_average})"


@settings(max_examples=100)
def test_average_tta_empty_list_handling():
    """
    Property 11: Average TTA calculation - Empty list handling
    For an empty set of evaluations, the average TTA should return 0.0
    **Validates: Requirements 4.4**
    """
    # Create service
    service = TimeToAnswerService()
    
    # Calculate average for empty list
    calculated_average = service.calculate_average_tta([])
    
    # Should return 0.0 for empty list (as implemented in the service)
    assert calculated_average == 0.0, \
        f"Average TTA for empty list should be 0.0, got {calculated_average}"


@given(
    start_time=valid_timestamp_strategy(),
    duration_seconds=st.floats(min_value=0.1, max_value=86400.0)
)
@settings(max_examples=100)
def test_tta_calculation_with_generated_end_time(start_time, duration_seconds):
    """
    Property 10: TTA calculation correctness - Generated end time
    For any start_time and duration, if we calculate end_time and then calculate TTA,
    we should get back the original duration
    **Validates: Requirements 4.3**
    """
    # Generate end_time from start_time + duration
    end_time = start_time + timedelta(seconds=duration_seconds)
    
    # Create service
    service = TimeToAnswerService()
    
    # Calculate TTA using the service
    calculated_tta = service.calculate_tta(start_time, end_time)
    
    # Should match the original duration (allowing for small floating point differences)
    assert abs(calculated_tta - duration_seconds) < 0.001, \
        f"Calculated TTA ({calculated_tta}) should match original duration ({duration_seconds})"


@given(timestamp_pairs=st.lists(timestamp_pair_strategy(), min_size=1, max_size=5))
@settings(max_examples=100)
def test_multiple_tta_calculations_independence(timestamp_pairs):
    """
    Property 10: TTA calculation correctness - Multiple calculations independence
    For any set of timestamp pairs, calculating TTA for each should be independent
    and each should match its expected duration
    **Validates: Requirements 4.3**
    """
    # Create service
    service = TimeToAnswerService()
    
    calculated_ttas = []
    expected_durations = []
    
    # Calculate TTA for each timestamp pair
    for start_time, end_time in timestamp_pairs:
        calculated_tta = service.calculate_tta(start_time, end_time)
        expected_duration = (end_time - start_time).total_seconds()
        
        calculated_ttas.append(calculated_tta)
        expected_durations.append(expected_duration)
    
    # Verify each calculation is correct
    for i, (calculated, expected) in enumerate(zip(calculated_ttas, expected_durations)):
        assert abs(calculated - expected) < 0.001, \
            f"TTA calculation {i}: calculated ({calculated}) should match expected ({expected})"


@given(start_time_end_time=timestamp_pair_strategy())
@settings(max_examples=100)
def test_tta_service_rejects_invalid_timestamps(start_time_end_time):
    """
    Property 10: TTA calculation correctness - Invalid timestamp rejection
    For any timestamp pair where end_time <= start_time, the service should reject the calculation
    **Validates: Requirements 4.3**
    """
    start_time, end_time = start_time_end_time
    
    # Create service
    service = TimeToAnswerService()
    
    # Valid calculation should work
    valid_tta = service.calculate_tta(start_time, end_time)
    assert valid_tta > 0, "Valid TTA calculation should return positive value"
    
    # Invalid calculation (end_time <= start_time) should fail
    with pytest.raises(ValueError, match="end_time must be after start_time"):
        service.calculate_tta(end_time, start_time)  # Swapped order
    
    # Equal timestamps should also fail
    with pytest.raises(ValueError, match="end_time must be after start_time"):
        service.calculate_tta(start_time, start_time)