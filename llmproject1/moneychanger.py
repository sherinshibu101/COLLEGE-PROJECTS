from typing import Tuple, Dict
import os
from dotenv import load_dotenv
import requests
import json
import streamlit as st
from openai import OpenAI
from langsmith import wrappers, traceable

# Load environment variables
load_dotenv()

# API keys and configurations
token = os.getenv("GITHUB_TOKEN")
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

if not token or not EXCHANGERATE_API_KEY or not LANGCHAIN_API_KEY:
    raise ValueError("Missing required API keys. Please check your .env file.")

endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

# OpenAI client setup
client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

# LangChain tracing setup
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "moneychanger"

@traceable
def get_exchange_rate(base: str, target: str, amount: str) -> Tuple:
    """Return a tuple of (base, target, amount, conversion_result (2 decimal places))"""
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{base}/{target}/{amount}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "conversion_result" not in data:
            raise ValueError(f"Unexpected response format: {data}")
        return (base, target, amount, f'{data["conversion_result"]:.2f}')
    except Exception as e:
        st.error(f"Error fetching exchange rate: {e}")
        return (base, target, amount, "Error")

@traceable
def call_llm(textbox_input: str) -> Dict:
    """Make a call to the LLM with the textbox_input as the prompt."""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "exchange_rate_function",
                "description": "Convert a given amount of money from one currency to another. Each currency will be represented as a 3-letter code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "base": {"type": "string", "description": "The base or original currency."},
                        "target": {"type": "string", "description": "The target or converted currency."},
                        "amount": {"type": "string", "description": "The amount of money to convert from the base currency."},
                    },
                    "required": ["base", "target", "amount"],
                    "additionalProperties": False,
                },
            },
        }
    ]

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": textbox_input},
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=model_name,
            tools=tools,
        )
        return response
    except Exception as e:
        st.error(f"Error calling LLM: {e}")
        return None

@traceable
def run_pipeline(user_input: str):
    """Based on user_input, determine if you need to use the tools (function calling) for the LLM.
    Call get_exchange_rate(...) if necessary."""
    response = call_llm(user_input)
    if not response:
        st.error("No response received from the LLM. Please check your API key or input.")
        return

    # Debugging: Print the response to the console
    print("LLM Response:", response)

    try:
        if hasattr(response, "choices") and response.choices[0].finish_reason == "tool_calls":
            response_arguments = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
            base = response_arguments["base"]
            target = response_arguments["target"]
            amount = response_arguments["amount"]
            _, _, _, conversion_result = get_exchange_rate(base, target, amount)
            st.write(f'{base} {amount} is {target} {conversion_result}')
        elif hasattr(response, "choices") and response.choices[0].finish_reason == "stop":
            st.write(f"(Function calling not used) and {response.choices[0].message.content}")
        else:
            st.write("NotImplemented")
    except AttributeError as e:
        st.error(f"Unexpected response format: {e}")

# Title of the app
st.title("Smart Money Exchanger")

# Text box for user input
user_input = st.text_input("Enter the amount and the currency")

# Submit button
if st.button("Submit"):
    # Display the input text below the text box
    run_pipeline(user_input)