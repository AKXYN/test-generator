import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def add_test_core_value(user_id):
    """
    Add a test core value to Firestore.
    
    Args:
        user_id (str): User ID
    """
    try:
        # Get Firebase config from environment variables
        firebase_config = {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.getenv("FIREBASE_APP_ID")
        }
        
        # Get Firestore URL for the user's core values document
        firestore_url = f"https://firestore.googleapis.com/v1/projects/{firebase_config['projectId']}/databases/(default)/documents/users/{user_id}/core_values"
        
        # Create a test core value
        test_core_value = {
            "name": "Test Core Value",
            "description": "This is a test core value"
        }
        
        # Format the data for Firestore
        data = {
            "fields": {
                "values": {
                    "arrayValue": {
                        "values": [
                            {
                                "mapValue": {
                                    "fields": {
                                        "name": {"stringValue": test_core_value["name"]},
                                        "description": {"stringValue": test_core_value["description"]}
                                    }
                                }
                            }
                        ]
                    }
                },
                "updated_at": {
                    "timestampValue": datetime.now(datetime.timezone.utc).isoformat()
                }
            }
        }
        
        # Send the request to Firestore
        response = requests.patch(firestore_url, json=data)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [200, 201]:
            print(f"Test core value added successfully: {test_core_value}")
            return True
        else:
            print(f"Error adding test core value: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error in add_test_core_value: {str(e)}")
        return False

if __name__ == "__main__":
    # Replace with your user ID
    user_id = input("Enter your user ID: ")
    add_test_core_value(user_id) 