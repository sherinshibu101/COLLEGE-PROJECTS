import os
import streamlit as st
import numpy as np
import faiss

from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text_into_chunks
from utils.embedder import embed_text_chunks, get_query_embedding, build_faiss_index, query_faiss_index

# =======================
# --- Chat Completion (Azure AI Inference) ---
# =======================
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
CHAT_ENDPOINT = "https://models.github.ai/inference"
CHAT_MODEL = "openai/gpt-4o"

chat_client = ChatCompletionsClient(
    endpoint=CHAT_ENDPOINT,
    credential=AzureKeyCredential(GITHUB_TOKEN)
)

def generate_response_with_gpt(query, context, user_request_style="default", temperature=0.7, max_tokens=1000):
    messages = [
        SystemMessage("You are a highly capable assistant."),
        UserMessage(
            f"""
            Context:
            {context}

            User Query:
            {query}

            User's Preferred Style: {user_request_style}
            Answer:
            """
        ),
    ]
    response = chat_client.complete(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        model=CHAT_MODEL
    )
    return response.choices[0].message.content.strip()

# =======================
# --- Chatbot Logic ---
# =======================
def initialize_chatbot_from_file(file, chunk_size=500, overlap=100):
    text = extract_text_from_pdf(file)
    if not text.strip():
        return None, None, None, "The uploaded PDF is empty or could not be processed. Please try a different file."
    chunks = split_text_into_chunks(text, chunk_size=chunk_size, overlap=overlap)
    embeddings = embed_text_chunks(chunks)
    index = build_faiss_index(embeddings)
    return index, embeddings, chunks, "Chatbot initialized successfully!"

# =======================
# --- Streamlit UI ---
# =======================
st.set_page_config(page_title="Personalized PDF Chatbot", layout="centered")
st.title("📄 Personalized PDF Chatbot")
st.write("Upload your PDF file to initialize the chatbot and start asking questions!")

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
        style_options = ["default", "explain like I'm 5", "technical", "brief"]
        selected_style = st.selectbox("How would you like the explanation?", style_options)
        user_query = st.text_input("💬 Enter your query:")
        if user_query:
            with st.spinner("Generating response..."):
                query_embedding = get_query_embedding(user_query)
                indices, _ = query_faiss_index(index, query_embedding, k=3)
                relevant_chunks = [chunks[idx] for idx in indices]
                context = "\n\n".join(relevant_chunks)
                response = generate_response_with_gpt(user_query, context, selected_style)
            st.write("### 🧠 Response:")
            st.write(response)
    os.remove("temp_uploaded_file.pdf")
