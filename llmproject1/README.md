# Smart Money Exchanger 💰

A Streamlit application that converts currencies using real-time exchange rates with the help of AI (GPT-4) and the ExchangeRate-API.

## Features ✨

- Real-time currency conversion
- AI-powered natural language understanding
- Support for all major currencies (USD, EUR, GBP, JPY, etc.)
- Simple and intuitive interface
- Built with LangSmith tracing for monitoring

## Prerequisites 🛠️

Before you begin, ensure you have the following:
- Python 3.8 or higher
- Git (optional)
- API keys for:
  - ExchangeRate-API
  - OpenAI/GPT-4
  - LangSmith (for tracing)

## Installation 📥

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/money-changer.git
   cd money-changer

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your API keys:
   ```
   GITHUB_TOKEN=your_github_token
   EXCHANGERATE_API_KEY=your_exchangerate_api_key
   LANGCHAIN_API_KEY=your_langchain_api_key
   ```

## Usage 🚀

1. Run the application:
   ```bash
   streamlit run moneychanger.py
   ```

2. In the browser window that opens:
   - Enter your currency conversion request in natural language (e.g., "Convert 100 USD to EUR")
   - Click the "Submit" button
   - View the conversion result

## Examples 🌍

Try these inputs:
- "Convert 50 US dollars to Japanese yen"
- "What's 200 Euros in British pounds?"
- "100 CAD to USD"

## Project Structure 📂

```
money-changer/
├── .gitignore
├── moneychanger.py      # Main application code
├── README.md            # This file
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (ignored by git)
```

## Contributing 🤝

Contributions are welcome! Please open an issue or submit a pull request for any improvements.

## License 📜

This project is licensed under the MIT License.

## 📧 Contact

Created with ❤️ by **Sherin Shibu**  
📩 [sherinshibu149@gmail.com](mailto:sherinshibu149@gmail.com)
```
