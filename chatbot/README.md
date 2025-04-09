# 📄 Personalized PDF Chatbot

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=OpenAI&logoColor=white)
[![Live Demo](https://img.shields.io/badge/Live_Demo-12pdfchatbot.streamlit.app-2ea44f?style=for-the-badge)](https://12pdfchatbot.streamlit.app/)

A smart chatbot that understands your PDF documents and answers questions in your preferred style.  
Created by [Sherin Shibu](mailto:sherinshibu149@gmail.com).

---

## ✨ Features

| Feature            | Description                                      |
|--------------------|--------------------------------------------------|
| 📄 **PDF Processing**   | Extract and clean text from uploaded PDFs         |
| ✂️ **Smart Chunking**   | Context-aware text splitting with overlap         |
| 🔍 **Vector Search**    | FAISS-powered semantic similarity matching        |
| 🧠 **Style Adaptation** | Answers in different explanation styles           |
| 🧹 **Temporary Files**  | Auto-cleanup of uploaded files after processing   |

---

## 🚀 Quick Start

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/personalized-pdf-chatbot.git
   cd personalized-pdf-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   streamlit run personalisedchatbot.py
   ```

---

## 📂 File Structure

```
.
├── personalisedchatbot.py          # Main Streamlit application
├── interface.py                    # (Optional) Separate UI logic
├── requirements.txt                # Python dependencies
├── .env                            # Environment configuration
└── utils/
    ├── embedder.py                 # Embedding and FAISS operations
    ├── pdf_loader.py               # PDF text extraction
    └── text_splitter.py            # Text chunking utilities
```

---

## ⚙️ Configuration

Customize parameters in `personalisedchatbot.py`:

```python
# Chatbot parameters
chunk_size = 500        # Characters per chunk
overlap = 100           # Overlap between chunks
chat_model = "gpt-4o"   # "gpt-4o" or "gpt-3.5-turbo"

# Style options (can be used for future style prompts)
style_options = [
    "default", 
    "explain like I'm 5",
    "technical",
    "brief"
]
```

---

## 🌐 Live Demo

🚀 [Try it live on Streamlit!](https://12pdfchatbot.streamlit.app/)

---

## 📧 Contact

Created with ❤️ by **Sherin Shibu**  
📩 [sherinshibu149@gmail.com](mailto:sherinshibu149@gmail.com)  
🌐 [Live Demo](https://12pdfchatbot.streamlit.app/)