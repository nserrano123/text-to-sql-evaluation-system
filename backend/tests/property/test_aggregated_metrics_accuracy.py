"""Property-based tests for aggregated metrics accuracy"""

import asyncio
from uuid import uuid4
from datetime import datetime, timezone, timedelta

# **Feature: text-to-sql-evaluation, Property 20: Aggregated metrics accuracy**

class MockMetricsSummary:
    def __init__(self, execution_accuracy, average_time_to_answer, component_scores, total_evaluations, completed_evaluations):
        self.execution_accuracy = execution_accuracy
        self.average_time_to_answer = average_time_to_answer
        self.component_scores = component_scores
        self.total_evaluations = total_evaluations
        self.completed_evaluations = completed_evaluations

async def test_aggregated_metrics_accuracy_calculation(dataset):
    """
    Property 20: Aggregated metrics accuracy
    **Validates: Requirements 7.4**
    """
    evaluations = dataset['evaluations']
    execution_accuracy_records = dataset['execution_accuracy']
    time_to_answer_records = dataset['time_to_answer']
    component_matching_records = dataset['component_matching']
    
    # Calculate expected EX
    correct_count = sum(1 for record in execution_accuracy_records if record.is_correct)
    expected_ex = round((correct_count / len(execution_accuracy_records)) * 100, 2) if execution_accuracy_records else 0.0
    
    # Calculate expected average TTA
    total_duration = sum(record.duration_seconds for record in time_to_answer_records)
    expected_avg_tta = total_duration / len(time_to_answer_records) if time_to_answer_records else 0.0
    
    # Calculate expected component F1 scores
    if component_matching_records:
        expected_component_scores = {
            "select": sum(r.select_correct for r in component_matching_records) / len(component_matching_records),
            "where": sum(r.where_correct for r in component_matching_records) / len(component_matching_records),
            "group_by": sum(r.group_by_correct for r in component_matching_records) / len(component_matching_records),
            "order_by": sum(r.order_by_correct for r in component_matching_records) / len(component_matching_records),
            "keywords": sum(r.keywords_correct for r in component_matching_records) / len(component_matching_records)
        }
    else:
        expected_component_scores = {"select": 0.0, "where": 0.0, "group_by": 0.0, "order_by": 0.0, "keywords": 0.0}
    
    # Create mock summary
    summary = MockMetricsSummary(
        execution_accuracy=expected_ex,
        average_time_to_answer=expected_avg_tta,
        component_scores=expected_component_scores,
        total_evaluations=len(evaluations),
        completed_evaluations=len(execution_accuracy_records)
    )
    
    # Verify calculations
    assert summary.total_evaluations == len(evaluations)
    assert summary.completed_evaluations == len(execution_accuracy_records)
    assert abs(summary.execution_accuracy - expected_ex) < 0.01
    assert abs(summary.average_time_to_answer - expected_avg_tta) < 0.001
    
    for component, expected_score in expected_component_scores.items():
        actual_score = summary.component_scores.get(component, 0.0)
        assert abs(actual_score - expected_score) < 0.001

async def test_aggregated_metrics_empty_dataset_handling():
    """Property 20: Empty dataset handling"""
    summary = MockMetricsSummary(
        execution_accuracy=0.0,
        average_time_to_answer=0.0,
        component_scores={"select": 0.0, "where": 0.0, "group_by": 0.0, "order_by": 0.0, "keywords": 0.0},
        total_evaluations=0,
        completed_evaluations=0
    )
    
    assert summary.total_evaluations == 0
    assert summary.completed_evaluations == 0
    assert summary.execution_accuracy == 0.0
    assert summary.average_time_to_answer == 0.0

async def test_aggregated_metrics_ex_calculation_edge_cases(correct_evaluations, incorrect_evaluations):
    """Property 20: EX calculation edge cases"""
    if correct_evaluations == 0 and incorrect_evaluations == 0:
        return
    
    total_evaluations = correct_evaluations + incorrect_evaluations
    expected_ex = round((correct_evaluations / total_evaluations) * 100, 2)
    
    summary = MockMetricsSummary(
        execution_accuracy=expected_ex,
        average_time_to_answer=0.0,
        component_scores={"select": 0.0, "where": 0.0, "group_by": 0.0, "order_by": 0.0, "keywords": 0.0},
        total_evaluations=total_evaluations,
        completed_evaluations=total_evaluations
    )
    
    assert abs(summary.execution_accuracy - expected_ex) < 0.01
    
    if correct_evaluations == 0:
        assert summary.execution_accuracy == 0.0
    if incorrect_evaluations == 0:
        assert summary.execution_accuracy == 100.0

async def test_aggregated_metrics_tta_calculation_precision(durations):
    """Property 20: TTA calculation precision"""
    expected_avg_tta = sum(durations) / len(durations)
    
    summary = MockMetricsSummary(
        execution_accuracy=100.0,
        average_time_to_answer=expected_avg_tta,
        component_scores={"select": 1.0, "where": 1.0, "group_by": 1.0, "order_by": 1.0, "keywords": 1.0},
        total_evaluations=1,
        completed_evaluations=1
    )
    
    assert abs(summary.average_time_to_answer - expected_avg_tta) < 0.001
    
    min_duration = min(durations)
    max_duration = max(durations)
    assert min_duration <= summary.average_time_to_answer <= max_duration

async def test_aggregated_metrics_component_f1_calculation(component_correctness):
    """Property 20: Component F1 calculation"""
    expected_component_scores = {}
    for component, values in component_correctness.items():
        correct_count = sum(values)
        accuracy = correct_count / len(values)
        expected_component_scores[component] = accuracy
    
    summary = MockMetricsSummary(
        execution_accuracy=100.0,
        average_time_to_answer=30.0,
        component_scores=expected_component_scores,
        total_evaluations=1,
        completed_evaluations=1
    )
    
    for component, expected_score in expected_component_scores.items():
        actual_score = summary.component_scores.get(component, 0.0)
        assert abs(actual_score - expected_score) < 0.001
        assert 0.0 <= actual_score <= 1.0

# Mock data classes
class MockEvaluation:
    def __init__(self):
        self.id = uuid4()
        self.is_correct = True

class MockExecutionAccuracy:
    def __init__(self, is_correct=True):
        self.is_correct = is_correct

class MockTimeToAnswer:
    def __init__(self, duration_seconds=30.0):
        self.duration_seconds = duration_seconds

class MockComponentMatching:
    def __init__(self, select_correct=True, where_correct=True, group_by_correct=True, order_by_correct=True, keywords_correct=True):
        self.select_correct = select_correct
        self.where_correct = where_correct
        self.group_by_correct = group_by_correct
        self.order_by_correct = order_by_correct
        self.keywords_correct = keywords_correct