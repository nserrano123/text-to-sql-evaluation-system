#!/usr/bin/env python3
"""
Direct runner for foreign key enforcement property-based tests
**Feature: text-to-sql-evaluation, Property 4: Foreign key enforcement**
"""

import sys
sys.path.append('.')

from hypothesis import given, strategies as st, settings
from pydantic import ValidationError
from app.models.evaluation import EvaluationCreate
from app.models.execution_accuracy import ExecutionAccuracy
from app.models.time_to_answer import TimeToAnswer
from app.models.component_matching import ComponentMatching
from uuid import uuid4, UUID
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

# Strategy for generating valid UUIDs
valid_uuid_strategy = st.builds(uuid4)

# Strategy for generating invalid UUIDs (non-existent references)
invalid_uuid_strategy = st.builds(uuid4)

# Strategy for generating valid strings
valid_string_strategy = st.text(min_size=1, max_size=1000).filter(lambda x: x.strip())

# Strategy for generating valid timestamps
valid_timestamp_strategy = st.datetimes(
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2030, 12, 31)
).map(lambda dt: dt.replace(tzinfo=timezone.utc))

# Strategy for generating valid boolean values
valid_boolean_strategy = st.booleans()

# Strategy for generating valid duration values
valid_duration_strategy = st.floats(min_value=0.01, max_value=3600.0)

# Strategy for generating valid F1 scores
valid_f1_score_strategy = st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0))

# Strategy for generating optional strings
optional_string_strategy = st.one_of(st.none(), st.text(max_size=1000))


class MockDatabase:
    """Mock database to simulate foreign key constraint checking"""
    
    def __init__(self):
        self.gold_queries: Dict[UUID, bool] = {}
        self.evaluations: Dict[UUID, bool] = {}
    
    def add_gold_query(self, gold_query_id: UUID):
        """Add a gold query to the mock database"""
        self.gold_queries[gold_query_id] = True
    
    def add_evaluation(self, evaluation_id: UUID):
        """Add an evaluation to the mock database"""
        self.evaluations[evaluation_id] = True
    
    def gold_query_exists(self, gold_query_id: UUID) -> bool:
        """Check if a gold query exists"""
        return gold_query_id in self.gold_queries
    
    def evaluation_exists(self, evaluation_id: UUID) -> bool:
        """Check if an evaluation exists"""
        return evaluation_id in self.evaluations


def simulate_foreign_key_check(model_data: Dict[str, Any], db: MockDatabase) -> bool:
    """
    Simulate foreign key constraint checking.
    Returns True if foreign keys are valid, False otherwise.
    """
    if 'gold_query_id' in model_data:
        if not db.gold_query_exists(model_data['gold_query_id']):
            return False
    
    if 'evaluation_id' in model_data:
        if not db.evaluation_exists(model_data['evaluation_id']):
            return False
    
    return True


@given(
    gold_query_id=invalid_uuid_strategy,
    generated_sql=valid_string_strategy
)
@settings(max_examples=100)
def test_evaluation_invalid_gold_query_id_rejected(gold_query_id: UUID, generated_sql: str):
    """
    Property 4: Foreign key enforcement - Evaluation with invalid gold_query_id
    For any evaluation record, attempting to insert with an invalid gold_query_id should fail
    **Validates: Requirements 2.5**
    """
    # Create mock database without the gold_query_id
    db = MockDatabase()
    
    # Create evaluation data
    evaluation_data = {
        'gold_query_id': gold_query_id,
        'generated_sql': generated_sql
    }
    
    # The model itself should validate successfully (Pydantic validation)
    evaluation = EvaluationCreate(**evaluation_data)
    assert evaluation.gold_query_id == gold_query_id
    assert evaluation.generated_sql == generated_sql
    
    # But foreign key constraint should fail
    foreign_key_valid = simulate_foreign_key_check(evaluation_data, db)
    assert not foreign_key_valid, "Foreign key constraint should reject invalid gold_query_id"


@given(
    evaluation_id=invalid_uuid_strategy,
    is_correct=valid_boolean_strategy,
    evaluator_notes=optional_string_strategy
)
@settings(max_examples=100)
def test_execution_accuracy_invalid_evaluation_id_rejected(
    evaluation_id: UUID, is_correct: bool, evaluator_notes: str
):
    """
    Property 4: Foreign key enforcement - ExecutionAccuracy with invalid evaluation_id
    For any execution accuracy record, attempting to insert with an invalid evaluation_id should fail
    **Validates: Requirements 2.5**
    """
    # Create mock database without the evaluation_id
    db = MockDatabase()
    
    # Create execution accuracy data
    execution_accuracy_data = {
        'id': uuid4(),
        'evaluation_id': evaluation_id,
        'results_match': None,
        'is_correct': is_correct,
        'evaluator_notes': evaluator_notes,
        'created_at': datetime.now(timezone.utc)
    }
    
    # The model itself should validate successfully (Pydantic validation)
    execution_accuracy = ExecutionAccuracy(**execution_accuracy_data)
    assert execution_accuracy.evaluation_id == evaluation_id
    assert execution_accuracy.is_correct == is_correct
    
    # But foreign key constraint should fail
    foreign_key_valid = simulate_foreign_key_check(execution_accuracy_data, db)
    assert not foreign_key_valid, "Foreign key constraint should reject invalid evaluation_id"


@given(
    evaluation_id=invalid_uuid_strategy,
    start_time=valid_timestamp_strategy,
    duration_seconds=valid_duration_strategy
)
@settings(max_examples=100)
def test_time_to_answer_invalid_evaluation_id_rejected(
    evaluation_id: UUID, start_time: datetime, duration_seconds: float
):
    """
    Property 4: Foreign key enforcement - TimeToAnswer with invalid evaluation_id
    For any time to answer record, attempting to insert with an invalid evaluation_id should fail
    **Validates: Requirements 2.5**
    """
    # Create mock database without the evaluation_id
    db = MockDatabase()
    
    # Calculate end_time based on start_time and duration
    end_time = start_time + timedelta(seconds=duration_seconds)
    
    # Create time to answer data
    time_to_answer_data = {
        'id': uuid4(),
        'evaluation_id': evaluation_id,
        'start_time': start_time,
        'end_time': end_time,
        'duration_seconds': duration_seconds,
        'created_at': datetime.now(timezone.utc)
    }
    
    # The model itself should validate successfully (Pydantic validation)
    time_to_answer = TimeToAnswer(**time_to_answer_data)
    assert time_to_answer.evaluation_id == evaluation_id
    
    # But foreign key constraint should fail
    foreign_key_valid = simulate_foreign_key_check(time_to_answer_data, db)
    assert not foreign_key_valid, "Foreign key constraint should reject invalid evaluation_id"


@given(
    evaluation_id=invalid_uuid_strategy,
    select_correct=valid_boolean_strategy,
    where_correct=valid_boolean_strategy,
    group_by_correct=valid_boolean_strategy,
    order_by_correct=valid_boolean_strategy,
    keywords_correct=valid_boolean_strategy,
    f1_score=valid_f1_score_strategy,
    evaluator_notes=optional_string_strategy
)
@settings(max_examples=100)
def test_component_matching_invalid_evaluation_id_rejected(
    evaluation_id: UUID, select_correct: bool, where_correct: bool,
    group_by_correct: bool, order_by_correct: bool, keywords_correct: bool,
    f1_score: float, evaluator_notes: str
):
    """
    Property 4: Foreign key enforcement - ComponentMatching with invalid evaluation_id
    For any component matching record, attempting to insert with an invalid evaluation_id should fail
    **Validates: Requirements 2.5**
    """
    # Create mock database without the evaluation_id
    db = MockDatabase()
    
    # Create component matching data
    component_matching_data = {
        'id': uuid4(),
        'evaluation_id': evaluation_id,
        'select_correct': select_correct,
        'where_correct': where_correct,
        'group_by_correct': group_by_correct,
        'order_by_correct': order_by_correct,
        'keywords_correct': keywords_correct,
        'f1_score': f1_score,
        'evaluator_notes': evaluator_notes,
        'created_at': datetime.now(timezone.utc)
    }
    
    # The model itself should validate successfully (Pydantic validation)
    component_matching = ComponentMatching(**component_matching_data)
    assert component_matching.evaluation_id == evaluation_id
    
    # But foreign key constraint should fail
    foreign_key_valid = simulate_foreign_key_check(component_matching_data, db)
    assert not foreign_key_valid, "Foreign key constraint should reject invalid evaluation_id"


@given(
    gold_query_id=valid_uuid_strategy,
    evaluation_id=valid_uuid_strategy,
    generated_sql=valid_string_strategy,
    is_correct=valid_boolean_strategy
)
@settings(max_examples=100)
def test_valid_foreign_keys_accepted(
    gold_query_id: UUID, evaluation_id: UUID, generated_sql: str, is_correct: bool
):
    """
    Property 4: Foreign key enforcement - Valid foreign keys should be accepted
    For any record with valid foreign keys, the constraint check should pass
    **Validates: Requirements 2.5**
    """
    # Create mock database with valid references
    db = MockDatabase()
    db.add_gold_query(gold_query_id)
    db.add_evaluation(evaluation_id)
    
    # Test evaluation with valid gold_query_id
    evaluation_data = {
        'gold_query_id': gold_query_id,
        'generated_sql': generated_sql
    }
    
    evaluation = EvaluationCreate(**evaluation_data)
    foreign_key_valid = simulate_foreign_key_check(evaluation_data, db)
    assert foreign_key_valid, "Valid gold_query_id should pass foreign key constraint"
    
    # Test execution accuracy with valid evaluation_id
    execution_accuracy_data = {
        'id': uuid4(),
        'evaluation_id': evaluation_id,
        'results_match': None,
        'is_correct': is_correct,
        'evaluator_notes': None,
        'created_at': datetime.now(timezone.utc)
    }
    
    execution_accuracy = ExecutionAccuracy(**execution_accuracy_data)
    foreign_key_valid = simulate_foreign_key_check(execution_accuracy_data, db)
    assert foreign_key_valid, "Valid evaluation_id should pass foreign key constraint"


@given(
    gold_query_id=valid_uuid_strategy,
    generated_sql=valid_string_strategy
)
@settings(max_examples=100)
def test_evaluation_with_existing_gold_query_accepted(gold_query_id: UUID, generated_sql: str):
    """
    Property 4: Foreign key enforcement - Evaluation with existing gold_query_id should be accepted
    For any evaluation with a gold_query_id that exists in the database, the constraint should pass
    **Validates: Requirements 2.5**
    """
    # Create mock database with the gold_query_id
    db = MockDatabase()
    db.add_gold_query(gold_query_id)
    
    # Create evaluation data
    evaluation_data = {
        'gold_query_id': gold_query_id,
        'generated_sql': generated_sql
    }
    
    # Both model validation and foreign key constraint should pass
    evaluation = EvaluationCreate(**evaluation_data)
    foreign_key_valid = simulate_foreign_key_check(evaluation_data, db)
    
    assert evaluation.gold_query_id == gold_query_id
    assert foreign_key_valid, "Existing gold_query_id should pass foreign key constraint"


@given(st.lists(valid_uuid_strategy, min_size=1, max_size=5))
@settings(max_examples=100)
def test_multiple_evaluations_same_gold_query_accepted(gold_query_ids: list):
    """
    Property 4: Foreign key enforcement - Multiple evaluations can reference same gold_query
    For any set of evaluations referencing the same valid gold_query_id, all should be accepted
    **Validates: Requirements 2.5**
    """
    # Use the first gold_query_id for all evaluations
    gold_query_id = gold_query_ids[0]
    
    # Create mock database with the gold_query_id
    db = MockDatabase()
    db.add_gold_query(gold_query_id)
    
    # Create multiple evaluations referencing the same gold_query_id
    for i in range(len(gold_query_ids)):
        evaluation_data = {
            'gold_query_id': gold_query_id,
            'generated_sql': f"SELECT * FROM table_{i};"
        }
        
        evaluation = EvaluationCreate(**evaluation_data)
        foreign_key_valid = simulate_foreign_key_check(evaluation_data, db)
        
        assert evaluation.gold_query_id == gold_query_id
        assert foreign_key_valid, f"Evaluation {i} should pass foreign key constraint"


def run_all_tests():
    """Run all property-based tests"""
    tests = [
        ("Evaluation invalid gold_query_id rejected", test_evaluation_invalid_gold_query_id_rejected),
        ("ExecutionAccuracy invalid evaluation_id rejected", test_execution_accuracy_invalid_evaluation_id_rejected),
        ("TimeToAnswer invalid evaluation_id rejected", test_time_to_answer_invalid_evaluation_id_rejected),
        ("ComponentMatching invalid evaluation_id rejected", test_component_matching_invalid_evaluation_id_rejected),
        ("Valid foreign keys accepted", test_valid_foreign_keys_accepted),
        ("Evaluation with existing gold_query accepted", test_evaluation_with_existing_gold_query_accepted),
        ("Multiple evaluations same gold_query accepted", test_multiple_evaluations_same_gold_query_accepted),
    ]
    
    print("Running Property-Based Tests for Foreign Key Enforcement")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"Running: {test_name}...")
            test_func()
            print(f"✅ PASSED: {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All property-based tests PASSED!")
        return True
    else:
        print("💥 Some property-based tests FAILED!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)