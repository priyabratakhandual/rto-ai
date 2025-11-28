# Static Data Folder

Place your PDF and CSV files in this folder to automatically process them when the server starts.

## Usage

1. Copy your files here:
   ```bash
   cp your_document.pdf static_data/
   cp your_data.csv static_data/
   ```

2. Start the server - files will be automatically processed:
   ```bash
   python app.py
   ```

3. The RAG pipeline will be ready with your documents indexed!

## Notes

- Only PDF and CSV files are processed
- Files are processed once on server startup
- To reprocess files after changes, use the `/rebuild` endpoint or restart the server
- Files in this folder are considered "static" and are always loaded

