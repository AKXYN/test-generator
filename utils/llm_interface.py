import os
import json
import requests
import streamlit as st
from typing import List, Dict, Tuple, Optional

# Hugging Face API settings
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS = {
    "Authorization": f"Bearer {st.secrets['secrets']['HF_API_KEY']}"
}

def generate_questions(core_values: List[Dict[str, str]], num_questions: int = 10) -> Tuple[List[Dict[str, str]], Optional[str]]:
    """
    Generate questions using Hugging Face's Inference API
    Returns a tuple of (questions, error_message)
    """
    try:
        num_questions = int(num_questions)
        core_values_text = "\n".join([
            f"- {cv['name']}: {cv['description']}"
            for cv in core_values
        ])

        # Improved prompt for better JSON formatting
        prompt = f"""<s>[INST] You are an expert in creating assessment questions for company core values.
Given these core values:
{core_values_text}

Generate {num_questions} multiple-choice questions with these requirements:
1. Specific to one or more core values
2. Realistic workplace scenarios
3. 4 answer options with scores (8,6,4,2)
4. Make sure that it is impossible to guess the option with the highest score. Each option should be a equally viable solution in the workplace
5. Return ONLY a valid JSON array formatted like:
[
  {{
    "id": 1,
    "text": "Question text",
    "core_values": ["Value1"],
    "options": [
      {{"text": "Option A", "score": 8}},
      {{"text": "Option B", "score": 6}}
    ]
  }}
][/INST]
</s>"""

        # Call Hugging Face API
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={
                "inputs": prompt,
                "parameters": {
                    "temperature": 0.7,
                    "max_new_tokens": 2000,
                    "return_full_text": False
                }
            }
        )

        if response.status_code != 200:
            return create_sample_questions(core_values, num_questions), f"API Error: {response.text}"

        # Try to extract valid JSON
        try:
            response_text = response.json()[0]['generated_text']
            questions = json.loads(response_text.strip())
            return questions, None
        except (json.JSONDecodeError, KeyError) as e:
            error_msg = f"JSON parsing failed: {str(e)}. Response: {response_text[:200]}..."
            return create_sample_questions(core_values, num_questions), error_msg
            
    except Exception as e:
        error_msg = f"Error generating questions: {str(e)}"
        return create_sample_questions(core_values, num_questions), error_msg

# Keep create_sample_questions() function the same as before

def create_sample_questions(core_values, num_questions):
    """
    Create sample questions based on core values.
    This is a fallback function used when AI generation fails.
    """
    # Ensure num_questions is an integer
    num_questions = int(num_questions)
    
    # Create sample questions
    questions = []
    for i in range(num_questions):
        # Get a core value (cycle through them if needed)
        core_value = core_values[i % len(core_values)]
        
        # Extract core value name
        if isinstance(core_value, dict):
            core_value_name = core_value.get('name', 'Unknown')
        else:
            core_value_name = str(core_value)
        
        question = {
            "id": i + 1,
            "text": f"Sample question {i+1} about {core_value_name}?",
            "core_values": [core_value_name],
            "options": [
                {"text": "Option A", "score": 8},
                {"text": "Option B", "score": 6},
                {"text": "Option C", "score": 4},
                {"text": "Option D", "score": 2}
            ]
        }
        questions.append(question)
    
    return questions 
