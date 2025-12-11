#!/usr/bin/env python3
"""Test runner for property-based tests"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_required_field_validation_tests():
    """Run the required field validation property tests"""
    print("Running Property-Based Tests for Required Field Validation...")
    print("**Feature: text-to-sql-evaluation, Property 1: Required field validation**")
    print()
    
    try:
        # Import and run the tests
        from backend.tests.property.test_required_field_validation import (
            test_missing_chat_input_rejected,
            test_missing_tablas_columnas_ddl_rejected,
            test_missing_sql_reference_rejected,
            test_valid_required_fields_accepted
        )
        
        print("Running test_missing_chat_input_rejected...")
        test_missing_chat_input_rejected()
        print("✓ test_missing_chat_input_rejected passed")
        
        print("Running test_missing_tablas_columnas_ddl_rejected...")
        test_missing_tablas_columnas_ddl_rejected()
        print("✓ test_missing_tablas_columnas_ddl_rejected passed")
        
        print("Running test_missing_sql_reference_rejected...")
        test_missing_sql_reference_rejected()
        print("✓ test_missing_sql_reference_rejected passed")
        
        print("Running test_valid_required_fields_accepted...")
        test_valid_required_fields_accepted()
        print("✓ test_valid_required_fields_accepted passed")
        
        print()
        print("🎉 All property tests passed!")
        print("Property 1: Required field validation - PASSED")
        print("**Validates: Requirements 1.2**")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_required_field_validation_tests()
    sys.exit(0 if success else 1)