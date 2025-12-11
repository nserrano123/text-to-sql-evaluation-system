#!/usr/bin/env python3
"""Test runner for evaluation persistence property tests"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_evaluation_persistence_tests():
    """Run the evaluation persistence property tests"""
    print("Running Property-Based Tests for Evaluation Persistence...")
    print("**Feature: text-to-sql-evaluation, Property 17: Evaluation persistence**")
    print()
    
    try:
        # Import and run the tests
        from backend.tests.property.test_evaluation_persistence import (
            test_completed_evaluation_persists_all_associated_data,
            test_incomplete_evaluation_missing_associated_data,
            test_multiple_evaluations_all_persist_independently,
            test_evaluation_persistence_atomic_operation
        )
        
        print("Running test_completed_evaluation_persists_all_associated_data...")
        test_completed_evaluation_persists_all_associated_data()
        print("✓ test_completed_evaluation_persists_all_associated_data passed")
        
        print("Running test_incomplete_evaluation_missing_associated_data...")
        test_incomplete_evaluation_missing_associated_data()
        print("✓ test_incomplete_evaluation_missing_associated_data passed")
        
        print("Running test_multiple_evaluations_all_persist_independently...")
        test_multiple_evaluations_all_persist_independently()
        print("✓ test_multiple_evaluations_all_persist_independently passed")
        
        print("Running test_evaluation_persistence_atomic_operation...")
        test_evaluation_persistence_atomic_operation()
        print("✓ test_evaluation_persistence_atomic_operation passed")
        
        print()
        print("🎉 All property tests passed!")
        print("Property 17: Evaluation persistence - PASSED")
        print("**Validates: Requirements 6.5**")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_evaluation_persistence_tests()
    sys.exit(0 if success else 1)