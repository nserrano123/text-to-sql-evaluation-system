#!/usr/bin/env python3
"""Test runner for aggregated metrics accuracy property tests"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import test functions directly
sys.path.insert(0, os.path.dirname(__file__))
from tests.property.test_aggregated_metrics_accuracy import *

async def run_aggregated_metrics_tests():
    """Run the aggregated metrics accuracy property tests"""
    print("Running Property-Based Tests for Aggregated Metrics Accuracy...")
    print("**Feature: text-to-sql-evaluation, Property 20: Aggregated metrics accuracy**")
    print()
    
    try:
        
        # Test 1: Basic calculation
        print("Running test_aggregated_metrics_accuracy_calculation...")
        
        # Create simple mock objects
        class SimpleEval:
            def __init__(self):
                self.id = "test"
        
        class SimpleEA:
            def __init__(self, correct):
                self.is_correct = correct
        
        class SimpleTTA:
            def __init__(self, duration):
                self.duration_seconds = duration
        
        class SimpleCM:
            def __init__(self):
                self.select_correct = True
                self.where_correct = False
                self.group_by_correct = True
                self.order_by_correct = False
                self.keywords_correct = True
        
        test_dataset = {
            'evaluations': [SimpleEval()],
            'execution_accuracy': [SimpleEA(True)],
            'time_to_answer': [SimpleTTA(30.0)],
            'component_matching': [SimpleCM()]
        }
        await test_aggregated_metrics_accuracy_calculation(test_dataset)
        print("✓ test_aggregated_metrics_accuracy_calculation passed")
        
        # Test 2: Empty dataset
        print("Running test_aggregated_metrics_empty_dataset_handling...")
        await test_aggregated_metrics_empty_dataset_handling()
        print("✓ test_aggregated_metrics_empty_dataset_handling passed")
        
        # Test 3: EX edge cases
        print("Running test_aggregated_metrics_ex_calculation_edge_cases...")
        await test_aggregated_metrics_ex_calculation_edge_cases(3, 2)
        print("✓ test_aggregated_metrics_ex_calculation_edge_cases passed")
        
        # Test 4: TTA precision
        print("Running test_aggregated_metrics_tta_calculation_precision...")
        await test_aggregated_metrics_tta_calculation_precision([10.5, 20.3, 15.7])
        print("✓ test_aggregated_metrics_tta_calculation_precision passed")
        
        # Test 5: Component F1
        print("Running test_aggregated_metrics_component_f1_calculation...")
        component_test_data = {
            'select': [True, False, True],
            'where': [True, True, False],
            'group_by': [False, False, False],
            'order_by': [True, True, True],
            'keywords': [False, True, False]
        }
        await test_aggregated_metrics_component_f1_calculation(component_test_data)
        print("✓ test_aggregated_metrics_component_f1_calculation passed")
        
        print()
        print("🎉 All property tests passed!")
        print("Property 20: Aggregated metrics accuracy - PASSED")
        print("**Validates: Requirements 7.4**")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_aggregated_metrics_tests())
    sys.exit(0 if success else 1)