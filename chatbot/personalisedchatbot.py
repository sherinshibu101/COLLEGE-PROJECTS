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
    query_faiss_index,
    load_index_with_metadata,
    save_index_with_metadata,
    build_faiss_index_with_metadata,
    get_query_embedding
)
import faiss

# Load environment variables
load_dotenv()
token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
embedding_model = "text-embedding-3-large"
chat_model = "gpt-4o"  # or "gpt-35-turbo" for Azure

client = OpenAI(
    base_url=endpoint,
    api_key=token,
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
    text = extract_text_from_pdf(file)
    if not text.strip():
        return None, None, None, "The uploaded PDF is empty or could not be processed. Please try a different file."

    # Step 2: Split text into chunks
    chunks = split_text_into_chunks(text, chunk_size=chunk_size, overlap=overlap)

    # Step 3: Embed chunks
    embeddings = embed_text_chunks(chunks)

    # Step 4: Build FAISS index
    index = build_faiss_index(embeddings)

    return index, embeddings, chunks, "Chatbot initialized successfully!"

def generate_response_with_gpt(query, context, user_request_style="default"):
    """
    Generate a response using GPT-4 with the retrieved context.
    The response is customized based on the user's preferred style of explanation.

    Parameters:
    - query: The user's query string.
    - context: The relevant context string (e.g., PDF content).
    - user_request_style: The user's preferred style of explanation.
    
    Returns:
    - The response content (formatted to match user preferences).
    """
    try:
        # Define a structured and dynamic prompt that adapts to the user's query.
        structured_prompt = """
        You are a helpful assistant that provides structured and clear answers based on the provided context. 
        The answers should be:
        1. Well-structured with clear points or sections.
        2. Adapted to the user's requested style of explanation.

        ### Rules:
        - If the user specifies "explain like I'm 5", simplify explanations as much as possible, avoiding technical jargon, and use simple sentences. 
        - If requested in another specific style, adapt accordingly. 
        - Always output the response in a structured manner with clearly marked sections, bullet points, and numbered lists when appropriate.

        Context:
        {context}

        User Query:
        {query}

        User's Preferred Style: {user_request_style}

        Answer:
        """
        # Prepare the combined prompt with user details and their preferred explanation style.
        prompt = structured_prompt.format(context=context, query=query, user_request_style=user_request_style)

        # Generate the response using GPT.
        response = client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": "You are a highly capable assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Adjust for balanced creativity and accuracy.
            max_tokens=1000   # Increase token limit to allow for detailed responses.
        )

        # Return the generated response content to the user.
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Handle potential errors gracefully.
        return f"Error generating response: {str(e)}"

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
        
        # Add style selector
        style_options = ["default", "explain like I'm 5", "technical", "brief"]
        selected_style = st.selectbox("How would you like the explanation?", style_options)
        
        user_query = st.text_input("💬 Enter your query:")
        
        if user_query:
            with st.spinner("Generating response..."):
                # Get query embedding
                query_embedding = get_query_embedding(user_query)
                # Get relevant chunks
                indices, _ = query_faiss_index(index, query_embedding, k=3)
                relevant_chunks = [chunks[idx] for idx in indices]
                context = "\n\n".join(relevant_chunks)
                # Generate response with style
                response = generate_response_with_gpt(user_query, context, selected_style)
            
            st.write("### 🧠 Response:")
            st.write(response)

    os.remove("temp_uploaded_file.pdf")