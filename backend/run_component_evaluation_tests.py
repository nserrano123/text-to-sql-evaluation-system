#!/usr/bin/env python3
"""Test runner for component evaluation completeness property tests"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_component_evaluation_tests():
    """Run the component evaluation completeness property tests"""
    print("Running Property-Based Tests for Component Evaluation Completeness...")
    print("**Feature: text-to-sql-evaluation, Property 12: Component evaluation completeness**")
    print()
    
    try:
        # Import the test functions
        from backend.tests.property.test_component_evaluation_completeness import (
            test_component_evaluation_has_all_five_components,
            test_component_evaluation_creation_completeness,
            test_component_matching_create_model_completeness,
            test_multiple_component_evaluations_completeness,
            test_component_evaluation_preserves_boolean_values,
            test_component_evaluation_no_missing_components,
            test_component_evaluation_extreme_cases,
            test_component_evaluation_f1_score_consistency
        )
        
        # Import required models and utilities
        from backend.app.models.component_matching import ComponentMatching, ComponentMatchingCreate
        from uuid import uuid4
        from datetime import datetime, timezone
        
        print("Running test_component_evaluation_has_all_five_components...")
        test_component_evaluation_has_all_five_components()
        print("✓ test_component_evaluation_has_all_five_components passed")
        
        print("Running test_component_evaluation_creation_completeness...")
        test_component_evaluation_creation_completeness()
        print("✓ test_component_evaluation_creation_completeness passed")
        
        print("Running test_component_matching_create_model_completeness...")
        test_component_matching_create_model_completeness()
        print("✓ test_component_matching_create_model_completeness passed")
        
        print("Running test_multiple_component_evaluations_completeness...")
        test_multiple_component_evaluations_completeness()
        print("✓ test_multiple_component_evaluations_completeness passed")
        
        print("Running test_component_evaluation_preserves_boolean_values...")
        test_component_evaluation_preserves_boolean_values()
        print("✓ test_component_evaluation_preserves_boolean_values passed")
        
        print("Running test_component_evaluation_no_missing_components...")
        test_component_evaluation_no_missing_components()
        print("✓ test_component_evaluation_no_missing_components passed")
        
        print("Running test_component_evaluation_extreme_cases...")
        test_component_evaluation_extreme_cases()
        print("✓ test_component_evaluation_extreme_cases passed")
        
        print("Running test_component_evaluation_f1_score_consistency...")
        test_component_evaluation_f1_score_consistency()
        print("✓ test_component_evaluation_f1_score_consistency passed")
        
        print()
        print("🎉 All component evaluation completeness property tests passed!")
        print("Property 12: Component evaluation completeness - PASSED")
        print("**Validates: Requirements 5.1**")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_component_evaluation_tests()
    sys.exit(0 if success else 1)