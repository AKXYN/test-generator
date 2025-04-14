import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_core_values(user_id):
    """
    Debug function to check core values in Firestore.
    
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
        
        # Make the request to Firestore
        response = requests.get(firestore_url)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if "fields" in data and "values" in data["fields"]:
                core_values = []
                for value in data["fields"]["values"]["arrayValue"]["values"]:
                    if "mapValue" in value and "fields" in value["mapValue"]:
                        fields = value["mapValue"]["fields"]
                        core_values.append({
                            "name": fields["name"]["stringValue"],
                            "description": fields["description"]["stringValue"]
                        })
                print(f"Retrieved core values: {json.dumps(core_values, indent=2)}")
                return core_values
        
        print(f"Error getting core values: {response.status_code}")
        print(f"Response: {response.text}")
        return []
    except Exception as e:
        print(f"Error in debug_core_values: {str(e)}")
        return []

if __name__ == "__main__":
    # Replace with your user ID
    user_id = input("Enter your user ID: ")
    debug_core_values(user_id) 