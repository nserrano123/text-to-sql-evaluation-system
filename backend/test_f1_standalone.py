#!/usr/bin/env python3
"""
Standalone test for F1 score calculation to avoid pytest issues
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from uuid import uuid4
from datetime import datetime
from hypothesis import given, strategies as st, settings

from app.models.component_matching import ComponentMatching
from app.services.component_matching_service import ComponentMatchingService


# Strategy for generating ComponentMatching records
def component_matching_strategy():
    """Generate ComponentMatching records with random boolean values"""
    return st.builds(
        ComponentMatching,
        id=st.just(uuid4()),
        evaluation_id=st.just(uuid4()),
        select_correct=st.booleans(),
        where_correct=st.booleans(),
        group_by_correct=st.booleans(),
        order_by_correct=st.booleans(),
        keywords_correct=st.booleans(),
        f1_score=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0)),
        evaluator_notes=st.one_of(st.none(), st.text()),
        created_at=st.just(datetime.now())
    )


# Strategy for generating precision and recall values
precision_recall_strategy = st.floats(min_value=0.0, max_value=1.0)


def test_f1_score_basic_formula():
    """Test basic F1 score formula"""
    service = ComponentMatchingService(None)
    
    # Test edge cases
    assert service.calculate_f1_score(0.0, 0.0) == 0.0
    assert service.calculate_f1_score(1.0, 1.0) == 1.0
    assert service.calculate_f1_score(1.0, 0.0) == 0.0
    assert service.calculate_f1_score(0.0, 1.0) == 0.0
    assert service.calculate_f1_score(0.5, 0.5) == 0.5
    
    # Test specific case
    precision, recall = 0.8, 0.6
    expected = 2 * (precision * recall) / (precision + recall)
    actual = service.calculate_f1_score(precision, recall)
    assert abs(actual - expected) < 1e-10
    
    print("✓ Basic F1 formula tests passed")


@given(precision_recall_strategy, precision_recall_strategy)
@settings(max_examples=100)
def test_f1_score_property(precision, recall):
    """
    **Feature: text-to-sql-evaluation, Property 13: F1 score calculation**
    **Validates: Requirements 5.3**
    
    Property test for F1 score calculation formula
    """
    service = ComponentMatchingService(None)
    
    # Calculate expected F1 score manually
    if precision + recall == 0:
        expected_f1 = 0.0
    else:
        expected_f1 = 2 * (precision * recall) / (precision + recall)
    
    # Calculate F1 using the service method
    actual_f1 = service.calculate_f1_score(precision, recall)
    
    # Assert they match (with small tolerance for floating point precision)
    assert abs(actual_f1 - expected_f1) < 1e-10, (
        f"F1 calculation mismatch: expected {expected_f1}, got {actual_f1}. "
        f"Precision: {precision}, Recall: {recall}"
    )
    
    # Ensure F1 score is within valid range [0, 1]
    assert 0.0 <= actual_f1 <= 1.0, f"F1 score {actual_f1} is outside valid range [0, 1]"


@given(st.lists(component_matching_strategy(), min_size=1, max_size=50))
@settings(max_examples=100)
def test_component_f1_scores_property(component_records):
    """
    **Feature: text-to-sql-evaluation, Property 13: F1 score calculation**
    **Validates: Requirements 5.3**
    
    Property test for component F1 scores calculation
    """
    service = ComponentMatchingService(None)
    
    # Calculate F1 scores using the service
    f1_scores = service.calculate_component_f1_scores(component_records)
    
    # Verify all expected components are present
    expected_components = {"select", "where", "group_by", "order_by", "keywords"}
    assert set(f1_scores.keys()) == expected_components
    
    # Manually calculate expected F1 scores for each component
    components_data = {
        "select": [record.select_correct for record in component_records],
        "where": [record.where_correct for record in component_records],
        "group_by": [record.group_by_correct for record in component_records],
        "order_by": [record.order_by_correct for record in component_records],
        "keywords": [record.keywords_correct for record in component_records]
    }
    
    for component_name, correct_values in components_data.items():
        total_evaluations = len(correct_values)
        correct_count = sum(correct_values)
        
        # Expected accuracy (which equals F1 in this implementation)
        expected_accuracy = correct_count / total_evaluations if total_evaluations > 0 else 0.0
        
        actual_f1 = f1_scores[component_name]
        
        # Assert they match (with small tolerance for floating point precision)
        assert abs(actual_f1 - expected_accuracy) < 1e-10, (
            f"Component {component_name} F1 calculation mismatch: "
            f"expected {expected_accuracy}, got {actual_f1}. "
            f"Correct: {correct_count}, Total: {total_evaluations}"
        )
        
        # Ensure F1 score is within valid range [0, 1]
        assert 0.0 <= actual_f1 <= 1.0, (
            f"Component {component_name} F1 score {actual_f1} is outside valid range [0, 1]"
        )


def test_component_f1_edge_cases():
    """Test component F1 scores edge cases"""
    service = ComponentMatchingService(None)
    
    # Test empty list
    f1_scores = service.calculate_component_f1_scores([])
    expected_components = {"select", "where", "group_by", "order_by", "keywords"}
    assert set(f1_scores.keys()) == expected_components
    for component, score in f1_scores.items():
        assert score == 0.0
    
    # Test all correct
    records = [
        ComponentMatching(
            id=uuid4(),
            evaluation_id=uuid4(),
            select_correct=True,
            where_correct=True,
            group_by_correct=True,
            order_by_correct=True,
            keywords_correct=True,
            created_at=datetime.now()
        )
        for _ in range(5)
    ]
    
    f1_scores = service.calculate_component_f1_scores(records)
    for component, score in f1_scores.items():
        assert score == 1.0
    
    # Test all incorrect
    records = [
        ComponentMatching(
            id=uuid4(),
            evaluation_id=uuid4(),
            select_correct=False,
            where_correct=False,
            group_by_correct=False,
            order_by_correct=False,
            keywords_correct=False,
            created_at=datetime.now()
        )
        for _ in range(5)
    ]
    
    f1_scores = service.calculate_component_f1_scores(records)
    for component, score in f1_scores.items():
        assert score == 0.0
    
    print("✓ Component F1 edge cases tests passed")


def main():
    """Run all tests"""
    print("Running F1 score calculation tests...")
    
    try:
        # Run basic tests
        test_f1_score_basic_formula()
        test_component_f1_edge_cases()
        
        # Run property tests
        print("Running property tests...")
        test_f1_score_property()
        test_component_f1_scores_property()
        
        print("✓ All F1 score calculation tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)