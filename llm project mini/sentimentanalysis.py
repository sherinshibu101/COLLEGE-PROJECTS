import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()
token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)


def get_sentiment(input_text):
    """
    Sends input_text to OpenAI GPT-4 model for sentiment analysis and returns the response.
    """
    try:
        # Call OpenAI GPT-4 model
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"The user expressed the following feelings: \"{input_text}\". Analyze the sentiment and determine whether it is happy, sad, or neutral. Provide a conversational, empathetic response that feels like a supportive chat. Avoid sounding robotic or overly formal."}])
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# Streamlit Web App Code
st.title("Sentiment Analysis")

# User Input Section
user_input = st.text_input("Enter your feelings below:")

if st.button("Submit"):
    if user_input:
        with st.spinner("Analyzing sentiment..."):
            # Get sentiment response from OpenAI GPT-4
            sentiment_response = get_sentiment(user_input)
        # Display sentiment response
        st.subheader("Emotions")
        st.write(sentiment_response)
    else:
        st.error("Please enter some text to analyze.")