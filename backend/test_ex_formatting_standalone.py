#!/usr/bin/env python3
"""
Standalone test for EX formatting property test
"""

import sys
import os
from uuid import uuid4
from datetime import datetime
import re

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.models.execution_accuracy import ExecutionAccuracy
from app.services.execution_accuracy_service import ExecutionAccuracyService
from app.repositories.execution_accuracy_repository import ExecutionAccuracyRepository


def test_ex_formatting_two_decimal_places():
    """
    **Feature: text-to-sql-evaluation, Property 7: EX formatting**
    **Validates: Requirements 3.3**
    
    For any calculated EX value, when displayed, it should be formatted 
    with exactly two decimal places
    """
    print("Testing EX formatting with two decimal places...")
    
    # Create service
    repository = ExecutionAccuracyRepository(None)  # We won't use the actual DB
    service = ExecutionAccuracyService(repository)
    
    # Test various scenarios
    test_cases = [
        # (correct_count, total_count, expected_result)
        (1, 3, 33.33),  # 1/3 = 33.333... -> 33.33
        (2, 3, 66.67),  # 2/3 = 66.666... -> 66.67
        (1, 7, 14.29),  # 1/7 = 14.285714... -> 14.29
        (1, 6, 16.67),  # 1/6 = 16.666... -> 16.67
        (3, 4, 75.0),   # 3/4 = 75.0
        (5, 5, 100.0),  # 5/5 = 100.0
        (0, 5, 0.0),    # 0/5 = 0.0
        (7, 9, 77.78),  # 7/9 = 77.777... -> 77.78
    ]
    
    for correct_count, total_count, expected in test_cases:
        # Create test records
        records = []
        
        # Add correct records
        for _ in range(correct_count):
            records.append(ExecutionAccuracy(
                id=uuid4(),
                evaluation_id=uuid4(),
                is_correct=True,
                created_at=datetime.now()
            ))
        
        # Add incorrect records
        for _ in range(total_count - correct_count):
            records.append(ExecutionAccuracy(
                id=uuid4(),
                evaluation_id=uuid4(),
                is_correct=False,
                created_at=datetime.now()
            ))
        
        # Calculate EX
        result = service.calculate_ex(records)
        
        # Check result
        print(f"  {correct_count}/{total_count}: Expected {expected}, Got {result}")
        
        # Verify the result matches expected
        assert result == expected, f"Expected {expected}, got {result}"
        
        # Verify it's a float
        assert isinstance(result, float), f"Result should be float, got {type(result)}"
        
        # Check decimal places in string representation
        result_str = str(result)
        if '.' in result_str:
            decimal_part = result_str.split('.')[1]
            assert len(decimal_part) <= 2, f"Result {result_str} has more than 2 decimal places"
        
        # Check regex pattern for proper formatting
        decimal_pattern = r'^\d+(\.\d{1,2})?$'
        assert re.match(decimal_pattern, result_str), f"Result {result_str} doesn't match decimal pattern"
    
    print("✅ All EX formatting tests passed!")
    return True


def test_ex_formatting_edge_cases():
    """Test edge cases for EX formatting"""
    print("Testing EX formatting edge cases...")
    
    repository = ExecutionAccuracyRepository(None)
    service = ExecutionAccuracyService(repository)
    
    # Test empty list
    result = service.calculate_ex([])
    assert result == 0.0, f"Empty list should return 0.0, got {result}"
    print(f"  Empty list: {result} ✅")
    
    # Test single correct
    single_correct = [ExecutionAccuracy(
        id=uuid4(),
        evaluation_id=uuid4(),
        is_correct=True,
        created_at=datetime.now()
    )]
    result = service.calculate_ex(single_correct)
    assert result == 100.0, f"Single correct should return 100.0, got {result}"
    print(f"  Single correct: {result} ✅")
    
    # Test single incorrect
    single_incorrect = [ExecutionAccuracy(
        id=uuid4(),
        evaluation_id=uuid4(),
        is_correct=False,
        created_at=datetime.now()
    )]
    result = service.calculate_ex(single_incorrect)
    assert result == 0.0, f"Single incorrect should return 0.0, got {result}"
    print(f"  Single incorrect: {result} ✅")
    
    print("✅ All edge case tests passed!")
    return True


def run_all_tests():
    """Run all EX formatting tests"""
    print("Running EX Formatting Property Tests")
    print("=" * 50)
    
    try:
        test_ex_formatting_two_decimal_places()
        test_ex_formatting_edge_cases()
        
        print("\n🎉 All EX formatting property tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)