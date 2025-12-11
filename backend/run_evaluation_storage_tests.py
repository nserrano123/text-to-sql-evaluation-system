#!/usr/bin/env python3
"""Test runner for evaluation storage property tests"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_evaluation_storage_tests():
    """Run the evaluation storage property tests"""
    print("Running Property-Based Tests for Evaluation Storage...")
    print("**Feature: text-to-sql-evaluation, Property 5: Evaluation storage**")
    print()
    
    try:
        # Import and run the tests
        from backend.tests.property.test_evaluation_storage import (
            test_evaluation_marked_correct_creates_execution_accuracy_record,
            test_evaluation_without_marking_has_no_execution_accuracy_record,
            test_multiple_evaluations_each_get_execution_accuracy_record,
            test_execution_accuracy_preserves_all_evaluation_data,
            test_evaluation_storage_one_to_one_relationship
        )
        
        print("Running test_evaluation_marked_correct_creates_execution_accuracy_record...")
        test_evaluation_marked_correct_creates_execution_accuracy_record()
        print("✓ test_evaluation_marked_correct_creates_execution_accuracy_record passed")
        
        print("Running test_evaluation_without_marking_has_no_execution_accuracy_record...")
        test_evaluation_without_marking_has_no_execution_accuracy_record()
        print("✓ test_evaluation_without_marking_has_no_execution_accuracy_record passed")
        
        print("Running test_multiple_evaluations_each_get_execution_accuracy_record...")
        test_multiple_evaluations_each_get_execution_accuracy_record()
        print("✓ test_multiple_evaluations_each_get_execution_accuracy_record passed")
        
        print("Running test_execution_accuracy_preserves_all_evaluation_data...")
        test_execution_accuracy_preserves_all_evaluation_data()
        print("✓ test_execution_accuracy_preserves_all_evaluation_data passed")
        
        print("Running test_evaluation_storage_one_to_one_relationship...")
        test_evaluation_storage_one_to_one_relationship()
        print("✓ test_evaluation_storage_one_to_one_relationship passed")
        
        print()
        print("🎉 All property tests passed!")
        print("Property 5: Evaluation storage - PASSED")
        print("**Validates: Requirements 3.1**")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_evaluation_storage_tests()
    sys.exit(0 if success else 1)