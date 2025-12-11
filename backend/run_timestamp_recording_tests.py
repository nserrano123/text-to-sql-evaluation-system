#!/usr/bin/env python3
"""Test runner for timestamp recording property tests"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_timestamp_recording_tests():
    """Run the timestamp recording property tests"""
    print("Running Property-Based Tests for Timestamp Recording...")
    print("**Feature: text-to-sql-evaluation, Property 9: Timestamp recording**")
    print()
    
    try:
        # Import hypothesis for running property tests
        from hypothesis import given, strategies as st, settings
        
        # Import the test functions
        from backend.tests.property.test_timestamp_recording import (
            test_evaluation_start_records_timestamp,
            test_evaluation_completion_records_timestamp,
            test_complete_evaluation_workflow_timestamps,
            test_multiple_evaluations_timestamp_independence,
            test_timestamp_recording_with_known_duration,
            test_timestamp_recording_chronological_order,
            test_timestamp_timezone_consistency
        )
        
        print("Running test_evaluation_start_records_timestamp...")
        test_evaluation_start_records_timestamp()
        print("✓ test_evaluation_start_records_timestamp passed")
        
        print("Running test_evaluation_completion_records_timestamp...")
        test_evaluation_completion_records_timestamp()
        print("✓ test_evaluation_completion_records_timestamp passed")
        
        print("Running test_complete_evaluation_workflow_timestamps...")
        test_complete_evaluation_workflow_timestamps()
        print("✓ test_complete_evaluation_workflow_timestamps passed")
        
        print("Running test_multiple_evaluations_timestamp_independence...")
        test_multiple_evaluations_timestamp_independence()
        print("✓ test_multiple_evaluations_timestamp_independence passed")
        
        print("Running test_timestamp_recording_with_known_duration...")
        test_timestamp_recording_with_known_duration()
        print("✓ test_timestamp_recording_with_known_duration passed")
        
        print("Running test_timestamp_recording_chronological_order...")
        test_timestamp_recording_chronological_order()
        print("✓ test_timestamp_recording_chronological_order passed")
        
        print("Running test_timestamp_timezone_consistency...")
        test_timestamp_timezone_consistency()
        print("✓ test_timestamp_timezone_consistency passed")
        
        print()
        print("🎉 All timestamp recording property tests passed!")
        print("Property 9: Timestamp recording - PASSED")
        print("**Validates: Requirements 4.1, 4.2**")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_timestamp_recording_tests()
    sys.exit(0 if success else 1)