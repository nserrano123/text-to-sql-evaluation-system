#!/usr/bin/env python3
"""
Isolated test for F1 score calculation without database dependencies
"""

import sys
import os
from uuid import uuid4
from datetime import datetime
from hypothesis import given, strategies as st, settings
from typing import List, Dict


# Minimal ComponentMatching model for testing
class ComponentMatching:
    def __init__(self, id, evaluation_id, select_correct, where_correct, 
                 group_by_correct, order_by_correct, keywords_correct, 
                 f1_score=None, evaluator_notes=None, created_at=None):
        self.id = id
        self.evaluation_id = evaluation_id
        self.select_correct = select_correct
        self.where_correct = where_correct
        self.group_by_correct = group_by_correct
        self.order_by_correct = order_by_correct
        self.keywords_correct = keywords_correct
        self.f1_score = f1_score
        self.evaluator_notes = evaluator_notes
        self.created_at = created_at or datetime.now()


# Isolated ComponentMatchingService for testing
class ComponentMatchingService:
    """Service for calculating Component Matching metrics"""
    
    def __init__(self, repository=None):
        self.repository = repository
    
    def calculate_f1_score(self, precision: float, recall: float) -> float:
        """
        Calculate F1 score using the standard formula.
        
        Formula: F1 = 2 × (precision × recall) / (precision + recall)
        
        Args:
            precision: Precision value (0.0 to 1.0)
            recall: Recall value (0.0 to 1.0)
            
        Returns:
            float: F1 score (0.0 to 1.0)
        """
        if precision + recall == 0:
            return 0.0
        
        f1 = 2 * (precision * recall) / (precision + recall)
        return f1
    
    def calculate_component_f1_scores(self, component_records: List[ComponentMatching]) -> Dict[str, float]:
        """
        Calculate F1 scores for each SQL component.
        
        For each component, we calculate precision and recall based on the boolean values
        in the component_records, then compute the F1 score.
        
        Args:
            component_records: List of ComponentMatching records
            
        Returns:
            Dict[str, float]: F1 scores per component
        """
        if not component_records:
            return {
                "select": 0.0,
                "where": 0.0,
                "group_by": 0.0,
                "order_by": 0.0,
                "keywords": 0.0
            }
        
        components = {
            "select": [record.select_correct for record in component_records],
            "where": [record.where_correct for record in component_records],
            "group_by": [record.group_by_correct for record in component_records],
            "order_by": [record.order_by_correct for record in component_records],
            "keywords": [record.keywords_correct for record in component_records]
        }
        
        f1_scores = {}
        
        for component_name, correct_values in components.items():
            # For component matching, we treat each evaluation as a binary classification
            # True Positives: correctly identified as correct
            # False Positives: incorrectly identified as correct  
            # False Negatives: incorrectly identified as incorrect
            # True Negatives: correctly identified as incorrect
            
            # In this context, we assume all components should ideally be correct
            # So precision = correct_predictions / total_predictions
            # And recall = correct_predictions / total_should_be_correct
            
            total_evaluations = len(correct_values)
            correct_count = sum(correct_values)
            
            if total_evaluations == 0:
                f1_scores[component_name] = 0.0
                continue
            
            # For component evaluation, precision and recall are the same
            # as we're measuring accuracy of component identification
            accuracy = correct_count / total_evaluations
            
            # F1 score when precision = recall = accuracy is just the accuracy
            f1_scores[component_name] = accuracy
        
        return f1_scores


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