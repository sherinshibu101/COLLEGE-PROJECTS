import faiss
import numpy as np
import pickle
import streamlit as st
import requests
from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text_into_chunks

token = st.secrets["GITHUB_TOKEN"]
endpoint = "https://api.github.com/models/openai/text-embedding-3-large/infer"

def embed_text_chunks(chunks, batch_size=32):
    """
    Embed text chunks using GitHub Models embedding API.
    Args:
        chunks (list of str): List of text chunks to embed.
        batch_size (int): Number of chunks to process in a single batch.
    Returns:
        np.ndarray: Normalized embeddings for the text chunks.
    """
    if not isinstance(chunks, list) or not all(isinstance(chunk, str) and chunk.strip() for chunk in chunks):
        raise ValueError("Input 'chunks' must be a list of non-empty strings.")

    embeddings = []
    headers = {"Authorization": f"Bearer {token}"}
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"Processing batch: {batch}")
        response = requests.post(endpoint, json={"inputs": batch}, headers=headers)
        response.raise_for_status()
        data = response.json()
        for item in data["embeddings"]:  # Adjust if API response differs!
            embeddings.append(item)
    embeddings = np.array(embeddings)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norms

def get_query_embedding(query):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(endpoint, json={"inputs": [query]}, headers=headers)
    response.raise_for_status()
    data = response.json()
    embedding = np.array(data["embeddings"][0])
    return embedding / np.linalg.norm(embedding)

# --- FAISS code unchanged ---
def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index

def build_faiss_index_with_metadata(embeddings, chunks):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index, chunks

def save_index_with_metadata(index, chunks, index_file, metadata_file):
    faiss.write_index(index, index_file)
    with open(metadata_file, 'wb') as f:
        pickle.dump(chunks, f)

def load_index_with_metadata(index_file, metadata_file):
    index = faiss.read_index(index_file)
    with open(metadata_file, 'rb') as f:
        chunks = pickle.load(f)
    return index, chunks

def query_faiss_index(index, query_embedding, k=5):
    if query_embedding.ndim == 1:
        query_embedding = np.expand_dims(query_embedding, axis=0)
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
    distances, indices = index.search(query_embedding, k)
    return indices[0], distances[0]
