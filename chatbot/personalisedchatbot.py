import os
import streamlit as st
from dotenv import load_dotenv
from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text_into_chunks
from utils.embedder import (
    embed_text_chunks,
    build_faiss_index,
    query_faiss_index
)
import openai
import numpy as np

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Chatbot Initialization
def initialize_chatbot_from_file(file, chunk_size=500, overlap=100):
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
    try:
        # Generate embedding of the user query
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=[user_query]
        )
        query_embedding = np.array(response["data"][0]["embedding"])

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

        chat_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who provides information based on context."},
                {"role": "user", "content": prompt},
            ]
        )
        return chat_response["choices"][0]["message"]["content"].strip()
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
