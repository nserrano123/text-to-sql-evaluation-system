"""Property-based test for F1 score calculation"""

import pytest
from hypothesis import given, strategies as st, settings
from uuid import uuid4
from datetime import datetime

from app.models.component_matching import ComponentMatching
from app.services.component_matching_service import ComponentMatchingService
from app.repositories.component_matching_repository import ComponentMatchingRepository


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


class TestF1ScoreCalculation:
    """Property-based tests for F1 score calculation"""
    
    def setup_method(self):
        """Set up test dependencies"""
        # Create a mock repository for testing
        self.repository = None  # We'll test the calculation logic directly
        self.service = ComponentMatchingService(self.repository)
    
    @given(precision_recall_strategy, precision_recall_strategy)
    @settings(max_examples=100)
    def test_f1_score_calculation_formula(self, precision, recall):
        """
        **Feature: text-to-sql-evaluation, Property 13: F1 score calculation**
        **Validates: Requirements 5.3**
        
        For any precision and recall values, the F1 score should be calculated correctly 
        using the standard formula: F1 = 2 × (precision × recall) / (precision + recall)
        """
        # Calculate expected F1 score manually
        if precision + recall == 0:
            expected_f1 = 0.0
        else:
            expected_f1 = 2 * (precision * recall) / (precision + recall)
        
        # Calculate F1 using the service method
        actual_f1 = self.service.calculate_f1_score(precision, recall)
        
        # Assert they match (with small tolerance for floating point precision)
        assert abs(actual_f1 - expected_f1) < 1e-10, (
            f"F1 calculation mismatch: expected {expected_f1}, got {actual_f1}. "
            f"Precision: {precision}, Recall: {recall}"
        )
        
        # Ensure F1 score is within valid range [0, 1]
        assert 0.0 <= actual_f1 <= 1.0, f"F1 score {actual_f1} is outside valid range [0, 1]"
    
    @given(st.lists(component_matching_strategy(), min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_component_f1_scores_calculation(self, component_records):
        """
        **Feature: text-to-sql-evaluation, Property 13: F1 score calculation**
        **Validates: Requirements 5.3**
        
        For any set of component evaluations, F1 scores should be calculated correctly
        for each component (SELECT, WHERE, GROUP BY, ORDER BY, KEYWORDS)
        """
        # Calculate F1 scores using the service
        f1_scores = self.service.calculate_component_f1_scores(component_records)
        
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
    
    def test_f1_score_edge_cases(self):
        """Test F1 score calculation edge cases"""
        
        # Test with precision = 0, recall = 0
        f1 = self.service.calculate_f1_score(0.0, 0.0)
        assert f1 == 0.0
        
        # Test with precision = 1, recall = 1 (perfect score)
        f1 = self.service.calculate_f1_score(1.0, 1.0)
        assert f1 == 1.0
        
        # Test with precision = 1, recall = 0
        f1 = self.service.calculate_f1_score(1.0, 0.0)
        assert f1 == 0.0
        
        # Test with precision = 0, recall = 1
        f1 = self.service.calculate_f1_score(0.0, 1.0)
        assert f1 == 0.0
        
        # Test with precision = 0.5, recall = 0.5
        f1 = self.service.calculate_f1_score(0.5, 0.5)
        assert f1 == 0.5
    
    def test_component_f1_scores_empty_list(self):
        """Test component F1 scores calculation with empty list"""
        f1_scores = self.service.calculate_component_f1_scores([])
        
        expected_components = {"select", "where", "group_by", "order_by", "keywords"}
        assert set(f1_scores.keys()) == expected_components
        
        # All scores should be 0.0 for empty list
        for component, score in f1_scores.items():
            assert score == 0.0, f"Component {component} should have F1 score 0.0 for empty list"
    
    def test_component_f1_scores_all_correct(self):
        """Test component F1 scores when all components are correct"""
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
        
        f1_scores = self.service.calculate_component_f1_scores(records)
        
        # All scores should be 1.0 (perfect)
        for component, score in f1_scores.items():
            assert score == 1.0, f"Component {component} should have F1 score 1.0 when all correct"
    
    def test_component_f1_scores_all_incorrect(self):
        """Test component F1 scores when all components are incorrect"""
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
        
        f1_scores = self.service.calculate_component_f1_scores(records)
        
        # All scores should be 0.0
        for component, score in f1_scores.items():
            assert score == 0.0, f"Component {component} should have F1 score 0.0 when all incorrect"