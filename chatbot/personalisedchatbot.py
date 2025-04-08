import os
import streamlit as st
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text_into_chunks
from utils.embedder import (
    embed_text_chunks,
    build_faiss_index,
    query_faiss_index
)

# Load environment variables from .env file
load_dotenv()
token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "text-embedding-3-large"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

response = client.embeddings.create(
    input=["user_query"],
    model=model_name,
)

# Chatbot Initialization
def initialize_chatbot_from_file(file, chunk_size=500, overlap=100):
    """
    Initialize the chatbot by processing the uploaded PDF file.
    Args:
        file (str): Path to the uploaded PDF file.
        chunk_size (int): Size of each text chunk.
        overlap (int): Overlap between chunks.
    Returns:
        tuple: FAISS index, embeddings, chunks, and status message.
    """
    # Step 1: Extract text from uploaded PDF
    with open(file, "rb") as f:
        text = extract_text_from_pdf(f)
    if not text.strip():
        return None, None, None, "The uploaded PDF is empty or could not be processed. Please try a different file."

    # Step 2: Split text into chunks
    chunks = split_text_into_chunks(text, chunk_size=chunk_size, overlap=overlap)

    # Step 3: Embed chunks
    embeddings = embed_text_chunks(chunks)

    # Step 4: Build FAISS index
    index = build_faiss_index(embeddings)

    return index, embeddings, chunks, "Chatbot initialized successfully!"

# Query using OpenAI API
def handle_query_with_openai(user_query, index, embeddings, chunks, max_results=3):
    """
    Handle user queries by generating responses using Azure OpenAI.
    Args:
        user_query (str): The user's query.
        index (faiss.IndexFlatIP): FAISS index of embeddings.
        embeddings (np.ndarray): Array of embeddings.
        chunks (list): List of text chunks.
        max_results (int): Number of top results to retrieve.
    Returns:
        str: Response generated based on the query.
    """
    try:
        # Validate user query
        if not isinstance(user_query, str) or not user_query.strip():
            raise ValueError("User query must be a non-empty string.")

        # Generate embedding of the user query
        response = client.responses.create(
            input=[user_query],
            model=model_name
        )
        query_embedding = np.array(response.data[0].embedding)

        # Retrieve relevant chunks from FAISS index
        indices, distances = query_faiss_index(index, query_embedding, k=max_results)

        # Retrieve the top chunks
        relevant_chunks = " ".join([chunks[idx] for idx in indices])

        # Construct prompt
        prompt = f"""
        You are a helpful assistant. Use the following extracted context from a document to answer the user's query.\n\n
        Context: {relevant_chunks}\n\n
        User Query: {user_query}\n\n
        Provide a concise and accurate response:
        """

        # Simulate a response (replace this with your actual chat model if needed)
        return f"Simulated response based on context: {relevant_chunks}"
    except Exception as e:
        return f"Could not get a response from OpenAI. Possible issue: {e}"

# Streamlit Interface
st.set_page_config(page_title="Personalized PDF Chatbot", layout="centered")
st.title("📄 Personalized PDF Chatbot")
st.write("Upload your PDF file to initialize the chatbot and start asking questions!")

# File Uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    with open("temp_uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Processing your PDF and initializing the chatbot..."):
        index, embeddings, chunks, status = initialize_chatbot_from_file("temp_uploaded_file.pdf")

    if index is None:
        st.error(status)
    else:
        st.success("Chatbot initialized! You can now start asking questions.")
        user_query = st.text_input("💬 Enter your query:")

        if user_query:
            with st.spinner("Generating response from OpenAI..."):
                response = handle_query_with_openai(user_query, index, embeddings, chunks)
            st.write("### 🧠 Response:")
            st.write(response)

    os.remove("temp_uploaded_file.pdf")