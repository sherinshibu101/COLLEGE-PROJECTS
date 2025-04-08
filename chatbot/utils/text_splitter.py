import re

def split_text_into_chunks(text, chunk_size=500, overlap=100):
    """
    Splits text into coherent chunks with sentence awareness.
    Args:
        text (str): Input text to split.
        chunk_size (int): Max characters per chunk.
        overlap (int): Overlapping characters between chunks.
    Returns:
        list[str]: List of text chunks.
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += f" {sentence.strip()}"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = current_chunk[-overlap:] if overlap > 0 else ""
            current_chunk += f" {sentence.strip()}"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks