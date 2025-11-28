# RTO AI Enrollment Chatbot

A Flask-based REST API for a chatbot with RAG (Retrieval-Augmented Generation) capabilities. The chatbot can process PDF and CSV files, extract information, and answer questions based on the uploaded documents using OpenAI.

## Features

- 📄 **PDF Processing**: Extract and index text from PDF files
- 📊 **CSV Processing**: Process and index CSV data
- 🔍 **RAG (Retrieval-Augmented Generation)**: Retrieve relevant context from uploaded documents
- 💬 **OpenAI Integration**: Generate intelligent responses using OpenAI's GPT models
- 🚀 **RESTful API**: Easy-to-use endpoints for file upload and chat

## Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Virtual environment (recommended)

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd "RTO AI Enrollment Chatbot"
   ```

2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   ```

## Usage

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5000`

2. **API Endpoints:**

   ### Health Check
   ```bash
   GET /health
   ```

   ### Upload File (PDF or CSV)
   ```bash
   POST /upload
   Content-Type: multipart/form-data
   
   Form data:
   - file: (PDF or CSV file)
   ```

   Example using curl:
   ```bash
   curl -X POST http://localhost:5000/upload \
     -F "file=@your_document.pdf"
   ```

   ### Chat
   ```bash
   POST /chat
   Content-Type: application/json
   
   {
     "message": "What is the enrollment process?",
     "history": []  # Optional: conversation history
   }
   ```

   Example using curl:
   ```bash
   curl -X POST http://localhost:5000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What information do you have about enrollments?"}'
   ```

   ### List Uploaded Files
   ```bash
   GET /files
   ```

   ### Clear Vector Store
   ```bash
   POST /clear
   ```

## Project Structure

```
RTO AI Enrollment Chatbot/
├── app.py                 # Main Flask application
├── rag_service.py         # RAG service for document processing
├── openai_service.py      # OpenAI integration service
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── static_data/          # Static files (auto-processed on startup)
├── uploads/              # Uploaded files (created automatically)
└── vector_store/         # FAISS vector store (created automatically)
```

## Static Files (RAG Pipeline)

The application supports **static files** that are automatically processed when the server starts. This creates a persistent RAG pipeline.

### How to Use Static Files:

1. **Place your files in the `static_data/` folder:**
   ```bash
   # Copy your PDF or CSV files to static_data folder
   cp your_document.pdf static_data/
   cp your_data.csv static_data/
   ```

2. **Start the server:**
   ```bash
   python app.py
   ```
   
   The server will automatically:
   - Detect all PDF and CSV files in `static_data/`
   - Process and index them
   - Create embeddings
   - Build the vector store

3. **The RAG pipeline is ready!** You can immediately start chatting with the bot.

### Static File Endpoints:

- **List Static Files:**
  ```bash
  GET /static-files
  ```

- **Rebuild Pipeline:**
  ```bash
  POST /rebuild
  ```
  
  This clears the vector store and reprocesses all static files (useful after updating files).

### Notes:

- Static files are processed **once on startup**
- If you add new files to `static_data/`, use the `/rebuild` endpoint or restart the server
- Static files take precedence and are always loaded first
- You can still upload additional files via `/upload` endpoint

## How It Works

1. **File Upload**: When you upload a PDF or CSV file, the system:
   - Extracts text/data from the file
   - Splits it into chunks
   - Creates embeddings using OpenAI
   - Stores them in a FAISS vector database

2. **Chat**: When you ask a question:
   - The system searches the vector database for relevant context
   - Retrieves the most relevant chunks
   - Sends the context and question to OpenAI
   - Returns an intelligent response based on your documents

## Configuration

- **OPENAI_API_KEY**: Your OpenAI API key (required)
- **OPENAI_MODEL**: OpenAI model to use (default: gpt-3.5-turbo)
- **UPLOAD_FOLDER**: Folder for uploaded files (default: uploads)
- **MAX_FILE_SIZE**: Maximum file size in bytes (default: 16MB)

## Error Handling

The API includes comprehensive error handling for:
- Invalid file types
- File processing errors
- OpenAI API errors
- Missing required parameters

## Notes

- The vector store persists between server restarts
- Multiple files can be uploaded and indexed
- The system maintains conversation history (last 5 messages)
- CSV files are converted to a text format for better searchability

## License

This project is open source and available for use.

