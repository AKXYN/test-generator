# Core Values Test Generator

A Streamlit application that generates assessment tests based on company core values.

## Features

- Firebase authentication integration
- Core values management
- AI-powered test generation
- Firestore database integration

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` and fill in your Firebase and OpenAI credentials
4. For local development, you can also use a Firebase service account key file named `serviceAccountKey.json`

## Running the App

### Local Development

```
streamlit run app.py
```

### Deployment

This app is designed to be deployed on Streamlit Cloud:

1. Push your code to a GitHub repository
2. Connect your repository to Streamlit Cloud
3. Set up your environment variables in the Streamlit Cloud dashboard
4. Deploy your app

## Integration with Core Values Dashboard

This app is designed to work with the Core Values Dashboard application. When a test is generated, it will be saved to Firestore and will appear in the "Future Tests" section of the dashboard.

## Project Structure

- `app.py`: Main Streamlit application
- `requirements.txt`: Python dependencies
- `.env`: Environment variables (not tracked in git)
- `.env.example`: Template for environment variables

## Future Enhancements

- Duration adjustment for future tests
- Start test button that emails students
- Quiz app for students to take the test
- Report generation service for insights and charts 