# Troubleshooting Guide

## Chat Endpoint Not Returning Answers

### Common Issues and Solutions

#### 1. **Request Format Issue**

**Problem:** Not sending JSON correctly in Postman

**Solution:**
- Make sure you're using `POST` method
- Set `Content-Type: application/json` in Headers
- Use the "Body" tab → select "raw" → select "JSON" from dropdown
- Use this exact format:
```json
{
    "message": "What information do you have?"
}
```

#### 2. **Empty Vector Store**

**Problem:** No documents have been processed

**Solution:**
- Check if static files exist: `GET /static-files`
- If empty, make sure you have PDF/CSV files in `static_data/` folder
- Rebuild the pipeline: `POST /rebuild`

#### 3. **OpenAI API Key Issue**

**Problem:** API key not set or invalid

**Solution:**
- Check your `.env` file exists
- Make sure it contains: `OPENAI_API_KEY=your_actual_key_here`
- Restart the server after updating `.env`

#### 4. **Server Not Running**

**Problem:** Server crashed or not started

**Solution:**
- Check terminal for errors
- Restart server: `python app.py`
- Look for "Services initialized successfully" message

#### 5. **Timeout Issues**

**Problem:** Request taking too long

**Solution:**
- OpenAI API calls can take 5-30 seconds
- Wait for the response
- Check server logs for errors

### Testing Steps

1. **Test Health:**
   ```
   GET http://localhost:5000/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **Check Static Files:**
   ```
   GET http://localhost:5000/static-files
   ```
   Should show your PDF/CSV files

3. **Test Chat:**
   ```
   POST http://localhost:5000/chat
   Content-Type: application/json
   
   {
       "message": "What information do you have?"
   }
   ```

### Expected Response Format

**Success:**
```json
{
    "response": "Based on the context..."
}
```

**Error (No Context):**
```json
{
    "response": "I apologize, but I don't have any information in my knowledge base to answer your question. Please make sure files have been uploaded and processed."
}
```

**Error (Invalid Request):**
```json
{
    "error": "Message is required. Please include \"message\" field in your request."
}
```

### Debug Checklist

- [ ] Server is running (check terminal)
- [ ] `.env` file exists with `OPENAI_API_KEY`
- [ ] Static files exist in `static_data/` folder
- [ ] Vector store has been created (check logs)
- [ ] Request format is correct (JSON with "message" field)
- [ ] Content-Type header is set to `application/json`
- [ ] No errors in server terminal

### Quick Test Command

Test the chat endpoint from terminal:
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What information do you have?"}'
```

