"""
Test script with UNKNOWN/CUSTOM ERROR
This will trigger the agent to:
1. Classify as "unknown" error
2. Fetch documentation from DuckDuckGo
3. Use AI to analyze with docs
4. Show 1 API call
"""

class CustomDatabaseException(Exception):
    """Custom exception that the agent won't recognize"""
    pass

def connect_to_custom_db():
    print("Attempting to connect to custom database...")
    print("Initializing connection pool...")
    
    # Raise a custom exception
    raise CustomDatabaseException(
        "Failed to authenticate with custom database: "
        "Invalid credentials or database schema mismatch. "
        "Error code: DB_AUTH_FAIL_0x4A2"
    )

if __name__ == "__main__":
    connect_to_custom_db()
