import os
import openai
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_questions(core_values, num_questions):
    """
    Generate questions based on core values using OpenAI API.
    
    Args:
        core_values (list): List of core values
        num_questions (int): Number of questions to generate
        
    Returns:
        tuple: (questions, error_message) where error_message is None if successful
    """
    try:
        # Ensure num_questions is an integer
        num_questions = int(num_questions)
        
        # Format core values for the prompt
        core_values_text = "\n".join([
            f"- {cv['name']}: {cv['description']}"
            for cv in core_values
        ])
        
        # Create the prompt for OpenAI
        prompt = f"""You are an expert in creating assessment questions for company core values.
Given the following core values and their descriptions:

{core_values_text}

Generate {num_questions} multiple-choice questions that test a candidate's alignment with these core values.
Each question should:
1. Be specific to one or more core values
2. Present a realistic workplace scenario
3. Have 4 answer options that represent different levels of alignment with the core values
4. Include scores for each option (8 for most aligned, 6 for somewhat aligned, 4 for somewhat misaligned, 2 for misaligned)

Format each question as a JSON object with:
- id: question number
- text: the question text
- core_values: list of core values this question tests
- options: list of answer options, each with text and score

Return only the JSON array of questions, no other text."""

        # Call OpenAI API using the new syntax
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in creating assessment questions for company core values."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract and parse the response using the new syntax
        questions_text = response.choices[0].message.content
        try:
            # Try to parse the response as JSON
            questions = json.loads(questions_text)
            return questions, None
        except json.JSONDecodeError:
            error_msg = f"Failed to parse OpenAI response as JSON. Response: {questions_text}"
            print(error_msg)
            return create_sample_questions(core_values, num_questions), error_msg
            
    except Exception as e:
        error_msg = f"Error generating questions: {str(e)}"
        print(error_msg)
        return create_sample_questions(core_values, num_questions), error_msg

def create_sample_questions(core_values, num_questions):
    """
    Create sample questions based on core values.
    This is a fallback function used when AI generation fails.
    
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
