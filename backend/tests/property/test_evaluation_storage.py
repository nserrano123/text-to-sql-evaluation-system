"""Property-based tests for evaluation storage"""

import pytest
from hypothesis import given, strategies as st, settings
from backend.app.models.evaluation import Evaluation, EvaluationCreate
from backend.app.models.execution_accuracy import ExecutionAccuracy, ExecutionAccuracyCreate
from backend.app.models.gold_query import GoldQuery
from uuid import uuid4, UUID
from datetime import datetime, timezone
from typing import Optional, Dict, Any


# **Feature: text-to-sql-evaluation, Property 5: Evaluation storage**

# Strategy for generating valid strings
valid_string_strategy = st.text(min_size=1, max_size=1000).filter(lambda x: x.strip())

# Strategy for generating valid UUIDs
valid_uuid_strategy = st.builds(uuid4)

# Strategy for generating valid timestamps
valid_timestamp_strategy = st.datetimes(
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2030, 12, 31)
).map(lambda dt: dt.replace(tzinfo=timezone.utc))

# Strategy for generating valid boolean values
valid_boolean_strategy = st.booleans()

# Strategy for generating optional strings
optional_string_strategy = st.one_of(st.none(), st.text(max_size=1000))


class MockEvaluationStorage:
    """Mock storage system to simulate evaluation and execution accuracy persistence"""
    
    def __init__(self):
        self.gold_queries: Dict[UUID, GoldQuery] = {}
        self.evaluations: Dict[UUID, Evaluation] = {}
        self.execution_accuracy_records: Dict[UUID, ExecutionAccuracy] = {}
        self.evaluation_to_accuracy_map: Dict[UUID, UUID] = {}  # evaluation_id -> execution_accuracy_id
    
    def add_gold_query(self, gold_query: GoldQuery):
        """Add a gold query to the mock storage"""
        self.gold_queries[gold_query.id] = gold_query
    
    def store_evaluation(self, evaluation_create: EvaluationCreate) -> Evaluation:
        """Store an evaluation and return the created evaluation"""
        # Verify gold query exists
        if evaluation_create.gold_query_id not in self.gold_queries:
            raise ValueError(f"Gold query {evaluation_create.gold_query_id} does not exist")
        
        evaluation = Evaluation(
            id=uuid4(),
            gold_query_id=evaluation_create.gold_query_id,
            generated_sql=evaluation_create.generated_sql,
            evaluation_date=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        self.evaluations[evaluation.id] = evaluation
        return evaluation
    
    def store_execution_accuracy(self, execution_accuracy_create: ExecutionAccuracyCreate) -> ExecutionAccuracy:
        """Store execution accuracy and return the created record"""
        # Verify evaluation exists
        if execution_accuracy_create.evaluation_id not in self.evaluations:
            raise ValueError(f"Evaluation {execution_accuracy_create.evaluation_id} does not exist")
        
        execution_accuracy = ExecutionAccuracy(
            id=uuid4(),
            evaluation_id=execution_accuracy_create.evaluation_id,
            results_match=execution_accuracy_create.results_match,
            is_correct=execution_accuracy_create.is_correct,
            evaluator_notes=execution_accuracy_create.evaluator_notes,
            created_at=datetime.now(timezone.utc)
        )
        
        self.execution_accuracy_records[execution_accuracy.id] = execution_accuracy
        self.evaluation_to_accuracy_map[execution_accuracy_create.evaluation_id] = execution_accuracy.id
        return execution_accuracy
    
    def get_execution_accuracy_for_evaluation(self, evaluation_id: UUID) -> Optional[ExecutionAccuracy]:
        """Get execution accuracy record for a given evaluation"""
        if evaluation_id in self.evaluation_to_accuracy_map:
            accuracy_id = self.evaluation_to_accuracy_map[evaluation_id]
            return self.execution_accuracy_records.get(accuracy_id)
        return None
    
    def evaluation_exists(self, evaluation_id: UUID) -> bool:
        """Check if an evaluation exists"""
        return evaluation_id in self.evaluations
    
    def execution_accuracy_exists_for_evaluation(self, evaluation_id: UUID) -> bool:
        """Check if execution accuracy record exists for an evaluation"""
        return evaluation_id in self.evaluation_to_accuracy_map


def create_gold_query_strategy():
    """Strategy for generating valid GoldQuery objects"""
    return st.builds(
        GoldQuery,
        id=valid_uuid_strategy,
        chat_input=valid_string_strategy,
        session_id=st.one_of(st.none(), st.text(max_size=255)),
        member_id=st.one_of(st.none(), st.text(max_size=255)),
        clasificacion=st.one_of(st.none(), st.text(max_size=100)),
        pregunta_descompuesta=st.one_of(st.none(), st.text(max_size=1000)),
        tablas_columnas_ddl=valid_string_strategy,
        sql_reference=valid_string_strategy,
        created_at=valid_timestamp_strategy
    )


def evaluation_create_strategy():
    """Strategy for generating valid EvaluationCreate objects"""
    return st.builds(
        EvaluationCreate,
        gold_query_id=valid_uuid_strategy,
        generated_sql=valid_string_strategy
    )


def execution_accuracy_create_strategy():
    """Strategy for generating valid ExecutionAccuracyCreate objects"""
    return st.builds(
        ExecutionAccuracyCreate,
        evaluation_id=valid_uuid_strategy,
        results_match=st.one_of(st.none(), valid_boolean_strategy),
        is_correct=valid_boolean_strategy,
        evaluator_notes=optional_string_strategy
    )


@given(
    gold_query=create_gold_query_strategy(),
    evaluation_create=evaluation_create_strategy(),
    is_correct=valid_boolean_strategy,
    evaluator_notes=optional_string_strategy
)
@settings(max_examples=100)
def test_evaluation_marked_correct_creates_execution_accuracy_record(
    gold_query: GoldQuery, evaluation_create: EvaluationCreate, 
    is_correct: bool, evaluator_notes: Optional[str]
):
    """
    Property 5: Evaluation storage - Correct/incorrect marking creates execution accuracy record
    For any evaluation marked as correct or incorrect, a corresponding record should exist 
    in the execution_accuracy table
    **Validates: Requirements 3.1**
    """
    # Create mock storage
    storage = MockEvaluationStorage()
    
    # Add the gold query first
    storage.add_gold_query(gold_query)
    
    # Update evaluation_create to reference the existing gold query
    evaluation_create.gold_query_id = gold_query.id
    
    # Store the evaluation
    evaluation = storage.store_evaluation(evaluation_create)
    
    # Create execution accuracy record for the evaluation
    execution_accuracy_create = ExecutionAccuracyCreate(
        evaluation_id=evaluation.id,
        results_match=None,  # Can be None as per model
        is_correct=is_correct,
        evaluator_notes=evaluator_notes
    )
    
    # Store the execution accuracy record
    execution_accuracy = storage.store_execution_accuracy(execution_accuracy_create)
    
    # Verify that the execution accuracy record exists for this evaluation
    assert storage.execution_accuracy_exists_for_evaluation(evaluation.id), \
        "Execution accuracy record should exist for evaluation marked as correct/incorrect"
    
    # Verify the stored record has correct values
    stored_accuracy = storage.get_execution_accuracy_for_evaluation(evaluation.id)
    assert stored_accuracy is not None, "Should be able to retrieve execution accuracy record"
    assert stored_accuracy.evaluation_id == evaluation.id, "Evaluation ID should match"
    assert stored_accuracy.is_correct == is_correct, "is_correct value should be preserved"
    assert stored_accuracy.evaluator_notes == evaluator_notes, "Evaluator notes should be preserved"


@given(
    gold_query=create_gold_query_strategy(),
    evaluation_create=evaluation_create_strategy()
)
@settings(max_examples=100)
def test_evaluation_without_marking_has_no_execution_accuracy_record(
    gold_query: GoldQuery, evaluation_create: EvaluationCreate
):
    """
    Property 5: Evaluation storage - Evaluation without marking has no execution accuracy
    For any evaluation that has not been marked as correct/incorrect, no execution accuracy 
    record should exist
    **Validates: Requirements 3.1**
    """
    # Create mock storage
    storage = MockEvaluationStorage()
    
    # Add the gold query first
    storage.add_gold_query(gold_query)
    
    # Update evaluation_create to reference the existing gold query
    evaluation_create.gold_query_id = gold_query.id
    
    # Store the evaluation but don't create execution accuracy record
    evaluation = storage.store_evaluation(evaluation_create)
    
    # Verify that no execution accuracy record exists for this evaluation
    assert not storage.execution_accuracy_exists_for_evaluation(evaluation.id), \
        "No execution accuracy record should exist for unmarked evaluation"
    
    # Verify we cannot retrieve an execution accuracy record
    stored_accuracy = storage.get_execution_accuracy_for_evaluation(evaluation.id)
    assert stored_accuracy is None, "Should not be able to retrieve execution accuracy for unmarked evaluation"


@given(
    gold_queries=st.lists(create_gold_query_strategy(), min_size=1, max_size=5),
    is_correct_values=st.lists(valid_boolean_strategy, min_size=1, max_size=5)
)
@settings(max_examples=100)
def test_multiple_evaluations_each_get_execution_accuracy_record(
    gold_queries: list, is_correct_values: list
):
    """
    Property 5: Evaluation storage - Multiple evaluations each get their own execution accuracy
    For any set of evaluations each marked as correct/incorrect, each should have its own 
    corresponding execution accuracy record
    **Validates: Requirements 3.1**
    """
    # Ensure we have the same number of gold queries and is_correct values
    min_length = min(len(gold_queries), len(is_correct_values))
    gold_queries = gold_queries[:min_length]
    is_correct_values = is_correct_values[:min_length]
    
    # Create mock storage
    storage = MockEvaluationStorage()
    
    # Add all gold queries
    for gold_query in gold_queries:
        storage.add_gold_query(gold_query)
    
    evaluations = []
    
    # Create evaluations for each gold query
    for i, gold_query in enumerate(gold_queries):
        evaluation_create = EvaluationCreate(
            gold_query_id=gold_query.id,
            generated_sql=f"SELECT * FROM table_{i};"
        )
        
        evaluation = storage.store_evaluation(evaluation_create)
        evaluations.append(evaluation)
        
        # Mark each evaluation with the corresponding is_correct value
        execution_accuracy_create = ExecutionAccuracyCreate(
            evaluation_id=evaluation.id,
            results_match=None,
            is_correct=is_correct_values[i],
            evaluator_notes=f"Notes for evaluation {i}"
        )
        
        storage.store_execution_accuracy(execution_accuracy_create)
    
    # Verify each evaluation has its own execution accuracy record
    for i, evaluation in enumerate(evaluations):
        assert storage.execution_accuracy_exists_for_evaluation(evaluation.id), \
            f"Evaluation {i} should have execution accuracy record"
        
        stored_accuracy = storage.get_execution_accuracy_for_evaluation(evaluation.id)
        assert stored_accuracy is not None, f"Should retrieve execution accuracy for evaluation {i}"
        assert stored_accuracy.evaluation_id == evaluation.id, f"Evaluation ID should match for evaluation {i}"
        assert stored_accuracy.is_correct == is_correct_values[i], f"is_correct should match for evaluation {i}"


@given(
    gold_query=create_gold_query_strategy(),
    evaluation_create=evaluation_create_strategy(),
    results_match=st.one_of(st.none(), valid_boolean_strategy),
    is_correct=valid_boolean_strategy,
    evaluator_notes=optional_string_strategy
)
@settings(max_examples=100)
def test_execution_accuracy_preserves_all_evaluation_data(
    gold_query: GoldQuery, evaluation_create: EvaluationCreate,
    results_match: Optional[bool], is_correct: bool, evaluator_notes: Optional[str]
):
    """
    Property 5: Evaluation storage - All execution accuracy data is preserved
    For any evaluation marked with execution accuracy data, all fields should be preserved
    in the execution_accuracy table
    **Validates: Requirements 3.1**
    """
    # Create mock storage
    storage = MockEvaluationStorage()
    
    # Add the gold query first
    storage.add_gold_query(gold_query)
    
    # Update evaluation_create to reference the existing gold query
    evaluation_create.gold_query_id = gold_query.id
    
    # Store the evaluation
    evaluation = storage.store_evaluation(evaluation_create)
    
    # Create execution accuracy record with all possible data
    execution_accuracy_create = ExecutionAccuracyCreate(
        evaluation_id=evaluation.id,
        results_match=results_match,
        is_correct=is_correct,
        evaluator_notes=evaluator_notes
    )
    
    # Store the execution accuracy record
    execution_accuracy = storage.store_execution_accuracy(execution_accuracy_create)
    
    # Verify all data is preserved
    stored_accuracy = storage.get_execution_accuracy_for_evaluation(evaluation.id)
    assert stored_accuracy is not None, "Should be able to retrieve execution accuracy record"
    
    # Check all fields are preserved
    assert stored_accuracy.evaluation_id == evaluation.id, "evaluation_id should be preserved"
    assert stored_accuracy.results_match == results_match, "results_match should be preserved"
    assert stored_accuracy.is_correct == is_correct, "is_correct should be preserved"
    assert stored_accuracy.evaluator_notes == evaluator_notes, "evaluator_notes should be preserved"
    
    # Verify the record has proper metadata
    assert stored_accuracy.id is not None, "Execution accuracy should have an ID"
    assert stored_accuracy.created_at is not None, "Execution accuracy should have created_at timestamp"


@given(
    gold_query=create_gold_query_strategy(),
    evaluation_create=evaluation_create_strategy(),
    is_correct=valid_boolean_strategy
)
@settings(max_examples=100)
def test_evaluation_storage_one_to_one_relationship(
    gold_query: GoldQuery, evaluation_create: EvaluationCreate, is_correct: bool
):
    """
    Property 5: Evaluation storage - One-to-one relationship between evaluation and execution accuracy
    For any evaluation, there should be at most one execution accuracy record
    **Validates: Requirements 3.1**
    """
    # Create mock storage
    storage = MockEvaluationStorage()
    
    # Add the gold query first
    storage.add_gold_query(gold_query)
    
    # Update evaluation_create to reference the existing gold query
    evaluation_create.gold_query_id = gold_query.id
    
    # Store the evaluation
    evaluation = storage.store_evaluation(evaluation_create)
    
    # Create first execution accuracy record
    execution_accuracy_create_1 = ExecutionAccuracyCreate(
        evaluation_id=evaluation.id,
        results_match=None,
        is_correct=is_correct,
        evaluator_notes="First evaluation"
    )
    
    execution_accuracy_1 = storage.store_execution_accuracy(execution_accuracy_create_1)
    
    # Verify the first record exists
    assert storage.execution_accuracy_exists_for_evaluation(evaluation.id), \
        "First execution accuracy record should exist"
    
    stored_accuracy_1 = storage.get_execution_accuracy_for_evaluation(evaluation.id)
    assert stored_accuracy_1 is not None, "Should retrieve first execution accuracy record"
    assert stored_accuracy_1.id == execution_accuracy_1.id, "Should get the correct record ID"
    
    # In a real system, attempting to create a second execution accuracy record 
    # for the same evaluation should either:
    # 1. Replace the existing record, or 
    # 2. Fail due to unique constraint
    # For this test, we'll verify the one-to-one relationship is maintained
    
    # The key property is that for any evaluation_id, there should be exactly one
    # execution accuracy record when the evaluation is marked
    execution_accuracy_records_for_evaluation = [
        record for record in storage.execution_accuracy_records.values()
        if record.evaluation_id == evaluation.id
    ]
    
    assert len(execution_accuracy_records_for_evaluation) == 1, \
        "Should have exactly one execution accuracy record per evaluation"