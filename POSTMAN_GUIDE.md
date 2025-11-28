# Postman Testing Guide

This guide shows you how to test all API endpoints in Postman.

## Base URL
```
http://localhost:5000
```
or
```
http://127.0.0.1:5000
```

---

## 1. Health Check

**Endpoint:** `GET /health`

**Request:**
- Method: `GET`
- URL: `http://localhost:5000/health`
- Headers: None required

**Expected Response:**
```json
{
    "status": "healthy",
    "message": "RAG Chatbot API is running"
}
```

---

## 2. List Static Files

**Endpoint:** `GET /static-files`

**Request:**
- Method: `GET`
- URL: `http://localhost:5000/static-files`
- Headers: None required

**Expected Response:**
```json
{
    "static_files": [
        {
            "filename": "converted_text.pdf",
            "size": 12345,
            "type": "pdf"
        }
    ]
}
```

---

## 3. List Uploaded Files

**Endpoint:** `GET /files`

**Request:**
- Method: `GET`
- URL: `http://localhost:5000/files`
- Headers: None required

**Expected Response:**
```json
{
    "files": [
        {
            "filename": "example.pdf",
            "size": 12345,
            "type": "pdf"
        }
    ]
}
```

---

## 4. Upload File (PDF or CSV)

**Endpoint:** `POST /upload`

**Request:**
- Method: `POST`
- URL: `http://localhost:5000/upload`
- Headers: None required (Postman will set Content-Type automatically)
- Body: 
  - Select `form-data` tab
  - Key: `file` (type: File)
  - Value: Select a PDF or CSV file from your computer

**In Postman:**
1. Go to Body tab
2. Select `form-data`
3. Change the first key type from "Text" to "File"
4. Key name: `file`
5. Click "Select Files" and choose your PDF or CSV file

**Expected Response:**
```json
{
    "message": "File processed successfully",
    "filename": "example.pdf",
    "chunks": 4
}
```

---

## 5. Chat with RAG

**Endpoint:** `POST /chat`

**Request:**
- Method: `POST`
- URL: `http://localhost:5000/chat`
- Headers:
  - `Content-Type: application/json`
- Body (raw JSON):
```json
{
    "message": "What information do you have about enrollments?"
}
```

**Expected Response:**
```json
{
    "response": "Based on the provided context, the enrollment process..."
}
```

---

## 6. Clear Vector Store

**Endpoint:** `POST /clear`

**Request:**
- Method: `POST`
- URL: `http://localhost:5000/clear`
- Headers: None required
- Body: None required

**Expected Response:**
```json
{
    "message": "Vector store cleared successfully"
}
```

---

## 7. Rebuild Pipeline

**Endpoint:** `POST /rebuild`

**Request:**
- Method: `POST`
- URL: `http://localhost:5000/rebuild`
- Headers: None required
- Body: None required

**Expected Response:**
```json
{
    "message": "RAG pipeline rebuilt successfully from static files"
}
```

---

## Postman Collection JSON

You can import this collection directly into Postman:

```json
{
    "info": {
        "name": "RAG Chatbot API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Health Check",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "http://localhost:5000/health",
                    "protocol": "http",
                    "host": ["localhost"],
                    "port": "5000",
                    "path": ["health"]
                }
            }
        },
        {
            "name": "List Static Files",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "http://localhost:5000/static-files",
                    "protocol": "http",
                    "host": ["localhost"],
                    "port": "5000",
                    "path": ["static-files"]
                }
            }
        },
        {
            "name": "List Uploaded Files",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "http://localhost:5000/files",
                    "protocol": "http",
                    "host": ["localhost"],
                    "port": "5000",
                    "path": ["files"]
                }
            }
        },
        {
            "name": "Upload File",
            "request": {
                "method": "POST",
                "header": [],
                "body": {
                    "mode": "formdata",
                    "formdata": [
                        {
                            "key": "file",
                            "type": "file",
                            "src": []
                        }
                    ]
                },
                "url": {
                    "raw": "http://localhost:5000/upload",
                    "protocol": "http",
                    "host": ["localhost"],
                    "port": "5000",
                    "path": ["upload"]
                }
            }
        },
        {
            "name": "Chat",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"message\": \"What information do you have?\",\n    \"history\": []\n}"
                },
                "url": {
                    "raw": "http://localhost:5000/chat",
                    "protocol": "http",
                    "host": ["localhost"],
                    "port": "5000",
                    "path": ["chat"]
                }
            }
        },
        {
            "name": "Clear Vector Store",
            "request": {
                "method": "POST",
                "header": [],
                "url": {
                    "raw": "http://localhost:5000/clear",
                    "protocol": "http",
                    "host": ["localhost"],
                    "port": "5000",
                    "path": ["clear"]
                }
            }
        },
        {
            "name": "Rebuild Pipeline",
            "request": {
                "method": "POST",
                "header": [],
                "url": {
                    "raw": "http://localhost:5000/rebuild",
                    "protocol": "http",
                    "host": ["localhost"],
                    "port": "5000",
                    "path": ["rebuild"]
                }
            }
        }
    ]
}
```

---

## Quick Test Steps

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Test Health Check:**
   - GET `http://localhost:5000/health`

3. **Test Chat (Main Feature):**
   - POST `http://localhost:5000/chat`
   - Body: `{"message": "What information do you have?"}`

4. **Upload a file:**
   - POST `http://localhost:5000/upload`
   - Body: form-data with file

5. **Chat again with new context:**
   - POST `http://localhost:5000/chat`
   - Ask questions about the uploaded file

---

## Common Issues

### 404 Not Found
- Make sure the server is running
- Check the URL is correct (should be `http://localhost:5000`)

### 500 Internal Server Error
- Check if OpenAI API key is set in `.env` file
- Check server logs for detailed error messages

### Empty Response
- Make sure you've uploaded files or have static files in `static_data/` folder
- Try rebuilding the pipeline: POST `/rebuild`

