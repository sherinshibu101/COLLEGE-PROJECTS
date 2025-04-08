import os
import streamlit as st
from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text_into_chunks
from utils.embedder import (
    embed_text_chunks,
    build_faiss_index_with_metadata,
    query_faiss_index
)
import openai

# Ensure OpenAI API key is set
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OpenAI API key not set! Please set it using `export OPENAI_API_KEY=<your_api_key>` and restart.")
    st.stop()

# Chatbot Initialization
def initialize_chatbot_from_file(file, chunk_size=500, overlap=100):
    # Step 1: Extract text from uploaded PDF
    with open(file, "rb") as f:
        text = extract_text_from_pdf(f)
    if not text.strip():
        return None, None, None, "The uploaded PDF is empty or could not be processed. Please try a different file."

    # Step 2: Split text into chunks
    chunks = split_text_into_chunks(text, chunk_size=chunk_size, overlap=overlap)

    # Step 3: Embed chunks using OpenAI embedding API
    embeddings = embed_text_chunks(chunks)

    # Step 4: Build FAISS index
    index, metadata = build_faiss_index_with_metadata(embeddings, chunks)

    return index, metadata, chunks, "Chatbot initialized successfully!"

# Query using OpenAI API
def handle_query_with_openai(user_query, index, chunks, max_results=3):
    try:
        # Generate embedding of the user query using OpenAI
        response = openai.Embedding.create(
            model="text-embedding-ada-002", 
            input=[user_query], 
            api_key=openai_api_key
        )
        query_embedding = np.array(response["data"][0]["embedding"])

        # Retrieve relevant chunks from FAISS index
        indices, distances = query_faiss_index(index, query_embedding)

        # Retrieve the top chunks relevant to the user's question
        relevant_chunks = " ".join([chunks[idx] for idx in indices[:max_results]])

        # Construct the prompt for OpenAI's ChatGPT API
        prompt = f"""
        You are a helpful assistant. Use the following extracted context from a document to answer the user's query.\n\n
        Context: {relevant_chunks}\n\n
        User Query: {user_query}\n\n
        Provide a concise and accurate response:
        """
        chat_response = openai.ChatCompletion.create(
            model="gpt-4",  # Use "gpt-3.5-turbo" if you prefer
            messages=[
                {"role": "system", "content": "You are a helpful assistant who provides information based on context."},
                {"role": "user", "content": prompt},
            ],
            api_key=openai_api_key
        )
        return chat_response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Could not get a response from OpenAI. Possible issue: {e}"

# Streamlit Interface
st.title("Summarizer Chatbot")
st.write("Upload your PDF file to initialize the chatbot and start asking questions!")

# File Uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Temporary storage for the uploaded file
    with open("temp_uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Initialize the chatbot
    with st.spinner("Processing your PDF and initializing the chatbot..."):
        index, metadata, chunks, status = initialize_chatbot_from_file("temp_uploaded_file.pdf")
    if index is None:
        st.error(status)
    else:
        st.success("Chatbot initialized! You can now start asking questions.")
        
        # Query Input
        user_query = st.text_input("Enter your query:")
        if user_query:
            with st.spinner("Generating response from OpenAI..."):
                response = handle_query_with_openai(user_query, index, chunks)
            st.write("### Response:")
            st.write(response)

        # Cleanup temporary file
        os.remove("temp_uploaded_file.pdf")