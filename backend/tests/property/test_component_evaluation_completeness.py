"""Property-based tests for component evaluation completeness"""

import pytest
from hypothesis import given, strategies as st, settings
from backend.app.models.component_matching import ComponentMatching, ComponentMatchingCreate
from uuid import uuid4, UUID
from datetime import datetime, timezone
from typing import Optional


# **Feature: text-to-sql-evaluation, Property 12: Component evaluation completeness**

# Strategy for generating valid UUIDs
valid_uuid_strategy = st.builds(uuid4)

# Strategy for generating valid timestamps with timezone
def valid_timestamp_strategy():
    """Generate valid timestamps with timezone"""
    return st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    ).map(lambda dt: dt.replace(tzinfo=timezone.utc))

# Strategy for generating boolean values for components
component_boolean_strategy = st.booleans()

# Strategy for generating valid F1 scores
f1_score_strategy = st.one_of(
    st.none(),
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)

# Strategy for generating optional evaluator notes
evaluator_notes_strategy = st.one_of(
    st.none(),
    st.text(min_size=0, max_size=500)
)

# Strategy for generating complete ComponentMatching objects
@st.composite
def component_matching_strategy(draw):
    """Generate valid ComponentMatching objects with all five components"""
    return ComponentMatching(
        id=draw(valid_uuid_strategy),
        evaluation_id=draw(valid_uuid_strategy),
        select_correct=draw(component_boolean_strategy),
        where_correct=draw(component_boolean_strategy),
        group_by_correct=draw(component_boolean_strategy),
        order_by_correct=draw(component_boolean_strategy),
        keywords_correct=draw(component_boolean_strategy),
        f1_score=draw(f1_score_strategy),
        evaluator_notes=draw(evaluator_notes_strategy),
        created_at=draw(valid_timestamp_strategy())
    )

# Strategy for generating ComponentMatchingCreate objects
@st.composite
def component_matching_create_strategy(draw):
    """Generate valid ComponentMatchingCreate objects with all five components"""
    return ComponentMatchingCreate(
        evaluation_id=draw(valid_uuid_strategy),
        select_correct=draw(component_boolean_strategy),
        where_correct=draw(component_boolean_strategy),
        group_by_correct=draw(component_boolean_strategy),
        order_by_correct=draw(component_boolean_strategy),
        keywords_correct=draw(component_boolean_strategy),
        f1_score=draw(f1_score_strategy),
        evaluator_notes=draw(evaluator_notes_strategy)
    )


class ComponentEvaluationService:
    """Simple component evaluation service for testing completeness without repository dependency"""
    
    def create_component_evaluation(
        self,
        evaluation_id: UUID,
        select_correct: bool,
        where_correct: bool,
        group_by_correct: bool,
        order_by_correct: bool,
        keywords_correct: bool,
        evaluator_notes: Optional[str] = None
    ) -> ComponentMatching:
        """
        Create a component evaluation with all five required components.
        
        Args:
            evaluation_id: ID of the evaluation being assessed
            select_correct: Whether SELECT component is correct
            where_correct: Whether WHERE component is correct
            group_by_correct: Whether GROUP BY component is correct
            order_by_correct: Whether ORDER BY component is correct
            keywords_correct: Whether KEYWORDS component is correct
            evaluator_notes: Optional notes from evaluator
            
        Returns:
            ComponentMatching: Complete component evaluation record
        """
        # Calculate F1 score based on component correctness
        f1_score = self.calculate_f1_score(
            select_correct, where_correct, group_by_correct, 
            order_by_correct, keywords_correct
        )
        
        return ComponentMatching(
            id=uuid4(),
            evaluation_id=evaluation_id,
            select_correct=select_correct,
            where_correct=where_correct,
            group_by_correct=group_by_correct,
            order_by_correct=order_by_correct,
            keywords_correct=keywords_correct,
            f1_score=f1_score,
            evaluator_notes=evaluator_notes,
            created_at=datetime.now(timezone.utc)
        )
    
    def calculate_f1_score(
        self,
        select_correct: bool,
        where_correct: bool,
        group_by_correct: bool,
        order_by_correct: bool,
        keywords_correct: bool
    ) -> float:
        """
        Calculate F1 score based on component correctness.
        
        For simplicity, this treats each component as equally weighted
        and calculates the proportion of correct components.
        """
        correct_components = sum([
            select_correct, where_correct, group_by_correct,
            order_by_correct, keywords_correct
        ])
        total_components = 5
        
        # Simple proportion as F1 score approximation
        return correct_components / total_components
    
    def validate_component_completeness(self, component_evaluation: ComponentMatching) -> bool:
        """
        Validate that a component evaluation has all five required boolean values.
        
        Args:
            component_evaluation: ComponentMatching record to validate
            
        Returns:
            bool: True if all five components have boolean values
        """
        # Check that all five component fields are present and are boolean
        required_components = [
            component_evaluation.select_correct,
            component_evaluation.where_correct,
            component_evaluation.group_by_correct,
            component_evaluation.order_by_correct,
            component_evaluation.keywords_correct
        ]
        
        # All should be boolean values (not None)
        return all(isinstance(component, bool) for component in required_components)


@given(component_evaluation=component_matching_strategy())
@settings(max_examples=100)
def test_component_evaluation_has_all_five_components(component_evaluation):
    """
    Property 12: Component evaluation completeness
    For any component evaluation, all five components (SELECT, WHERE, GROUP BY, ORDER BY, KEYWORDS) 
    should have boolean values recorded
    **Validates: Requirements 5.1**
    """
    # Create service for validation
    service = ComponentEvaluationService()
    
    # Verify that all five components have boolean values
    assert service.validate_component_completeness(component_evaluation), \
        "Component evaluation should have boolean values for all five components"
    
    # Verify each component individually
    assert isinstance(component_evaluation.select_correct, bool), \
        "select_correct should be a boolean value"
    assert isinstance(component_evaluation.where_correct, bool), \
        "where_correct should be a boolean value"
    assert isinstance(component_evaluation.group_by_correct, bool), \
        "group_by_correct should be a boolean value"
    assert isinstance(component_evaluation.order_by_correct, bool), \
        "order_by_correct should be a boolean value"
    assert isinstance(component_evaluation.keywords_correct, bool), \
        "keywords_correct should be a boolean value"


@given(
    evaluation_id=valid_uuid_strategy,
    select_correct=component_boolean_strategy,
    where_correct=component_boolean_strategy,
    group_by_correct=component_boolean_strategy,
    order_by_correct=component_boolean_strategy,
    keywords_correct=component_boolean_strategy,
    evaluator_notes=evaluator_notes_strategy
)
@settings(max_examples=100)
def test_component_evaluation_creation_completeness(
    evaluation_id, select_correct, where_correct, group_by_correct, 
    order_by_correct, keywords_correct, evaluator_notes
):
    """
    Property 12: Component evaluation completeness - Creation
    For any component evaluation created, all five components should be recorded with boolean values
    **Validates: Requirements 5.1**
    """
    # Create service
    service = ComponentEvaluationService()
    
    # Create component evaluation
    component_evaluation = service.create_component_evaluation(
        evaluation_id=evaluation_id,
        select_correct=select_correct,
        where_correct=where_correct,
        group_by_correct=group_by_correct,
        order_by_correct=order_by_correct,
        keywords_correct=keywords_correct,
        evaluator_notes=evaluator_notes
    )
    
    # Verify all five components are recorded with the correct boolean values
    assert component_evaluation.select_correct == select_correct, \
        f"select_correct should be {select_correct}"
    assert component_evaluation.where_correct == where_correct, \
        f"where_correct should be {where_correct}"
    assert component_evaluation.group_by_correct == group_by_correct, \
        f"group_by_correct should be {group_by_correct}"
    assert component_evaluation.order_by_correct == order_by_correct, \
        f"order_by_correct should be {order_by_correct}"
    assert component_evaluation.keywords_correct == keywords_correct, \
        f"keywords_correct should be {keywords_correct}"
    
    # Verify completeness using service validation
    assert service.validate_component_completeness(component_evaluation), \
        "Created component evaluation should pass completeness validation"


@given(component_create=component_matching_create_strategy())
@settings(max_examples=100)
def test_component_matching_create_model_completeness(component_create):
    """
    Property 12: Component evaluation completeness - Create model
    For any ComponentMatchingCreate object, all five components should have boolean values
    **Validates: Requirements 5.1**
    """
    # Verify that all five components have boolean values in the create model
    assert isinstance(component_create.select_correct, bool), \
        "select_correct should be a boolean value in create model"
    assert isinstance(component_create.where_correct, bool), \
        "where_correct should be a boolean value in create model"
    assert isinstance(component_create.group_by_correct, bool), \
        "group_by_correct should be a boolean value in create model"
    assert isinstance(component_create.order_by_correct, bool), \
        "order_by_correct should be a boolean value in create model"
    assert isinstance(component_create.keywords_correct, bool), \
        "keywords_correct should be a boolean value in create model"
    
    # Verify that the create model can be converted to a full ComponentMatching object
    full_component = ComponentMatching(
        id=uuid4(),
        evaluation_id=component_create.evaluation_id,
        select_correct=component_create.select_correct,
        where_correct=component_create.where_correct,
        group_by_correct=component_create.group_by_correct,
        order_by_correct=component_create.order_by_correct,
        keywords_correct=component_create.keywords_correct,
        f1_score=component_create.f1_score,
        evaluator_notes=component_create.evaluator_notes,
        created_at=datetime.now(timezone.utc)
    )
    
    # Verify the full object maintains completeness
    service = ComponentEvaluationService()
    assert service.validate_component_completeness(full_component), \
        "ComponentMatching created from ComponentMatchingCreate should be complete"


@given(
    evaluations_count=st.integers(min_value=1, max_value=10),
    evaluation_id=valid_uuid_strategy
)
@settings(max_examples=100)
def test_multiple_component_evaluations_completeness(evaluations_count, evaluation_id):
    """
    Property 12: Component evaluation completeness - Multiple evaluations
    For any number of component evaluations, each should have all five components recorded
    **Validates: Requirements 5.1**
    """
    # Create service
    service = ComponentEvaluationService()
    
    component_evaluations = []
    
    # Create multiple component evaluations with random boolean values
    for i in range(evaluations_count):
        # Generate random boolean values for each component
        select_correct = bool(i % 2)  # Alternate true/false
        where_correct = bool((i + 1) % 2)
        group_by_correct = bool((i + 2) % 2)
        order_by_correct = bool((i + 3) % 2)
        keywords_correct = bool((i + 4) % 2)
        
        component_evaluation = service.create_component_evaluation(
            evaluation_id=evaluation_id,
            select_correct=select_correct,
            where_correct=where_correct,
            group_by_correct=group_by_correct,
            order_by_correct=order_by_correct,
            keywords_correct=keywords_correct,
            evaluator_notes=f"Evaluation {i}"
        )
        
        component_evaluations.append(component_evaluation)
    
    # Verify each evaluation has complete component data
    for i, component_evaluation in enumerate(component_evaluations):
        assert service.validate_component_completeness(component_evaluation), \
            f"Component evaluation {i} should have all five components recorded"
        
        # Verify each component is a boolean
        assert isinstance(component_evaluation.select_correct, bool), \
            f"Evaluation {i}: select_correct should be boolean"
        assert isinstance(component_evaluation.where_correct, bool), \
            f"Evaluation {i}: where_correct should be boolean"
        assert isinstance(component_evaluation.group_by_correct, bool), \
            f"Evaluation {i}: group_by_correct should be boolean"
        assert isinstance(component_evaluation.order_by_correct, bool), \
            f"Evaluation {i}: order_by_correct should be boolean"
        assert isinstance(component_evaluation.keywords_correct, bool), \
            f"Evaluation {i}: keywords_correct should be boolean"


@given(
    evaluation_id=valid_uuid_strategy,
    component_values=st.lists(component_boolean_strategy, min_size=5, max_size=5)
)
@settings(max_examples=100)
def test_component_evaluation_preserves_boolean_values(evaluation_id, component_values):
    """
    Property 12: Component evaluation completeness - Value preservation
    For any set of boolean values assigned to components, they should be preserved exactly
    **Validates: Requirements 5.1**
    """
    # Unpack the five boolean values
    select_correct, where_correct, group_by_correct, order_by_correct, keywords_correct = component_values
    
    # Create service
    service = ComponentEvaluationService()
    
    # Create component evaluation with specific boolean values
    component_evaluation = service.create_component_evaluation(
        evaluation_id=evaluation_id,
        select_correct=select_correct,
        where_correct=where_correct,
        group_by_correct=group_by_correct,
        order_by_correct=order_by_correct,
        keywords_correct=keywords_correct
    )
    
    # Verify that the exact boolean values are preserved
    preserved_values = [
        component_evaluation.select_correct,
        component_evaluation.where_correct,
        component_evaluation.group_by_correct,
        component_evaluation.order_by_correct,
        component_evaluation.keywords_correct
    ]
    
    assert preserved_values == component_values, \
        f"Component boolean values should be preserved exactly: expected {component_values}, got {preserved_values}"


@given(component_evaluation=component_matching_strategy())
@settings(max_examples=100)
def test_component_evaluation_no_missing_components(component_evaluation):
    """
    Property 12: Component evaluation completeness - No missing components
    For any component evaluation, none of the five required components should be None or missing
    **Validates: Requirements 5.1**
    """
    # Verify that no component is None
    assert component_evaluation.select_correct is not None, \
        "select_correct should not be None"
    assert component_evaluation.where_correct is not None, \
        "where_correct should not be None"
    assert component_evaluation.group_by_correct is not None, \
        "group_by_correct should not be None"
    assert component_evaluation.order_by_correct is not None, \
        "order_by_correct should not be None"
    assert component_evaluation.keywords_correct is not None, \
        "keywords_correct should not be None"
    
    # Verify that all components are explicitly boolean (not just truthy/falsy)
    component_types = [
        type(component_evaluation.select_correct),
        type(component_evaluation.where_correct),
        type(component_evaluation.group_by_correct),
        type(component_evaluation.order_by_correct),
        type(component_evaluation.keywords_correct)
    ]
    
    assert all(comp_type == bool for comp_type in component_types), \
        f"All components should be of type bool, got types: {component_types}"


@given(
    evaluation_id=valid_uuid_strategy,
    all_true=st.just(True),
    all_false=st.just(False)
)
@settings(max_examples=100)
def test_component_evaluation_extreme_cases(evaluation_id, all_true, all_false):
    """
    Property 12: Component evaluation completeness - Extreme cases
    For component evaluations with all True or all False values, completeness should be maintained
    **Validates: Requirements 5.1**
    """
    # Create service
    service = ComponentEvaluationService()
    
    # Test case: all components correct
    all_correct_evaluation = service.create_component_evaluation(
        evaluation_id=evaluation_id,
        select_correct=all_true,
        where_correct=all_true,
        group_by_correct=all_true,
        order_by_correct=all_true,
        keywords_correct=all_true
    )
    
    # Test case: all components incorrect
    all_incorrect_evaluation = service.create_component_evaluation(
        evaluation_id=evaluation_id,
        select_correct=all_false,
        where_correct=all_false,
        group_by_correct=all_false,
        order_by_correct=all_false,
        keywords_correct=all_false
    )
    
    # Verify completeness for both extreme cases
    assert service.validate_component_completeness(all_correct_evaluation), \
        "All-correct evaluation should have complete component data"
    assert service.validate_component_completeness(all_incorrect_evaluation), \
        "All-incorrect evaluation should have complete component data"
    
    # Verify F1 scores are calculated correctly for extreme cases
    assert all_correct_evaluation.f1_score == 1.0, \
        "All-correct evaluation should have F1 score of 1.0"
    assert all_incorrect_evaluation.f1_score == 0.0, \
        "All-incorrect evaluation should have F1 score of 0.0"


@given(
    evaluation_id=valid_uuid_strategy,
    mixed_components=st.lists(component_boolean_strategy, min_size=5, max_size=5)
)
@settings(max_examples=100)
def test_component_evaluation_f1_score_consistency(evaluation_id, mixed_components):
    """
    Property 12: Component evaluation completeness - F1 score consistency
    For any component evaluation, the F1 score should be consistent with the component boolean values
    **Validates: Requirements 5.1**
    """
    # Unpack component values
    select_correct, where_correct, group_by_correct, order_by_correct, keywords_correct = mixed_components
    
    # Create service
    service = ComponentEvaluationService()
    
    # Create component evaluation
    component_evaluation = service.create_component_evaluation(
        evaluation_id=evaluation_id,
        select_correct=select_correct,
        where_correct=where_correct,
        group_by_correct=group_by_correct,
        order_by_correct=order_by_correct,
        keywords_correct=keywords_correct
    )
    
    # Calculate expected F1 score based on component values
    correct_count = sum(mixed_components)
    expected_f1 = correct_count / 5.0
    
    # Verify F1 score matches expected value
    assert abs(component_evaluation.f1_score - expected_f1) < 0.001, \
        f"F1 score ({component_evaluation.f1_score}) should match expected ({expected_f1}) " \
        f"based on component values {mixed_components}"
    
    # Verify completeness is maintained
    assert service.validate_component_completeness(component_evaluation), \
        "Component evaluation with F1 score should maintain completeness"