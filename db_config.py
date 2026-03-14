from pymongo import MongoClient
import sys

def get_db_connection():
    try:
        # Standard MongoDB URI
        connection_string = "mongodb://localhost:27017"
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Check if server is available
        client.server_info() 
        return client.campus_lost_found
    except Exception as e:
        print(f"Error: Could not connect to MongoDB. {e}")
        sys.exit(1)

# Initialize the database and collections
db = get_db_connection()

# The three collections required for the matching system
lost_items = db.lost_items
found_items = db.found_items
alerts = db.alerts