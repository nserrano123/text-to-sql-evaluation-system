#!/usr/bin/env python3
"""
Run CSV export completeness property tests
"""

import sys
import os
sys.path.append('.')

from hypothesis import given, strategies as st, settings
from tests.property.test_csv_export_completeness import (
    test_csv_export_completeness_all_gold_fields_property,
    test_csv_export_completeness_full_dataset_property,
    test_csv_export_completeness_partial_data_property,
    test_csv_export_completeness_scalability_property,
    gold_query_strategy,
    evaluation_strategy,
    execution_accuracy_strategy,
    time_to_answer_strategy,
    component_matching_strategy
)

def run_property_tests():
    """Run all property-based tests for CSV export completeness"""
    
    print("Running CSV Export Completeness Property Tests...")
    print("=" * 60)
    
    # Test 1: All gold fields property
    print("\n1. Testing all gold fields property...")
    try:
        # Run with Hypothesis
        @given(gold_queries=st.lists(gold_query_strategy(), min_size=1, max_size=5))
        @settings(max_examples=10)  # Reduced for faster testing
        def test_wrapper_1(gold_queries):
            test_csv_export_completeness_all_gold_fields_property(gold_queries)
        
        test_wrapper_1()
        print("   ✓ PASSED: All gold fields property test")
    except Exception as e:
        print(f"   ✗ FAILED: All gold fields property test - {e}")
        return False
    
    # Test 2: Scalability property
    print("\n2. Testing scalability property...")
    try:
        @given(data_size=st.integers(min_value=1, max_value=10))
        @settings(max_examples=10)
        def test_wrapper_2(data_size):
            test_csv_export_completeness_scalability_property(data_size)
        
        test_wrapper_2()
        print("   ✓ PASSED: Scalability property test")
    except Exception as e:
        print(f"   ✗ FAILED: Scalability property test - {e}")
        return False
    
    # Test 3: Partial data property
    print("\n3. Testing partial data property...")
    try:
        @given(
            gold_queries=st.lists(gold_query_strategy(), min_size=1, max_size=3),
            partial_evaluations=st.lists(evaluation_strategy(), min_size=0, max_size=2)
        )
        @settings(max_examples=10)
        def test_wrapper_3(gold_queries, partial_evaluations):
            test_csv_export_completeness_partial_data_property(gold_queries, partial_evaluations)
        
        test_wrapper_3()
        print("   ✓ PASSED: Partial data property test")
    except Exception as e:
        print(f"   ✗ FAILED: Partial data property test - {e}")
        return False
    
    # Test 4: Full dataset property (simplified)
    print("\n4. Testing full dataset property...")
    try:
        @given(
            gold_queries=st.lists(gold_query_strategy(), min_size=1, max_size=2),
            evaluations_with_metrics=st.lists(
                st.tuples(
                    evaluation_strategy(),
                    execution_accuracy_strategy(),
                    time_to_answer_strategy(),
                    component_matching_strategy()
                ),
                min_size=1,
                max_size=2
            )
        )
        @settings(max_examples=5)  # Reduced due to complexity
        def test_wrapper_4(gold_queries, evaluations_with_metrics):
            test_csv_export_completeness_full_dataset_property(gold_queries, evaluations_with_metrics)
        
        test_wrapper_4()
        print("   ✓ PASSED: Full dataset property test")
    except Exception as e:
        print(f"   ✗ FAILED: Full dataset property test - {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ ALL CSV EXPORT COMPLETENESS PROPERTY TESTS PASSED!")
    return True

if __name__ == "__main__":
    success = run_property_tests()
    sys.exit(0 if success else 1)