#!/usr/bin/env python3
"""Test runner for TTA calculation property-based tests"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_tta_calculation_tests():
    """Run the TTA calculation property tests"""
    print("Running Property-Based Tests for TTA Calculation Correctness...")
    print("**Feature: text-to-sql-evaluation, Property 10 & 11: TTA calculation correctness**")
    print()
    
    try:
        # Import and run the tests
        from backend.tests.property.test_tta_calculation import (
            test_tta_calculation_matches_timestamp_difference,
            test_time_to_answer_model_duration_consistency,
            test_time_to_answer_create_model_validation,
            test_average_tta_calculation_correctness,
            test_tta_calculation_with_generated_end_time,
            test_multiple_tta_calculations_independence,
            test_tta_service_rejects_invalid_timestamps,
            # Property 11 tests
            test_average_tta_for_completed_evaluations,
            test_average_tta_with_uniform_durations,
            test_average_tta_mathematical_properties,
            test_average_tta_empty_list_handling
        )
        
        print("=== Property 10: TTA calculation correctness ===")
        print("Running test_tta_calculation_matches_timestamp_difference...")
        test_tta_calculation_matches_timestamp_difference()
        print("✓ test_tta_calculation_matches_timestamp_difference passed")
        
        print("Running test_time_to_answer_model_duration_consistency...")
        test_time_to_answer_model_duration_consistency()
        print("✓ test_time_to_answer_model_duration_consistency passed")
        
        print("Running test_time_to_answer_create_model_validation...")
        test_time_to_answer_create_model_validation()
        print("✓ test_time_to_answer_create_model_validation passed")
        
        print("Running test_average_tta_calculation_correctness...")
        test_average_tta_calculation_correctness()
        print("✓ test_average_tta_calculation_correctness passed")
        
        print("Running test_tta_calculation_with_generated_end_time...")
        test_tta_calculation_with_generated_end_time()
        print("✓ test_tta_calculation_with_generated_end_time passed")
        
        print("Running test_multiple_tta_calculations_independence...")
        test_multiple_tta_calculations_independence()
        print("✓ test_multiple_tta_calculations_independence passed")
        
        print("Running test_tta_service_rejects_invalid_timestamps...")
        test_tta_service_rejects_invalid_timestamps()
        print("✓ test_tta_service_rejects_invalid_timestamps passed")
        
        print()
        print("=== Property 11: Average TTA calculation ===")
        print("Running test_average_tta_for_completed_evaluations...")
        test_average_tta_for_completed_evaluations()
        print("✓ test_average_tta_for_completed_evaluations passed")
        
        print("Running test_average_tta_with_uniform_durations...")
        test_average_tta_with_uniform_durations()
        print("✓ test_average_tta_with_uniform_durations passed")
        
        print("Running test_average_tta_mathematical_properties...")
        test_average_tta_mathematical_properties()
        print("✓ test_average_tta_mathematical_properties passed")
        
        print("Running test_average_tta_empty_list_handling...")
        test_average_tta_empty_list_handling()
        print("✓ test_average_tta_empty_list_handling passed")
        
        print()
        print("🎉 All property tests passed!")
        print("Property 10: TTA calculation correctness - PASSED")
        print("**Validates: Requirements 4.3**")
        print("Property 11: Average TTA calculation - PASSED")
        print("**Validates: Requirements 4.4**")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_tta_calculation_tests()
    sys.exit(0 if success else 1)