import faiss
import numpy as np
import pickle
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Set your Azure OpenAI API key and endpoint
openai_api_key = os.getenv("GITHUB_TOKEN")
endpoint = "https://models.inference.ai.azure.com"

if not openai_api_key:
    raise ValueError("OpenAI API key not set! Please set it using `export OPENAI_API_KEY=<your_api_key>` and retry.")

# Initialize OpenAI client with Azure endpoint
client = OpenAI(
    base_url=endpoint,
    api_key=openai_api_key,
)

# Embed text chunks using OpenAI's embedding model
def embed_text_chunks(chunks, batch_size=32):
    """
    Embed text chunks using OpenAI's embedding model.
    Args:
        chunks (list of str): List of text chunks to embed.
        batch_size (int): Number of chunks to process in a single batch.
    Returns:
        np.ndarray: Normalized embeddings for the text chunks.
    """
    embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=batch
        )
        batch_embeddings = [datum["embedding"] for datum in response["data"]]
        embeddings.extend(batch_embeddings)
    embeddings = np.array(embeddings)

    # Normalize for cosine similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norms

# Build FAISS index
def build_faiss_index(embeddings):
    """
    Build a FAISS index for the given embeddings.
    Args:
        embeddings (np.ndarray): Array of embeddings.
    Returns:
        faiss.IndexFlatIP: FAISS index for the embeddings.
    """
    dim = embeddings.shape[1]  # Dimension of the embeddings
    index = faiss.IndexFlatIP(dim)  # Inner product for cosine similarity
    index.add(embeddings)  # Add embeddings to the index
    return index

# Build FAISS index with metadata (text chunks mapped to embeddings)
def build_faiss_index_with_metadata(embeddings, chunks):
    """
    Build a FAISS index with metadata mapping text chunks to embeddings.
    Args:
        embeddings (np.ndarray): Array of embeddings.
        chunks (list of str): List of text chunks corresponding to embeddings.
    Returns:
        tuple: FAISS index and the chunks.
    """
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Using inner product for cosine similarity
    index.add(embeddings)
    return index, chunks

# Save FAISS index and metadata
def save_index_with_metadata(index, chunks, index_file, metadata_file):
    """
    Save the FAISS index and metadata to files.
    Args:
        index (faiss.IndexFlatIP): FAISS index.
        chunks (list of str): List of text chunks.
        index_file (str): Path to save the FAISS index.
        metadata_file (str): Path to save the metadata.
    """
    faiss.write_index(index, index_file)
    with open(metadata_file, 'wb') as f:
        pickle.dump(chunks, f)

# Load FAISS index and metadata
def load_index_with_metadata(index_file, metadata_file):
    """
    Load the FAISS index and metadata from files.
    Args:
        index_file (str): Path to the FAISS index file.
        metadata_file (str): Path to the metadata file.
    Returns:
        tuple: FAISS index and the chunks.
    """
    index = faiss.read_index(index_file)
    with open(metadata_file, 'rb') as f:
        chunks = pickle.load(f)
    return index, chunks

# Query FAISS index
def query_faiss_index(index, query_embedding, k=5):
    """
    Query the FAISS index to find the most similar embeddings.
    Args:
        index (faiss.IndexFlatIP): FAISS index.
        query_embedding (np.ndarray): Query embedding.
        k (int): Number of nearest neighbors to retrieve.
    Returns:
        tuple: Indices and distances of the nearest neighbors.
    """
    if query_embedding.ndim == 1:
        query_embedding = np.expand_dims(query_embedding, axis=0)
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
    distances, indices = index.search(query_embedding, k)
    return indices[0], distances[0]