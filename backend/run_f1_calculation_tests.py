#!/usr/bin/env python3
"""
Runner script for F1 score calculation property tests
"""

import sys
import subprocess

def run_f1_calculation_tests():
    """Run the F1 score calculation property tests"""
    print("Running F1 score calculation property tests...")
    
    try:
        # Run the specific test file
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/property/test_f1_score_calculation.py",
            "-v", "--tb=short"
        ], cwd=".", capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return code: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_f1_calculation_tests()
    sys.exit(0 if success else 1)