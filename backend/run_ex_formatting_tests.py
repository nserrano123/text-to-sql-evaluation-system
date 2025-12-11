#!/usr/bin/env python3
"""
Standalone test runner for EX formatting property tests
"""

import sys
import os
import subprocess

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def run_ex_formatting_tests():
    """Run the EX formatting property tests"""
    print("Running EX formatting property tests...")
    print("=" * 50)
    
    # Run the specific test file
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/property/test_ex_formatting.py",
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=backend_dir, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nTest execution completed with return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ All EX formatting tests passed!")
        else:
            print("❌ Some EX formatting tests failed!")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_ex_formatting_tests()
    sys.exit(0 if success else 1)