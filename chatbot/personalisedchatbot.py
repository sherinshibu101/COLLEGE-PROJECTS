import os
import streamlit as st
import numpy as np
import requests
import faiss
import pickle

from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text_into_chunks

# =======================
# --- Embedding Code ---
# =======================
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
EMBEDDING_ENDPOINT = "https://api.github.com/models/openai/text-embedding-3-large/infer"
CHAT_ENDPOINT = "https://api.github.com/models/openai/gpt-4o/infer"

def embed_text_chunks(chunks, batch_size=32):
    if not isinstance(chunks, list) or not all(isinstance(chunk, str) and chunk.strip() for chunk in chunks):
        raise ValueError("Input 'chunks' must be a list of non-empty strings.")

    embeddings = []
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        response = requests.post(EMBEDDING_ENDPOINT, json={"inputs": batch}, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "embeddings" not in data:
            st.error(f"Embedding API response missing 'embeddings' key: {data}")
            raise KeyError("API response missing 'embeddings' key")
        for item in data["embeddings"]:
            embeddings.append(item)
    embeddings = np.array(embeddings)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norms

def get_query_embedding(query):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.post(EMBEDDING_ENDPOINT, json={"inputs": [query]}, headers=headers)
    response.raise_for_status()
    data = response.json()
    if "embeddings" not in data:
        st.error(f"Embedding API response missing 'embeddings' key: {data}")
        raise KeyError("API response missing 'embeddings' key")
    embedding = np.array(data["embeddings"][0])
    return embedding / np.linalg.norm(embedding)

# =======================
# --- FAISS Code ---
# =======================
def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index

def query_faiss_index(index, query_embedding, k=5):
    if query_embedding.ndim == 1:
        query_embedding = np.expand_dims(query_embedding, axis=0)
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
    distances, indices = index.search(query_embedding, k)
    return indices[0], distances[0]

def save_index_with_metadata(index, chunks, index_file, metadata_file):
    faiss.write_index(index, index_file)
    with open(metadata_file, 'wb') as f:
        pickle.dump(chunks, f)

def load_index_with_metadata(index_file, metadata_file):
    index = faiss.read_index(index_file)
    with open(metadata_file, 'rb') as f:
        chunks = pickle.load(f)
    return index, chunks

# =======================
# --- Chat Completion ---
# =======================
def generate_response_with_gpt(query, context, user_request_style="default", temperature=0.7, max_tokens=1000):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    system_prompt = "You are a highly capable assistant."
    user_prompt = f"""
        Context:
        {context}

        User Query:
        {query}

        User's Preferred Style: {user_request_style}
        Answer:
    """
    payload = {
        "inputs": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "parameters": {
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    }
    response = requests.post(CHAT_ENDPOINT, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    # Adjust if output structure changes!
    if "choices" in data and len(data["choices"]) > 0 and "message" in data["choices"][0]:
        return data["choices"][0]["message"]["content"].strip()
    else:
        st.error(f"Chat API response missing expected keys: {data}")
        return "An error occurred while generating your response."

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
