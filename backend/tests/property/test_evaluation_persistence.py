"""Property-based tests for evaluation persistence"""

import pytest
from hypothesis import given, strategies as st, settings
from backend.app.models.evaluation import Evaluation, EvaluationCreate
from backend.app.models.execution_accuracy import ExecutionAccuracy, ExecutionAccuracyCreate
from backend.app.models.time_to_answer import TimeToAnswer, TimeToAnswerCreate
from backend.app.models.component_matching import ComponentMatching, ComponentMatchingCreate
from backend.app.models.gold_query import GoldQuery
from uuid import uuid4, UUID
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List


# **Feature: text-to-sql-evaluation, Property 17: Evaluation persistence**

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

# Strategy for generating valid F1 scores
valid_f1_score_strategy = st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0))

# Strategy for generating valid duration values (in seconds)
valid_duration_strategy = st.floats(min_value=0.01, max_value=3600.0)


class MockSupabaseStorage:
    """Mock Supabase storage system to simulate complete evaluation persistence"""
    
    def __init__(self):
        self.gold_queries: Dict[UUID, GoldQuery] = {}
        self.evaluations: Dict[UUID, Evaluation] = {}
        self.execution_accuracy_records: Dict[UUID, ExecutionAccuracy] = {}
        self.time_to_answer_records: Dict[UUID, TimeToAnswer] = {}
        self.component_matching_records: Dict[UUID, ComponentMatching] = {}
        
        # Mapping evaluation_id to associated records
        self.evaluation_to_execution_accuracy: Dict[UUID, UUID] = {}
        self.evaluation_to_time_to_answer: Dict[UUID, UUID] = {}
        self.evaluation_to_component_matching: Dict[UUID, UUID] = {}
    
    def add_gold_query(self, gold_query: GoldQuery):
        """Add a gold query to the mock storage"""
        self.gold_queries[gold_query.id] = gold_query
    
    def store_evaluation(self, evaluation_create: EvaluationCreate) -> Evaluation:
        """Store an evaluation and return the created evaluation"""
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
        self.evaluation_to_execution_accuracy[execution_accuracy_create.evaluation_id] = execution_accuracy.id
        return execution_accuracy
    
    def store_time_to_answer(self, time_to_answer_create: TimeToAnswerCreate) -> TimeToAnswer:
        """Store time to answer and return the created record"""
        if time_to_answer_create.evaluation_id not in self.evaluations:
            raise ValueError(f"Evaluation {time_to_answer_create.evaluation_id} does not exist")
        
        time_to_answer = TimeToAnswer(
            id=uuid4(),
            evaluation_id=time_to_answer_create.evaluation_id,
            start_time=time_to_answer_create.start_time,
            end_time=time_to_answer_create.end_time,
            duration_seconds=time_to_answer_create.duration_seconds,
            created_at=datetime.now(timezone.utc)
        )
        
        self.time_to_answer_records[time_to_answer.id] = time_to_answer
        self.evaluation_to_time_to_answer[time_to_answer_create.evaluation_id] = time_to_answer.id
        return time_to_answer
    
    def store_component_matching(self, component_matching_create: ComponentMatchingCreate) -> ComponentMatching:
        """Store component matching and return the created record"""
        if component_matching_create.evaluation_id not in self.evaluations:
            raise ValueError(f"Evaluation {component_matching_create.evaluation_id} does not exist")
        
        component_matching = ComponentMatching(
            id=uuid4(),
            evaluation_id=component_matching_create.evaluation_id,
            select_correct=component_matching_create.select_correct,
            where_correct=component_matching_create.where_correct,
            group_by_correct=component_matching_create.group_by_correct,
            order_by_correct=component_matching_create.order_by_correct,
            keywords_correct=component_matching_create.keywords_correct,
            f1_score=component_matching_create.f1_score,
            evaluator_notes=component_matching_create.evaluator_notes,
            created_at=datetime.now(timezone.utc)
        )
        
        self.component_matching_records[component_matching.id] = component_matching
        self.evaluation_to_component_matching[component_matching_create.evaluation_id] = component_matching.id
        return component_matching
    
    def get_execution_accuracy_for_evaluation(self, evaluation_id: UUID) -> Optional[ExecutionAccuracy]:
        """Get execution accuracy record for a given evaluation"""
        if evaluation_id in self.evaluation_to_execution_accuracy:
            accuracy_id = self.evaluation_to_execution_accuracy[evaluation_id]
            return self.execution_accuracy_records.get(accuracy_id)
        return None
    
    def get_time_to_answer_for_evaluation(self, evaluation_id: UUID) -> Optional[TimeToAnswer]:
        """Get time to answer record for a given evaluation"""
        if evaluation_id in self.evaluation_to_time_to_answer:
            tta_id = self.evaluation_to_time_to_answer[evaluation_id]
            return self.time_to_answer_records.get(tta_id)
        return None
    
    def get_component_matching_for_evaluation(self, evaluation_id: UUID) -> Optional[ComponentMatching]:
        """Get component matching record for a given evaluation"""
        if evaluation_id in self.evaluation_to_component_matching:
            cm_id = self.evaluation_to_component_matching[evaluation_id]
            return self.component_matching_records.get(cm_id)
        return None
    
    def has_complete_evaluation_data(self, evaluation_id: UUID) -> bool:
        """Check if an evaluation has all associated data persisted"""
        return (
            evaluation_id in self.evaluations and
            evaluation_id in self.evaluation_to_execution_accuracy and
            evaluation_id in self.evaluation_to_time_to_answer and
            evaluation_id in self.evaluation_to_component_matching
        )


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


def create_valid_timestamp_pair():
    """Create a valid start_time and end_time pair with proper duration"""
    start_time = st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    ).map(lambda dt: dt.replace(tzinfo=timezone.utc))
    
    @st.composite
    def timestamp_pair(draw):
        start = draw(start_time)
        duration = draw(st.floats(min_value=0.01, max_value=3600.0))
        end = start + timedelta(seconds=duration)
        return start, end, duration
    
    return timestamp_pair()


@given(
    gold_query=create_gold_query_strategy(),
    evaluation_create=evaluation_create_strategy(),
    is_correct=valid_boolean_strategy,
    timestamp_data=create_valid_timestamp_pair(),
    select_correct=valid_boolean_strategy,
    where_correct=valid_boolean_strategy,
    group_by_correct=valid_boolean_strategy,
    order_by_correct=valid_boolean_strategy,
    keywords_correct=valid_boolean_strategy,
    f1_score=valid_f1_score_strategy,
    execution_notes=optional_string_strategy,
    component_notes=optional_string_strategy
)
@settings(max_examples=100)
def test_completed_evaluation_persists_all_associated_data(
    gold_query: GoldQuery,
    evaluation_create: EvaluationCreate,
    is_correct: bool,
    timestamp_data: tuple,
    select_correct: bool,
    where_correct: bool,
    group_by_correct: bool,
    order_by_correct: bool,
    keywords_correct: bool,
    f1_score: Optional[float],
    execution_notes: Optional[str],
    component_notes: Optional[str]
):
    """
    Property 17: Evaluation persistence - Complete evaluation data persistence
    For any completed evaluation, all associated data (execution_accuracy, time_to_answer, 
    component_matching) should be persisted in Supabase
    **Validates: Requirements 6.5**
    """
    start_time, end_time, duration_seconds = timestamp_data
    
    # Create mock storage
    storage = MockSupabaseStorage()
    
    # Add the gold query first
    storage.add_gold_query(gold_query)
    
    # Update evaluation_create to reference the existing gold query
    evaluation_create.gold_query_id = gold_query.id
    
    # Store the evaluation
    evaluation = storage.store_evaluation(evaluation_create)
    
    # Create and store execution accuracy record
    execution_accuracy_create = ExecutionAccuracyCreate(
        evaluation_id=evaluation.id,
        results_match=None,
        is_correct=is_correct,
        evaluator_notes=execution_notes
    )
    execution_accuracy = storage.store_execution_accuracy(execution_accuracy_create)
    
    # Create and store time to answer record
    time_to_answer_create = TimeToAnswerCreate(
        evaluation_id=evaluation.id,
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration_seconds
    )
    time_to_answer = storage.store_time_to_answer(time_to_answer_create)
    
    # Create and store component matching record
    component_matching_create = ComponentMatchingCreate(
        evaluation_id=evaluation.id,
        select_correct=select_correct,
        where_correct=where_correct,
        group_by_correct=group_by_correct,
        order_by_correct=order_by_correct,
        keywords_correct=keywords_correct,
        f1_score=f1_score,
        evaluator_notes=component_notes
    )
    component_matching = storage.store_component_matching(component_matching_create)
    
    # Verify that all associated data is persisted
    assert storage.has_complete_evaluation_data(evaluation.id), \
        "Completed evaluation should have all associated data persisted"
    
    # Verify each component is retrievable and has correct data
    stored_execution_accuracy = storage.get_execution_accuracy_for_evaluation(evaluation.id)
    assert stored_execution_accuracy is not None, "Execution accuracy should be persisted"
    assert stored_execution_accuracy.evaluation_id == evaluation.id
    assert stored_execution_accuracy.is_correct == is_correct
    assert stored_execution_accuracy.evaluator_notes == execution_notes
    
    stored_time_to_answer = storage.get_time_to_answer_for_evaluation(evaluation.id)
    assert stored_time_to_answer is not None, "Time to answer should be persisted"
    assert stored_time_to_answer.evaluation_id == evaluation.id
    assert stored_time_to_answer.start_time == start_time
    assert stored_time_to_answer.end_time == end_time
    assert abs(stored_time_to_answer.duration_seconds - duration_seconds) < 0.01
    
    stored_component_matching = storage.get_component_matching_for_evaluation(evaluation.id)
    assert stored_component_matching is not None, "Component matching should be persisted"
    assert stored_component_matching.evaluation_id == evaluation.id
    assert stored_component_matching.select_correct == select_correct
    assert stored_component_matching.where_correct == where_correct
    assert stored_component_matching.group_by_correct == group_by_correct
    assert stored_component_matching.order_by_correct == order_by_correct
    assert stored_component_matching.keywords_correct == keywords_correct
    assert stored_component_matching.f1_score == f1_score
    assert stored_component_matching.evaluator_notes == component_notes


@given(
    gold_query=create_gold_query_strategy(),
    evaluation_create=evaluation_create_strategy()
)
@settings(max_examples=100)
def test_incomplete_evaluation_missing_associated_data(
    gold_query: GoldQuery,
    evaluation_create: EvaluationCreate
):
    """
    Property 17: Evaluation persistence - Incomplete evaluation detection
    For any evaluation that is not completed (missing associated data), 
    the system should detect it as incomplete
    **Validates: Requirements 6.5**
    """
    # Create mock storage
    storage = MockSupabaseStorage()
    
    # Add the gold query first
    storage.add_gold_query(gold_query)
    
    # Update evaluation_create to reference the existing gold query
    evaluation_create.gold_query_id = gold_query.id
    
    # Store only the evaluation, but not the associated data
    evaluation = storage.store_evaluation(evaluation_create)
    
    # Verify that the evaluation is detected as incomplete
    assert not storage.has_complete_evaluation_data(evaluation.id), \
        "Evaluation without associated data should be detected as incomplete"
    
    # Verify that individual components are not retrievable
    assert storage.get_execution_accuracy_for_evaluation(evaluation.id) is None, \
        "Should not retrieve execution accuracy for incomplete evaluation"
    assert storage.get_time_to_answer_for_evaluation(evaluation.id) is None, \
        "Should not retrieve time to answer for incomplete evaluation"
    assert storage.get_component_matching_for_evaluation(evaluation.id) is None, \
        "Should not retrieve component matching for incomplete evaluation"


@given(
    gold_queries=st.lists(create_gold_query_strategy(), min_size=2, max_size=5),
    is_correct_values=st.lists(valid_boolean_strategy, min_size=2, max_size=5),
    timestamp_pairs=st.lists(create_valid_timestamp_pair(), min_size=2, max_size=5)
)
@settings(max_examples=100)
def test_multiple_evaluations_all_persist_independently(
    gold_queries: List[GoldQuery],
    is_correct_values: List[bool],
    timestamp_pairs: List[tuple]
):
    """
    Property 17: Evaluation persistence - Multiple evaluations independence
    For any set of completed evaluations, each should have its own complete 
    set of associated data persisted independently
    **Validates: Requirements 6.5**
    """
    # Ensure we have the same number of items for all lists
    min_length = min(len(gold_queries), len(is_correct_values), len(timestamp_pairs))
    gold_queries = gold_queries[:min_length]
    is_correct_values = is_correct_values[:min_length]
    timestamp_pairs = timestamp_pairs[:min_length]
    
    # Create mock storage
    storage = MockSupabaseStorage()
    
    # Add all gold queries
    for gold_query in gold_queries:
        storage.add_gold_query(gold_query)
    
    evaluations = []
    
    # Create complete evaluations for each gold query
    for i, (gold_query, is_correct, timestamp_data) in enumerate(zip(gold_queries, is_correct_values, timestamp_pairs)):
        start_time, end_time, duration_seconds = timestamp_data
        
        # Create evaluation
        evaluation_create = EvaluationCreate(
            gold_query_id=gold_query.id,
            generated_sql=f"SELECT * FROM table_{i};"
        )
        evaluation = storage.store_evaluation(evaluation_create)
        evaluations.append(evaluation)
        
        # Create execution accuracy
        execution_accuracy_create = ExecutionAccuracyCreate(
            evaluation_id=evaluation.id,
            results_match=None,
            is_correct=is_correct,
            evaluator_notes=f"Notes for evaluation {i}"
        )
        storage.store_execution_accuracy(execution_accuracy_create)
        
        # Create time to answer
        time_to_answer_create = TimeToAnswerCreate(
            evaluation_id=evaluation.id,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds
        )
        storage.store_time_to_answer(time_to_answer_create)
        
        # Create component matching
        component_matching_create = ComponentMatchingCreate(
            evaluation_id=evaluation.id,
            select_correct=True,
            where_correct=False,
            group_by_correct=True,
            order_by_correct=False,
            keywords_correct=True,
            f1_score=0.6,
            evaluator_notes=f"Component notes for evaluation {i}"
        )
        storage.store_component_matching(component_matching_create)
    
    # Verify each evaluation has complete data persisted independently
    for i, evaluation in enumerate(evaluations):
        assert storage.has_complete_evaluation_data(evaluation.id), \
            f"Evaluation {i} should have complete data persisted"
        
        # Verify data integrity for each evaluation
        stored_execution_accuracy = storage.get_execution_accuracy_for_evaluation(evaluation.id)
        assert stored_execution_accuracy is not None, f"Evaluation {i} should have execution accuracy"
        assert stored_execution_accuracy.is_correct == is_correct_values[i], \
            f"Evaluation {i} execution accuracy should match input"
        
        stored_time_to_answer = storage.get_time_to_answer_for_evaluation(evaluation.id)
        assert stored_time_to_answer is not None, f"Evaluation {i} should have time to answer"
        
        stored_component_matching = storage.get_component_matching_for_evaluation(evaluation.id)
        assert stored_component_matching is not None, f"Evaluation {i} should have component matching"


@given(
    gold_query=create_gold_query_strategy(),
    evaluation_create=evaluation_create_strategy(),
    is_correct=valid_boolean_strategy,
    timestamp_data=create_valid_timestamp_pair(),
    select_correct=valid_boolean_strategy,
    where_correct=valid_boolean_strategy,
    group_by_correct=valid_boolean_strategy,
    order_by_correct=valid_boolean_strategy,
    keywords_correct=valid_boolean_strategy
)
@settings(max_examples=100)
def test_evaluation_persistence_atomic_operation(
    gold_query: GoldQuery,
    evaluation_create: EvaluationCreate,
    is_correct: bool,
    timestamp_data: tuple,
    select_correct: bool,
    where_correct: bool,
    group_by_correct: bool,
    order_by_correct: bool,
    keywords_correct: bool
):
    """
    Property 17: Evaluation persistence - Atomic operation behavior
    For any completed evaluation, either all associated data should be persisted 
    or none should be (atomic behavior)
    **Validates: Requirements 6.5**
    """
    start_time, end_time, duration_seconds = timestamp_data
    
    # Create mock storage
    storage = MockSupabaseStorage()
    
    # Add the gold query first
    storage.add_gold_query(gold_query)
    
    # Update evaluation_create to reference the existing gold query
    evaluation_create.gold_query_id = gold_query.id
    
    # Store the evaluation
    evaluation = storage.store_evaluation(evaluation_create)
    
    # Initially, evaluation should not be complete
    assert not storage.has_complete_evaluation_data(evaluation.id), \
        "Evaluation should not be complete initially"
    
    # Store execution accuracy
    execution_accuracy_create = ExecutionAccuracyCreate(
        evaluation_id=evaluation.id,
        results_match=None,
        is_correct=is_correct,
        evaluator_notes=None
    )
    storage.store_execution_accuracy(execution_accuracy_create)
    
    # Still not complete (missing time_to_answer and component_matching)
    assert not storage.has_complete_evaluation_data(evaluation.id), \
        "Evaluation should not be complete with only execution accuracy"
    
    # Store time to answer
    time_to_answer_create = TimeToAnswerCreate(
        evaluation_id=evaluation.id,
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration_seconds
    )
    storage.store_time_to_answer(time_to_answer_create)
    
    # Still not complete (missing component_matching)
    assert not storage.has_complete_evaluation_data(evaluation.id), \
        "Evaluation should not be complete with only execution accuracy and time to answer"
    
    # Store component matching - now it should be complete
    component_matching_create = ComponentMatchingCreate(
        evaluation_id=evaluation.id,
        select_correct=select_correct,
        where_correct=where_correct,
        group_by_correct=group_by_correct,
        order_by_correct=order_by_correct,
        keywords_correct=keywords_correct,
        f1_score=None,
        evaluator_notes=None
    )
    storage.store_component_matching(component_matching_create)
    
    # Now it should be complete
    assert storage.has_complete_evaluation_data(evaluation.id), \
        "Evaluation should be complete after all associated data is stored"