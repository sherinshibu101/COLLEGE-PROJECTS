import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_file_path):
    """
    Extracts text from a PDF file.

    Args:
        pdf_file_path (str): Path to the PDF file.

    Returns:
        str: Cleaned extracted text, or an error message if extraction fails.
    """
    try:
        # Open the PDF file
        doc = fitz.open(pdf_file_path)
        pdf_text = ""

        # Iterate through each page and extract text
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pdf_text += page.get_text("text")
        
        doc.close()

        # Clean and return the extracted text
        return clean_extracted_text(pdf_text)

    except Exception as e:
        return f"Error extracting text from {pdf_file_path}: {e}"

def clean_extracted_text(raw_text):
    """
    Cleans up the raw text by removing unnecessary whitespace.

    Args:
        raw_text (str): Raw text to clean.

    Returns:
        str: Cleaned text with redundant spaces and line breaks removed.
    """
    if not raw_text:
        return ""
    
    # Remove multiple line breaks and extra spaces
    cleaned_text = " ".join(raw_text.splitlines())
    return " ".join(cleaned_text.split())