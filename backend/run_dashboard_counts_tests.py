#!/usr/bin/env python3
"""
Standalone test runner for dashboard counts accuracy property tests
"""

import sys
import os
import asyncio

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.property.test_dashboard_counts_accuracy import (
    test_dashboard_total_queries_count,
    test_dashboard_evaluated_queries_count,
    test_dashboard_progress_percentage,
    test_dashboard_counts_empty_dataset,
    test_dashboard_counts_all_evaluated,
    test_dashboard_counts_none_evaluated,
    test_dashboard_counts_partial_evaluation,
    test_dashboard_counts_consistency,
    MockGoldQuery
)

def run_property_tests():
    """Run all dashboard counts accuracy property tests"""
    print("Running Property 19: Dashboard counts accuracy tests...")
    print("=" * 60)
    
    try:
        # Test 1: Empty dataset
        print("✓ Testing empty dataset handling...")
        test_dashboard_counts_empty_dataset()
        
        # Test 2: Consistency invariants
        print("✓ Testing consistency invariants...")
        test_dashboard_counts_consistency()
        
        # Test 3: All evaluated scenario
        print("✓ Testing all queries evaluated scenario...")
        # Run the hypothesis test which will generate its own inputs
        test_dashboard_counts_all_evaluated()
        
        # Test 4: None evaluated scenario
        print("✓ Testing no queries evaluated scenario...")
        # Run the hypothesis test which will generate its own inputs
        test_dashboard_counts_none_evaluated()
        
        # Test 5: Partial evaluation scenario
        print("✓ Testing partial evaluation scenario...")
        # Run the hypothesis test which will generate its own inputs
        test_dashboard_counts_partial_evaluation()
        
        print("=" * 60)
        print("✅ All dashboard counts accuracy property tests passed!")
        
        # Run hypothesis-based property tests
        print("\n🔄 Running Hypothesis property tests...")
        print("This may take a moment as it generates random test cases...")
        
        # These will run with Hypothesis generating random inputs
        test_dashboard_total_queries_count()
        test_dashboard_evaluated_queries_count()
        test_dashboard_progress_percentage()
        
        print("✅ All Hypothesis property tests passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_property_tests()
    sys.exit(0 if success else 1)