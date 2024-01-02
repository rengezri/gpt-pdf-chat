
# GPT PDF Chat

## Introduction
GPT PDF Chat is an advanced Python application that allows users to interact with PDF documents using natural language queries. It uses OpenAI's models for understanding and responding to user queries, and integrates a vector store for efficient querying of document contents.

## Features
- **PDF Document Processing:** Ingests PDF documents and processes them into a queryable vector store.
- **Natural Language Query:** Allows users to ask questions and get answers based on the contents of the ingested PDF documents.
- **Gradio Interface:** Provides an easy-to-use web interface for interacting with the application.

## Installation

### Prerequisites
- Python 3.6 or later
- Pip package manager

### Step-by-Step Guide
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/gpt-pdf-chat.git
   cd gpt-pdf-chat
   ```

2. **Install Dependencies:**
   Install the required Python libraries using pip.
   ```bash
   pip install asyncio openai pathlib threading gradio os dotenv
   ```

3. **Environment Variables:**
   Create a `.env` file in the root directory of the project and add your OpenAI API key:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Running the Application:**
   Run the main Python script to start the application.
   ```bash
   python3 app.py
   ```

## Usage
Once the application is running, you can use it as follows:
1. **Upload a PDF Document:** Use the 'Ingest PDF File' button to upload a PDF document.
2. **Process PDF:** Click the 'Process PDF' button to initialize the vector store with the uploaded document.
3. **Query the Document:** Enter your question in the textbox and click 'Get Answer' to receive a response based on the PDF content.

## Contributing
Contributions are welcome. Please read the contributing guidelines before making a pull request.

## License
This project is licensed under the [MIT License](LICENSE).

---

**Note:** The application requires an API key from OpenAI, which is not provided with the code. Please ensure you have this key before running the application.
