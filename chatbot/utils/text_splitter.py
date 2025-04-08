import re

def split_text_into_chunks(text, chunk_size=500, overlap=100):
    """
    Splits a long text into smaller, coherent chunks based on sentences.

    Args:
        text (str): The input text to split.
        chunk_size (int): The maximum size (in number of characters) for each chunk.
        overlap (int): The number of overlapping characters between consecutive chunks.

    Returns:
        list: A list of text chunks, maintaining coherence between sentences.
    """
    # Split text into sentences based on punctuation
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # Check if adding the sentence exceeds the chunk size
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence.strip()  # Add the sentence to the current chunk
        else:
            # Add the current chunk to the chunks list
            chunks.append(current_chunk.strip())
            
            # Start a new chunk with overlap
            if overlap > 0 and len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:]  # Take the last `overlap` characters
            else:
                current_chunk = ""
            current_chunk += " " + sentence.strip()
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks