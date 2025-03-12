import os
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt
from datetime import datetime

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment variable
MONGODB_URI = os.getenv("MONGODB_URI")

try:
    # Connect to MongoDB Atlas
    client = MongoClient(MONGODB_URI)
    # Send a ping to confirm a successful connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"Error connecting to MongoDB Atlas: {e}")

# Get database and collections
db = client["date_tracker"]
users_col = db["users"]
dates_col = db["dates"]

def add_date(username, date):
    """Add a date to the dates collection."""
    try:
        new_date = {
            "username": username,
            "date": date,
            "timestamp": datetime.now()
        }
        dates_col.insert_one(new_date)
        return True
    except Exception as e:
        print(f"Error adding date: {e}")
        return False

def get_dates(username):
    """Get all dates for a user."""
    try:
        dates = dates_col.find({"username": username})
        return [d["date"] for d in dates]
    except Exception as e:
        print(f"Error getting dates: {e}")
        return []

def delete_date(username, date_to_delete):
    """Delete a specific date from the dates collection."""
    try:
        dates_col.delete_one({
            "username": username,
            "date": date_to_delete
        })
        return True
    except Exception as e:
        print(f"Error deleting date: {e}")
        return False

def delete_record(username):
    """Delete all dates for a user."""
    try:
        dates_col.delete_many({"username": username})
        return True
    except Exception as e:
        print(f"Error deleting records: {e}")
        return False

def register_user(username, password):
    """Register a new user."""
    try:
        if users_col.find_one({"username": username}):
            return False
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users_col.insert_one({
            "username": username,
            "password": hashed_password
        })
        return True
    except Exception as e:
        print(f"Error registering user: {e}")
        return False

def authenticate_user(username, password):
    """Authenticate a user."""
    try:
        user = users_col.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            return True
        return False
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return False

def update_password(username, new_password):
    """Update user's password."""
    try:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        users_col.update_one(
            {"username": username},
            {"$set": {"password": hashed_password}}
        )
        return True
    except Exception as e:
        print(f"Error updating password: {e}")
        return False

def edit_date(username, old_date, new_date):
    """Edit a date for a user."""
    try:
        dates_col.update_one(
            {"username": username, "date": old_date},
            {"$set": {"date": new_date, "timestamp": datetime.now()}}
        )
        return True
    except Exception as e:
        print(f"Error editing date: {e}")
        return False 