import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_questions(core_values, num_questions):
    """
    Generate questions based on core values using OpenAI API.
    
    Args:
        core_values (list): List of core values
        num_questions (int): Number of questions to generate
        
    Returns:
        list: List of generated questions
    """
    try:
        # Ensure num_questions is an integer
        num_questions = int(num_questions)
        
        # For now, return a sample test
        return create_sample_questions(core_values, num_questions)
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        return None

def create_sample_questions(core_values, num_questions):
    """
    Create sample questions based on core values.
    
    Args:
        core_values (list): List of core values
        num_questions (int): Number of questions to generate
        
    Returns:
        list: List of sample questions
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