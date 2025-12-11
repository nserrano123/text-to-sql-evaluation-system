"""Property-based tests for notes round-trip functionality"""

import pytest
from hypothesis import given, strategies as st, settings
from backend.app.models.execution_accuracy import ExecutionAccuracy, ExecutionAccuracyCreate
from backend.app.models.component_matching import ComponentMatching, ComponentMatchingCreate
from backend.app.models.evaluation import Evaluation, EvaluationCreate
from backend.app.models.gold_query import GoldQuery
from uuid import uuid4, UUID
from datetime import datetime, timezone
from typing import Optional, Dict, Any


# **Feature: text-to-sql-evaluation, Property 8: Notes round-trip**

# Strategy for generating various text content including edge cases
notes_strategy = st.one_of(
    st.none(),  # No notes
    st.text(min_size=0, max_size=0),  # Empty string
    st.text(min_size=1, max_size=1000),  # Regular text
    st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Ps', 'Pe', 'Po', 'Sm', 'Sc', 'Sk', 'So', 'Zs')), min_size=1, max_size=500),  # Text with special characters
    st.just("This is a test note with special chars: áéíóú ñ ¿¡ @#$%^&*()"),  # Spanish characters
    st.just("Multi\nline\nnotes\nwith\nbreaks"),  # Multi-line text
    st.just("   Leading and trailing spaces   "),  # Whitespace handling
    st.just("SQL injection attempt: '; DROP TABLE users; --"),  # SQL-like content
    st.just("JSON-like content: {\"key\": \"value\", \"number\": 123}"),  # JSON-like content
)

# Strategy for generating valid UUIDs
valid_uuid_strategy = st.builds(uuid4)

# Strategy for generating valid timestamps
valid_timestamp_strategy = st.datetimes(
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2030, 12, 31)
).map(lambda dt: dt.replace(tzinfo=timezone.utc))

# Strategy for generating valid strings
valid_string_strategy = st.text(min_size=1, max_size=1000).filter(lambda x: x.strip())

# Strategy for generating valid boolean values
valid_boolean_strategy = st.booleans()


class MockNotesStorage:
    """Mock storage system to simulate notes persistence and retrieval"""
    
    def __init__(self):
        self.gold_queries: Dict[UUID, GoldQuery] = {}
        self.evaluations: Dict[UUID, Evaluation] = {}
        self.execution_accuracy_records: Dict[UUID, ExecutionAccuracy] = {}
        self.component_matching_records: Dict[UUID, ComponentMatching] = {}
    
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
    
    def store_execution_accuracy_with_notes(self, execution_accuracy_create: ExecutionAccuracyCreate) -> ExecutionAccuracy:
        """Store execution accuracy with notes and return the created record"""
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
        return execution_accuracy
    
    def store_component_matching_with_notes(self, component_matching_create: ComponentMatchingCreate) -> ComponentMatching:
        """Store component matching with notes and return the created record"""
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
        return component_matching
    
    def get_execution_accuracy(self, execution_accuracy_id: UUID) -> Optional[ExecutionAccuracy]:
        """Get execution accuracy record by ID"""
        return self.execution_accuracy_records.get(execution_accuracy_id)
    
    def get_component_matching(self, component_matching_id: UUID) -> Optional[ComponentMatching]:
        """Get component matching record by ID"""
        return self.component_matching_records.get(component_matching_id)


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


@given(
    gold_query=create_gold_query_strategy(),
    evaluation_create=evaluation_create_strategy(),
    evaluator_notes=notes_strategy
)
@settings(max_examples=100)
def test_execution_accuracy_notes_round_trip(
    gold_query: GoldQuery, evaluation_create: EvaluationCreate, evaluator_notes: Optional[str]
):
    """
    Property 8: Notes round-trip - Execution accuracy notes
    For any text stored in execution_accuracy.evaluator_notes, retrieving it should return 
    the exact same text
    **Validates: Requirements 3.4, 10.3**
    """
    # Create mock storage
    storage = MockNotesStorage()
    
    # Add the gold query first
    storage.add_gold_query(gold_query)
    
    # Update evaluation_create to reference the existing gold query
    evaluation_create.gold_query_id = gold_query.id
    
    # Store the evaluation
    evaluation = storage.store_evaluation(evaluation_create)
    
    # Create execution accuracy record with notes
    execution_accuracy_create = ExecutionAccuracyCreate(
        evaluation_id=evaluation.id,
        results_match=None,
        is_correct=True,  # Required field
        evaluator_notes=evaluator_notes
    )
    
    # Store the execution accuracy record with notes
    stored_execution_accuracy = storage.store_execution_accuracy_with_notes(execution_accuracy_create)
    
    # Retrieve the stored record
    retrieved_execution_accuracy = storage.get_execution_accuracy(stored_execution_accuracy.id)
    
    # Verify round-trip: stored notes should exactly match retrieved notes
    assert retrieved_execution_accuracy is not None, "Should be able to retrieve execution accuracy record"
    assert retrieved_execution_accuracy.evaluator_notes == evaluator_notes, \
        f"Notes round-trip failed: stored '{evaluator_notes}' but retrieved '{retrieved_execution_accuracy.evaluator_notes}'"
    
    # Additional verification: the notes should be exactly the same type and value
    if evaluator_notes is None:
        assert retrieved_execution_accuracy.evaluator_notes is None, "None notes should remain None"
    elif evaluator_notes == "":
        assert retrieved_execution_accuracy.evaluator_notes == "", "Empty string notes should remain empty string"
    else:
        assert isinstance(retrieved_execution_accuracy.evaluator_notes, str), "String notes should remain strings"
        assert retrieved_execution_accuracy.evaluator_notes == evaluator_notes, "String content should be identical"


@given(
    gold_query=create_gold_query_strategy(),
    evaluation_create=evaluation_create_strategy(),
    evaluator_notes=notes_strategy
)
@settings(max_examples=100)
def test_component_matching_notes_round_trip(
    gold_query: GoldQuery, evaluation_create: EvaluationCreate, evaluator_notes: Optional[str]
):
    """
    Property 8: Notes round-trip - Component matching notes
    For any text stored in component_matching.evaluator_notes, retrieving it should return 
    the exact same text
    **Validates: Requirements 5.5, 10.3**
    """
    # Create mock storage
    storage = MockNotesStorage()
    
    # Add the gold query first
    storage.add_gold_query(gold_query)
    
    # Update evaluation_create to reference the existing gold query
    evaluation_create.gold_query_id = gold_query.id
    
    # Store the evaluation
    evaluation = storage.store_evaluation(evaluation_create)
    
    # Create component matching record with notes
    component_matching_create = ComponentMatchingCreate(
        evaluation_id=evaluation.id,
        select_correct=True,
        where_correct=False,
        group_by_correct=True,
        order_by_correct=False,
        keywords_correct=True,
        f1_score=0.75,
        evaluator_notes=evaluator_notes
    )
    
    # Store the component matching record with notes
    stored_component_matching = storage.store_component_matching_with_notes(component_matching_create)
    
    # Retrieve the stored record
    retrieved_component_matching = storage.get_component_matching(stored_component_matching.id)
    
    # Verify round-trip: stored notes should exactly match retrieved notes
    assert retrieved_component_matching is not None, "Should be able to retrieve component matching record"
    assert retrieved_component_matching.evaluator_notes == evaluator_notes, \
        f"Notes round-trip failed: stored '{evaluator_notes}' but retrieved '{retrieved_component_matching.evaluator_notes}'"
    
    # Additional verification: the notes should be exactly the same type and value
    if evaluator_notes is None:
        assert retrieved_component_matching.evaluator_notes is None, "None notes should remain None"
    elif evaluator_notes == "":
        assert retrieved_component_matching.evaluator_notes == "", "Empty string notes should remain empty string"
    else:
        assert isinstance(retrieved_component_matching.evaluator_notes, str), "String notes should remain strings"
        assert retrieved_component_matching.evaluator_notes == evaluator_notes, "String content should be identical"


@given(
    gold_query=create_gold_query_strategy(),
    evaluation_create=evaluation_create_strategy(),
    execution_notes=notes_strategy,
    component_notes=notes_strategy
)
@settings(max_examples=100)
def test_both_notes_fields_round_trip_independently(
    gold_query: GoldQuery, evaluation_create: EvaluationCreate, 
    execution_notes: Optional[str], component_notes: Optional[str]
):
    """
    Property 8: Notes round-trip - Both notes fields independently
    For any evaluation with both execution accuracy and component matching notes, 
    each notes field should preserve its content independently
    **Validates: Requirements 3.4, 5.5, 10.3**
    """
    # Create mock storage
    storage = MockNotesStorage()
    
    # Add the gold query first
    storage.add_gold_query(gold_query)
    
    # Update evaluation_create to reference the existing gold query
    evaluation_create.gold_query_id = gold_query.id
    
    # Store the evaluation
    evaluation = storage.store_evaluation(evaluation_create)
    
    # Create execution accuracy record with its own notes
    execution_accuracy_create = ExecutionAccuracyCreate(
        evaluation_id=evaluation.id,
        results_match=True,
        is_correct=True,
        evaluator_notes=execution_notes
    )
    
    # Create component matching record with its own notes
    component_matching_create = ComponentMatchingCreate(
        evaluation_id=evaluation.id,
        select_correct=True,
        where_correct=True,
        group_by_correct=False,
        order_by_correct=False,
        keywords_correct=True,
        f1_score=0.6,
        evaluator_notes=component_notes
    )
    
    # Store both records
    stored_execution_accuracy = storage.store_execution_accuracy_with_notes(execution_accuracy_create)
    stored_component_matching = storage.store_component_matching_with_notes(component_matching_create)
    
    # Retrieve both records
    retrieved_execution_accuracy = storage.get_execution_accuracy(stored_execution_accuracy.id)
    retrieved_component_matching = storage.get_component_matching(stored_component_matching.id)
    
    # Verify both records exist
    assert retrieved_execution_accuracy is not None, "Should retrieve execution accuracy record"
    assert retrieved_component_matching is not None, "Should retrieve component matching record"
    
    # Verify execution accuracy notes round-trip
    assert retrieved_execution_accuracy.evaluator_notes == execution_notes, \
        f"Execution accuracy notes round-trip failed: stored '{execution_notes}' but retrieved '{retrieved_execution_accuracy.evaluator_notes}'"
    
    # Verify component matching notes round-trip
    assert retrieved_component_matching.evaluator_notes == component_notes, \
        f"Component matching notes round-trip failed: stored '{component_notes}' but retrieved '{retrieved_component_matching.evaluator_notes}'"
    
    # Verify independence: changing one shouldn't affect the other
    # (This is implicit in the separate storage, but we verify they're different records)
    assert retrieved_execution_accuracy.id != retrieved_component_matching.id, \
        "Execution accuracy and component matching should be separate records"
    
    # If the notes are different, verify they remain different
    if execution_notes != component_notes:
        assert retrieved_execution_accuracy.evaluator_notes != retrieved_component_matching.evaluator_notes, \
            "Different notes should remain different after storage and retrieval"


@given(
    notes_list=st.lists(notes_strategy, min_size=1, max_size=10)
)
@settings(max_examples=100)
def test_multiple_notes_round_trip_consistency(notes_list: list):
    """
    Property 8: Notes round-trip - Multiple notes consistency
    For any list of notes stored in multiple records, each should be retrievable 
    with its exact original content
    **Validates: Requirements 3.4, 5.5, 10.3**
    """
    # Create mock storage
    storage = MockNotesStorage()
    
    # Create a gold query for all evaluations
    gold_query = GoldQuery(
        id=uuid4(),
        chat_input="Test input",
        session_id=None,
        member_id=None,
        clasificacion=None,
        pregunta_descompuesta=None,
        tablas_columnas_ddl="CREATE TABLE test (id INT);",
        sql_reference="SELECT * FROM test;",
        created_at=datetime.now(timezone.utc)
    )
    storage.add_gold_query(gold_query)
    
    stored_records = []
    
    # Store multiple execution accuracy records with different notes
    for i, notes in enumerate(notes_list):
        # Create evaluation
        evaluation_create = EvaluationCreate(
            gold_query_id=gold_query.id,
            generated_sql=f"SELECT * FROM test WHERE id = {i};"
        )
        evaluation = storage.store_evaluation(evaluation_create)
        
        # Create execution accuracy with notes
        execution_accuracy_create = ExecutionAccuracyCreate(
            evaluation_id=evaluation.id,
            results_match=True,
            is_correct=True,
            evaluator_notes=notes
        )
        
        stored_record = storage.store_execution_accuracy_with_notes(execution_accuracy_create)
        stored_records.append((stored_record.id, notes))
    
    # Retrieve all records and verify notes round-trip
    for record_id, original_notes in stored_records:
        retrieved_record = storage.get_execution_accuracy(record_id)
        assert retrieved_record is not None, f"Should retrieve record {record_id}"
        assert retrieved_record.evaluator_notes == original_notes, \
            f"Notes round-trip failed for record {record_id}: stored '{original_notes}' but retrieved '{retrieved_record.evaluator_notes}'"
    
    # Verify that all notes are preserved independently
    retrieved_notes = []
    for record_id, _ in stored_records:
        retrieved_record = storage.get_execution_accuracy(record_id)
        retrieved_notes.append(retrieved_record.evaluator_notes)
    
    assert retrieved_notes == notes_list, \
        f"All notes should be preserved in order: expected {notes_list} but got {retrieved_notes}"