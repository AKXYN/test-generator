import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Firebase configuration
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_DATABASE_URL = f"https://{FIREBASE_PROJECT_ID}.firebaseio.com"
FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
FIREBASE_FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

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
        # Get Firebase config from environment variables
        firebase_config = {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.getenv("FIREBASE_APP_ID")
        }
        
        # Debug: Print all environment variables (without sensitive values)
        print("Environment Variables Check:")
        for key in firebase_config:
            value = firebase_config[key]
            if value:
                masked_value = value[:5] + "..." if len(value) > 5 else "***"
                print(f"{key}: {masked_value}")
            else:
                print(f"{key}: Not set!")
        
        # Get Firestore URL for authentication
        firestore_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_config['apiKey']}"
        
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
        print(f"URL: {firestore_url}")
        print(f"Email: {email}")
        print(f"Headers: {headers}")
        
        # Make the request to Firebase
        response = requests.post(
            firestore_url,
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
def save_core_values(user_id, core_values, id_token=None):
    """
    Save core values to Firestore.
    
    Args:
        user_id (str): The user's ID.
        core_values (list): List of core value objects with name and description.
        id_token (str, optional): The ID token for authentication
    
    Returns:
        bool: True if successful, False otherwise.
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
        
        # Construct Firestore URL
        project_id = firebase_config["projectId"]
        document_id = "core_values"  # Use a fixed document ID
        firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}/core_values/{document_id}"
        
        print(f"Saving core values to URL: {firestore_url}")
        
        # Format data for Firestore
        data = {
            "fields": {
                "values": {
                    "arrayValue": {
                        "values": [
                            {
                                "mapValue": {
                                    "fields": {
                                        "name": {"stringValue": value["name"]},
                                        "description": {"stringValue": value["description"]}
                                    }
                                }
                            }
                            for value in core_values
                        ]
                    }
                },
                "lastUpdated": {
                    "timestampValue": datetime.now().isoformat() + "Z"
                }
            }
        }
        
        # Print debug information
        print(f"Saving core values to Firestore: {json.dumps(data, indent=2)}")
        
        # Set up headers
        headers = {
            "Content-Type": "application/json",
            "X-Firebase-Project-ID": project_id
        }
        
        # Add ID token if provided
        if id_token:
            headers["Authorization"] = f"Bearer {id_token}"
            print(f"Using ID token: {id_token[:20]}...")
        else:
            print("No ID token provided")
        
        # Send request to Firestore
        response = requests.patch(
            firestore_url,
            headers=headers,
            data=json.dumps(data)
        )
        
        # Print response information
        print(f"Firestore response status: {response.status_code}")
        print(f"Firestore response content: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error saving core values: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def get_core_values(user_id, id_token=None):
    """
    Get core values from Firestore using REST API.
    
    Args:
        user_id (str): User ID
        id_token (str, optional): The ID token for authentication
        
    Returns:
        list: List of core values
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
        project_id = firebase_config["projectId"]
        document_id = "core_values"  # Use a fixed document ID
        firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}/core_values/{document_id}"
        
        print(f"Fetching core values from URL: {firestore_url}")
        
        # Set up headers
        headers = {
            "Content-Type": "application/json",
            "X-Firebase-Project-ID": project_id
        }
        
        # Add ID token if provided
        if id_token:
            headers["Authorization"] = f"Bearer {id_token}"
            print(f"Using ID token: {id_token[:20]}...")
        else:
            print("No ID token provided")
        
        # Make the request to Firestore
        response = requests.get(firestore_url, headers=headers)
        
        print(f"Firestore response status: {response.status_code}")
        print(f"Firestore response content: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Parsed JSON data: {json.dumps(data, indent=2)}")
            
            # If the document doesn't exist yet, create it with an empty values array
            if not data or "fields" not in data:
                print("Document does not exist, creating it with empty values array")
                initial_data = {
                    "fields": {
                        "values": {
                            "arrayValue": {
                                "values": []
                            }
                        },
                        "lastUpdated": {
                            "timestampValue": datetime.now().isoformat() + "Z"
                        }
                    }
                }
                
                # Create the document
                create_response = requests.patch(
                    firestore_url,
                    headers=headers,
                    data=json.dumps(initial_data)
                )
                
                if create_response.status_code == 200:
                    print("Document created successfully")
                    return []
                else:
                    print(f"Error creating document: {create_response.status_code}")
                    print(f"Response: {create_response.text}")
                    return []
            
            # If the document exists, extract the core values
            if "fields" in data and "values" in data["fields"]:
                print("Values field found")
                core_values = []
                for value in data["fields"]["values"]["arrayValue"]["values"]:
                    if "mapValue" in value and "fields" in value["mapValue"]:
                        fields = value["mapValue"]["fields"]
                        core_values.append({
                            "name": fields["name"]["stringValue"],
                            "description": fields["description"]["stringValue"]
                        })
                print(f"Retrieved core values: {core_values}")
                return core_values
            else:
                print("No 'values' field found in response")
        
        print(f"Error getting core values: {response.status_code}")
        print(f"Response: {response.text}")
        return []
    except Exception as e:
        print(f"Error in get_core_values: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return []

# Test functions
def save_test(user_id, test_data, id_token=None):
    """
    Save a test to Firestore.
    
    Args:
        user_id (str): The user ID
        test_data (dict): The test data to save
        id_token (str, optional): The ID token for authentication
    
    Returns:
        str: The ID of the saved test, or None if saving failed
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
        
        # Get Firestore URL
        firestore_url = f"https://firestore.googleapis.com/v1/projects/{firebase_config['projectId']}/databases/(default)/documents/tests"
        
        # Create ISO format timestamps
        now = datetime.now()
        start_date = now
        end_date = now + timedelta(days=30)  # Set end date to 30 days from now
        
        # Format the questions for Firestore
        formatted_questions = []
        for q in test_data["questions"]:
            # Format core values as an array
            core_values_array = {
                "arrayValue": {
                    "values": [{"stringValue": cv} for cv in q["core_values"]]
                }
            }
            
            # Format options as an array of maps
            formatted_options = []
            for opt in q["options"]:
                option_map = {
                    "mapValue": {
                        "fields": {
                            "text": {"stringValue": opt["text"]},
                            "score": {"integerValue": opt["score"]}
                        }
                    }
                }
                formatted_options.append(option_map)
            
            options_array = {
                "arrayValue": {
                    "values": formatted_options
                }
            }
            
            # Create the formatted question
            formatted_question = {
                "mapValue": {
                    "fields": {
                        "id": {"integerValue": q["id"]},
                        "text": {"stringValue": q["text"]},
                        "core_values": core_values_array,
                        "options": options_array
                    }
                }
            }
            formatted_questions.append(formatted_question)
        
        # Format the test data for Firestore
        firestore_data = {
            "fields": {
                "userId": {"stringValue": user_id},
                "name": {"stringValue": test_data["name"]},
                "company": {"stringValue": test_data["company"]},
                "description": {"stringValue": test_data.get("description", "")},
                "coreValues": {"arrayValue": {"values": [{"stringValue": cv["name"] if isinstance(cv, dict) and "name" in cv else str(cv)} for cv in test_data["core_values"]]}},
                "questions": {"arrayValue": {"values": formatted_questions}},
                "status": {"stringValue": "draft"},
                "createdAt": {"timestampValue": now.isoformat() + "Z"},
                "startDate": {"timestampValue": start_date.isoformat() + "Z"},
                "endDate": {"timestampValue": end_date.isoformat() + "Z"}
            }
        }
        
        # Set up headers
        headers = {
            "Content-Type": "application/json",
            "X-Firebase-Project-ID": firebase_config["projectId"]
        }
        
        # Add ID token if provided
        if id_token:
            headers["Authorization"] = f"Bearer {id_token}"
        
        # Make the request to Firestore
        response = requests.post(
            firestore_url,
            headers=headers,
            json=firestore_data
        )
        
        # Check response
        if response.status_code == 200:
            # Extract the document ID from the response
            doc_id = response.json().get("name", "").split("/")[-1]
            print(f"Test saved successfully with ID: {doc_id}")
            return doc_id
        else:
            print(f"Error saving test: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error in save_test: {str(e)}")
        return None 
