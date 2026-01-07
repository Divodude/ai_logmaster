"""
Test script with TYPE ERROR
This will trigger the agent to:
1. Classify as "type" error
2. Fetch documentation from DuckDuckGo
3. Use AI to analyze with docs
4. Show 1 API call
"""

def calculate_average(numbers):
    print("Calculating average...")
    
    # This will cause a TypeError
    total = sum(numbers)
    count = len(numbers)
    
    # Trying to divide by a string (wrong type)
    average = total / "invalid"
    
    return average

if __name__ == "__main__":
    data = [10, 20, 30, 40, 50]
    result = calculate_average(data)
    print(f"Average: {result}")
