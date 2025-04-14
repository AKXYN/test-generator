import streamlit as st
import os
from dotenv import load_dotenv
import time
import json

# Import utility modules
from utils.firebase_utils import login_user, save_core_values, get_core_values, save_test
from utils.llm_interface import generate_questions

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Core Values Test Generator",
    page_icon="🎯",
    layout="wide"
)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'core_values' not in st.session_state:
    st.session_state.core_values = []
if 'test_data' not in st.session_state:
    st.session_state.test_data = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# Main function
def main():
    # App title
    st.title("Core Values Test Generator")
    
    # Page routing
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "core_values":
        core_values_page()
    elif st.session_state.page == "generate_test":
        test_generation_page()

# Login page
def login_page():
    st.subheader("Login")
    
    # Debug information
    with st.expander("Debug Information"):
        st.write("Using hardcoded Firebase configuration")
        st.write("Firebase Project ID: corevaluesapp-9ca55")
        st.write("Session State:", st.session_state)
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
    
    if submit_button:
        st.write("Attempting login with email:", email)
        user = login_user(email, password)
        if user:
            st.session_state.user = user
            st.session_state.page = "core_values"
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid email or password")
            st.write("Login failed. Check the debug information above for details.")
    
    # Register link
    st.markdown("Don't have an account? [Register here](https://akxyn.github.io/core-values/auth.html)")

# Core values page
def core_values_page():
    st.subheader("Define Your Core Values")
    
    # Get user ID from session state
    user_id = st.session_state.user.get("uid") or st.session_state.user.get("localId")
    id_token = st.session_state.user.get("idToken")
    
    # Debug information
    with st.expander("Debug Information"):
        st.write("User ID:", user_id)
        st.write("Session State:", st.session_state)
    
    # Load existing core values
    if not st.session_state.core_values:
        st.session_state.core_values = get_core_values(user_id, id_token)
        st.write("Loaded core values from database:", st.session_state.core_values)
    
    # Display existing core values
    if st.session_state.core_values:
        st.write("Your current core values:")
        for i, value in enumerate(st.session_state.core_values):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{value['name']}**: {value['description']}")
            with col2:
                if st.button("Delete", key=f"delete_{i}"):
                    st.session_state.core_values.pop(i)
                    save_core_values(user_id, st.session_state.core_values, id_token)
                    st.rerun()
    else:
        st.info("No core values found. Please add some below.")
    
    # Add new core value
    st.write("Add a new core value:")
    with st.form("core_value_form"):
        name = st.text_input("Name")
        description = st.text_area("Description")
        submit_button = st.form_submit_button("Add Core Value")
    
    if submit_button and name and description:
        new_core_value = {
            "name": name,
            "description": description
        }
        st.session_state.core_values.append(new_core_value)
        save_core_values(user_id, st.session_state.core_values, id_token)
        st.success(f"Core value '{name}' added successfully!")
        st.rerun()
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Login"):
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()
    with col2:
        if st.button("Generate Test"):
            st.session_state.page = "generate_test"
            st.rerun()

# Test generation page
def test_generation_page():
    """Page for generating tests based on core values."""
    if "user" not in st.session_state:
        st.error("Please log in to access this page.")
        return
    
    user = st.session_state.user
    company_name = user.get("email", "").split("@")[1].split(".")[0]
    id_token = user.get("idToken")
    
    st.title("Generate Test")
    
    # Get test name and number of questions
    test_name = st.text_input("Test Name", "Core Values Assessment")
    num_questions = st.number_input("Number of Questions", min_value=5, max_value=20, value=10)
    
    # Debug information
    with st.expander("Debug Information"):
        st.write("User ID:", user.get("uid"))
        st.write("Session State:", st.session_state)
        
        # Get core values from the database
        core_values = get_core_values(user["uid"], id_token)
        st.write("Core Values from Database:", core_values)
    
    if st.button("Generate Test"):
        with st.spinner("Generating test questions..."):
            # Get core values from the database
            core_values = get_core_values(user["uid"], id_token)
            
            if not core_values:
                st.error("Please add core values first.")
                return
            
            # Generate test questions
            questions = generate_questions(core_values, num_questions)
            
            if not questions:
                st.error("Failed to generate questions. Please try again.")
                return
                
            test_data = {
                "name": test_name,
                "company": company_name,
                "core_values": core_values,
                "questions": questions
            }
            
            # Save test to Firebase
            test_id = save_test(user["uid"], test_data, id_token)
            
            if test_id:
                st.success("Test generated successfully!")
                st.info("Please refresh your dashboard to see the new test.")
                
                # Display test data for debugging
                with st.expander("View Generated Test"):
                    st.json(test_data)
                
                # Provide download option
                st.download_button(
                    "Download Test as JSON",
                    data=json.dumps(test_data, indent=2),
                    file_name=f"{test_name.lower().replace(' ', '_')}.json",
                    mime="application/json"
                )
                
                # Add button to view in dashboard
                if st.button("View in Dashboard"):
                    st.markdown(f"[Open Dashboard](https://{company_name}.github.io/core-values-app/dashboard.html)")
            else:
                st.error("Failed to save test. Please try again.")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Core Values"):
            st.session_state.page = "core_values"
            st.rerun()
    with col2:
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
