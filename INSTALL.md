# Installation Guide

## Quick Setup

1. **Activate your virtual environment:**
   ```bash
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate  # On Windows
   ```

2. **Install all dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment variables:**
   ```bash
   cp env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

## Troubleshooting

### ModuleNotFoundError: langchain

If you get import errors, make sure you've installed all the required packages:

```bash
pip install --upgrade -r requirements.txt
```

### Specific LangChain Import Issues

The code handles multiple LangChain versions automatically. If you still have issues:

1. **For newer LangChain versions (v0.1+):**
   ```bash
   pip install langchain langchain-openai langchain-community langchain-text-splitters langchain-core
   ```

2. **For older LangChain versions (v0.0.x):**
   ```bash
   pip install langchain==0.0.350
   ```

### FAISS Installation Issues

If FAISS fails to install:

```bash
# Try CPU version (recommended)
pip install faiss-cpu

# Or if you have GPU support
pip install faiss-gpu
```

### OpenAI API Key Issues

Make sure your `.env` file exists and contains:
```
OPENAI_API_KEY=your_actual_api_key_here
```

## Verify Installation

Test if everything is installed correctly:

```bash
python -c "from rag_service import RAGService; print('✓ RAG Service OK')"
python -c "from openai_service import OpenAIService; print('✓ OpenAI Service OK')"
```

