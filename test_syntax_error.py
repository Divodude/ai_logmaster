"""
Test script with SYNTAX ERROR
This will trigger the agent to:
1. Classify as "syntax" error
2. Fetch documentation from DuckDuckGo
3. Use AI to analyze with docs
4. Show 1 API call
"""

def broken_function():
    print("Starting complex operation...")
    
    # This has a syntax error
    if True:
        print("This will fail")
    
    return "success"

if __name__ == "__main__":
    broken_function()
