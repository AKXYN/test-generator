import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Firebase configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyCuRBnVEgZ4EVFi6ZvIthFm_IUsLxD22bc",
    "authDomain": "corevaluesapp-9ca55.firebaseapp.com",
    "projectId": "corevaluesapp-9ca55",
    "storageBucket": "corevaluesapp-9ca55.appspot.com",
    "messagingSenderId": "110268466622836450181",
    "appId": "1:894079508319:web:8c7cc5a0389b87939d20ea"
}

# Firebase URLs
FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_CONFIG['apiKey']}"
FIREBASE_FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['projectId']}/databases/(default)/documents"

# Authentication functions
def login_user(email, password):
    """
    Login a user with email and password.
    
    Args:
        email (str): User's email
        password (str): User's password
        
    Returns:
        dict: User data if login successful, None otherwise
    """
    try:
        print("Using hardcoded Firebase config")
        print(f"API Key: {FIREBASE_CONFIG['apiKey'][:5]}...")
        print(f"Auth Domain: {FIREBASE_CONFIG['authDomain']}")
        print(f"App ID: {FIREBASE_CONFIG['appId']}")
        
        # Set up headers
        headers = {
            "Content-Type": "application/json"
        }
        
        # Set up request data
        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        print(f"\nAttempting login with:")
        print(f"URL: {FIREBASE_AUTH_URL}")
        print(f"Email: {email}")
        print(f"Headers: {headers}")
        
        # Make the request to Firebase
        response = requests.post(
            FIREBASE_AUTH_URL,
            headers=headers,
            json=data
        )
        
        print(f"\nFirebase response:")
        print(f"Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            # Extract user data from response
            user_data = response.json()
            print(f"Login successful for user: {user_data.get('email')}")
            return user_data
        else:
            print(f"Login failed with status code: {response.status_code}")
            print(f"Error message: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error in login_user: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

# Core values functions
def save_core_values(user_id, core_values, id_token):
    """
    Save core values for a user to Firestore.
    
    Args:
        user_id (str): User ID
        core_values (list): List of core values
        id_token (str): Firebase ID token
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get Firestore URL for core values
        firestore_url = f"{FIREBASE_FIRESTORE_URL}/users/{user_id}/core_values/core_values"
        
        print(f"\nSaving core values to URL: {firestore_url}")
        print(f"Using ID token: {id_token[:20]}...")
        
        # Set up headers
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }
        
        # Format core values for Firestore
        values = []
        for cv in core_values:
            if isinstance(cv, dict):
                values.append({
                    "mapValue": {
                        "fields": {
                            "name": {"stringValue": cv.get("name", "")},
                            "description": {"stringValue": cv.get("description", "")}
                        }
                    }
                })
            else:
                values.append({
                    "mapValue": {
                        "fields": {
                            "name": {"stringValue": str(cv)},
                            "description": {"stringValue": ""}
                        }
                    }
                })
        
        # Set up request data
        data = {
            "fields": {
                "values": {
                    "arrayValue": {
                        "values": values
                    }
                },
                "lastUpdated": {
                    "timestampValue": datetime.now().isoformat() + "Z"
                }
            }
        }
        
        # Always use PATCH - Firestore will create the document if it doesn't exist
        response = requests.patch(
            firestore_url,
            headers=headers,
            json=data
        )
        
        print(f"Save response status: {response.status_code}")
        print(f"Save response content: {response.text}")
        
        success = response.status_code in [200, 201]
        print(f"Save operation {'successful' if success else 'failed'}")
        return success
            
    except Exception as e:
        print(f"Error in save_core_values: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def get_core_values(user_id, id_token):
    """
    Get core values for a user from Firestore.
    
    Args:
        user_id (str): User ID
        id_token (str): Firebase ID token
        
    Returns:
        list: List of core values
    """
    try:
        # Get Firestore URL for core values
        firestore_url = f"{FIREBASE_FIRESTORE_URL}/users/{user_id}/core_values/core_values"
        
        print(f"\nFetching core values from URL: {firestore_url}")
        print(f"Using ID token: {id_token[:20]}...")
        print(f"Full URL being used: {firestore_url}")
        print(f"Project ID from config: {FIREBASE_CONFIG['projectId']}")
        
        # Set up headers
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }
        
        print(f"Request headers: {headers}")
        
        # Make the request to Firestore
        response = requests.get(
            firestore_url,
            headers=headers
        )
        
        print(f"Firestore response status: {response.status_code}")
        print(f"Firestore response content: {response.text}")
        
        if response.status_code == 200:
            # Extract core values from response
            data = response.json()
            print(f"Parsed JSON response: {json.dumps(data, indent=2)}")
            
            if "fields" in data and "values" in data["fields"]:
                core_values = data["fields"]["values"]["arrayValue"]["values"]
                # Convert each map value to a dictionary
                result = []
                for cv in core_values:
                    if "mapValue" in cv:
                        fields = cv["mapValue"]["fields"]
                        result.append({
                            "name": fields.get("name", {}).get("stringValue", ""),
                            "description": fields.get("description", {}).get("stringValue", "")
                        })
                    else:
                        # Handle legacy format or other formats
                        result.append({
                            "name": cv.get("stringValue", ""),
                            "description": ""
                        })
                print(f"Processed core values: {json.dumps(result, indent=2)}")
                return result
            print("No fields or values found in response")
            return []
        elif response.status_code == 404:
            print("Document not found (404)")
            return []
        else:
            print(f"Error getting core values: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"Error in get_core_values: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return []

# Test functions
def save_test(user_id, test_data, id_token):
    """
    Save a test to Firestore.
    
    Args:
        user_id (str): User ID
        test_data (dict): Test data
        id_token (str): Firebase ID token
        
    Returns:
        str: Test ID if successful, None otherwise
    """
    try:
        # Get Firestore URL for tests
        firestore_url = f"{FIREBASE_FIRESTORE_URL}/users/{user_id}/tests"
        
        print(f"\nSaving test to URL: {firestore_url}")
        print(f"Using ID token: {id_token[:20]}...")
        
        # Set up headers
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }
        
        # Format test data for Firestore
        formatted_data = {
            "fields": {
                "name": {"stringValue": test_data["name"]},
                "company": {"stringValue": test_data["company"]},
                "coreValues": {
                    "arrayValue": {
                        "values": [{"stringValue": cv["name"]} for cv in test_data["core_values"]]
                    }
                },
                "questions": {
                    "arrayValue": {
                        "values": [
                            {
                                "mapValue": {
                                    "fields": {
                                        "text": {"stringValue": q["text"]},
                                        "options": {
                                            "arrayValue": {
                                                "values": [
                                                    {
                                                        "mapValue": {
                                                            "fields": {
                                                                "text": {"stringValue": opt["text"]},
                                                                "score": {"integerValue": opt["score"]}
                                                            }
                                                        }
                                                    } for opt in q["options"]
                                                ]
                                            }
                                        }
                                    }
                                }
                            } for q in test_data["questions"]
                        ]
                    }
                },
                "createdAt": {"timestampValue": datetime.now().isoformat() + "Z"},
                "updatedAt": {"timestampValue": datetime.now().isoformat() + "Z"}
            }
        }
        
        # Make the request to Firestore
        response = requests.post(
            firestore_url,
            headers=headers,
            json=formatted_data
        )
        
        print(f"Firestore response status: {response.status_code}")
        print(f"Firestore response content: {response.text}")
        
        if response.status_code == 201:
            # Extract test ID from response
            data = response.json()
            return data["name"].split("/")[-1]
        else:
            print(f"Error saving test: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error in save_test: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None 
