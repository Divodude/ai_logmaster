"""
Test script that intentionally fails for demonstration
"""
import sys

def buggy_function():
    print("Starting application...")
    print("Connecting to database...")
    
    # This will fail
    # raise ConnectionRefusedError("Connection refused to database at localhost:5432")

if __name__ == "__main__":
    buggy_function()
