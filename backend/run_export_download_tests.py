#!/usr/bin/env python3
"""
Test runner for export download availability property tests
"""

import sys
import subprocess
import os

def main():
    """Run the export download availability property tests"""
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Running Property 25: Export download availability tests...")
    print("=" * 60)
    
    # Run the specific test file
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/property/test_export_download_availability.py",
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print("\n✅ All export download availability tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print("STDOUT:")
        print(e.stdout)
        print("STDERR:")
        print(e.stderr)
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)