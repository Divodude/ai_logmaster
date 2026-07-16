"""
Test script that intentionally fails for demonstration
"""
import sys

def buggy_function():
    print("Starting application...")
    print("Connecting to database...")
    a = 10
    b = 0
    
    # This will fail
    raise ZeroDivisionError("Division by zero")
    print(a/b)
    

if __name__ == "__main__":
    buggy_function()
