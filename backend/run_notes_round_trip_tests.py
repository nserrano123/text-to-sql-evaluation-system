#!/usr/bin/env python3
"""Test runner for notes round-trip property tests"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_notes_round_trip_tests():
    """Run the notes round-trip property tests"""
    print("Running Property-Based Tests for Notes Round-Trip...")
    print("**Feature: text-to-sql-evaluation, Property 8: Notes round-trip**")
    print()
    
    try:
        # Import and run the tests
        from backend.tests.property.test_notes_round_trip import (
            test_execution_accuracy_notes_round_trip,
            test_component_matching_notes_round_trip,
            test_both_notes_fields_round_trip_independently,
            test_multiple_notes_round_trip_consistency
        )
        
        print("Running test_execution_accuracy_notes_round_trip...")
        test_execution_accuracy_notes_round_trip()
        print("✓ test_execution_accuracy_notes_round_trip passed")
        
        print("Running test_component_matching_notes_round_trip...")
        test_component_matching_notes_round_trip()
        print("✓ test_component_matching_notes_round_trip passed")
        
        print("Running test_both_notes_fields_round_trip_independently...")
        test_both_notes_fields_round_trip_independently()
        print("✓ test_both_notes_fields_round_trip_independently passed")
        
        print("Running test_multiple_notes_round_trip_consistency...")
        test_multiple_notes_round_trip_consistency()
        print("✓ test_multiple_notes_round_trip_consistency passed")
        
        print()
        print("🎉 All property tests passed!")
        print("Property 8: Notes round-trip - PASSED")
        print("**Validates: Requirements 3.4, 5.5, 10.3**")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_notes_round_trip_tests()
    sys.exit(0 if success else 1)