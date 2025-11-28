import os
import pandas as pd
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Try importing RecursiveCharacterTextSplitter from different possible locations
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        raise ImportError("Could not import RecursiveCharacterTextSplitter. Please install langchain-text-splitters or langchain.")

# Try importing FAISS from different possible locations
try:
    from langchain_community.vectorstores import FAISS
except ImportError:
    try:
        from langchain.vectorstores import FAISS
    except ImportError:
        raise ImportError("Could not import FAISS. Please install langchain-community or langchain.")

# Try importing Document from different possible locations
try:
    from langchain_core.documents import Document
except ImportError:
    try:
        from langchain.schema import Document
    except ImportError:
        # Fallback - Document might not be needed directly
        Document = None

# Try importing OpenAIEmbeddings from different possible locations
try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    try:
        from langchain.embeddings import OpenAIEmbeddings
    except ImportError:
        raise ImportError("Could not import OpenAIEmbeddings. Please install langchain-openai or langchain with OpenAI support.")

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG (Retrieval-Augmented Generation) operations"""
    
    def __init__(self, static_data_folder='static_data'):
        self.vector_store_path = 'vector_store'
        self.static_data_folder = static_data_folder
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self.vector_store = None
        self._load_or_create_vector_store()
        # Initialize RAG pipeline with static files
        self._initialize_rag_pipeline()
    
    def _load_or_create_vector_store(self):
        """Load existing vector store or create a new one"""
        try:
            if os.path.exists(self.vector_store_path) and os.listdir(self.vector_store_path):
                try:
                    # Allow deserialization since we're loading our own files
                    self.vector_store = FAISS.load_local(
                        self.vector_store_path,
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    logger.info("Loaded existing vector store")
                    return
                except Exception as load_error:
                    logger.warning(f"Could not load existing vector store: {str(load_error)}. Will create new one.")
            
            # Vector store will be created when first document is added
            # Don't create empty store as FAISS needs actual documents
            self.vector_store = None
            logger.info("Vector store initialized (will be created when first document is added)")
        except Exception as e:
            logger.warning(f"Could not initialize vector store: {str(e)}. Will create when first document is added.")
            self.vector_store = None
    
    def process_pdf(self, filepath):
        """Extract text from PDF and add to vector store"""
        try:
            logger.info(f"Processing PDF: {filepath}")
            
            # Read PDF
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            if not text.strip():
                return {'success': False, 'error': 'No text extracted from PDF'}
            
            # Split into chunks
            documents = self.text_splitter.create_documents([text])
            
            # Add metadata
            for doc in documents:
                doc.metadata = {'source': os.path.basename(filepath), 'type': 'pdf'}
            
            # Add to vector store
            if self.vector_store is None:
                # Create new vector store with documents
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
            else:
                self.vector_store.add_documents(documents)
            
            # Save vector store
            self.vector_store.save_local(self.vector_store_path)
            
            logger.info(f"Successfully processed PDF with {len(documents)} chunks")
            return {'success': True, 'chunks': len(documents)}
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_csv(self, filepath):
        """Extract data from CSV and add to vector store"""
        try:
            logger.info(f"Processing CSV: {filepath}")
            
            # Read CSV
            df = pd.read_csv(filepath)
            
            # Convert DataFrame to text
            # Create a text representation of the CSV
            text_parts = []
            
            # Add column names
            text_parts.append(f"Columns: {', '.join(df.columns.tolist())}\n\n")
            
            # Add data rows as text
            for idx, row in df.iterrows():
                row_text = f"Row {idx + 1}:\n"
                for col in df.columns:
                    row_text += f"  {col}: {row[col]}\n"
                text_parts.append(row_text + "\n")
            
            text = "\n".join(text_parts)
            
            if not text.strip():
                return {'success': False, 'error': 'No data extracted from CSV'}
            
            # Split into chunks
            documents = self.text_splitter.create_documents([text])
            
            # Add metadata
            for doc in documents:
                doc.metadata = {
                    'source': os.path.basename(filepath),
                    'type': 'csv',
                    'rows': len(df),
                    'columns': len(df.columns)
                }
            
            # Add to vector store
            if self.vector_store is None:
                # Create new vector store with documents
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
            else:
                self.vector_store.add_documents(documents)
            
            # Save vector store
            self.vector_store.save_local(self.vector_store_path)
            
            logger.info(f"Successfully processed CSV with {len(documents)} chunks")
            return {'success': True, 'chunks': len(documents)}
            
        except Exception as e:
            logger.error(f"Error processing CSV: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def retrieve_context(self, query, top_k=3):
        """Retrieve relevant context from vector store"""
        try:
            if self.vector_store is None:
                logger.warning("Vector store is not initialized")
                return []
            
            # Check if vector store has any documents
            try:
                num_docs = self.vector_store.index.ntotal
                if num_docs == 0:
                    logger.warning("Vector store is empty")
                    return []
            except AttributeError:
                # Fallback check
                logger.warning("Could not check vector store size")
                return []
            
            # Search for similar documents
            docs = self.vector_store.similarity_search(query, k=top_k)
            
            # Format context
            context = []
            for doc in docs:
                context.append({
                    'content': doc.page_content,
                    'source': doc.metadata.get('source', 'unknown'),
                    'type': doc.metadata.get('type', 'unknown')
                })
            
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []
    
    def clear_vector_store(self):
        """Clear the vector store"""
        try:
            # Remove existing vector store files
            if os.path.exists(self.vector_store_path):
                import shutil
                shutil.rmtree(self.vector_store_path)
            
            # Set vector store to None (will be recreated when documents are added)
            self.vector_store = None
            
            # Create empty directory
            os.makedirs(self.vector_store_path, exist_ok=True)
            
            logger.info("Vector store cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            raise
    
    def _initialize_rag_pipeline(self):
        """Initialize RAG pipeline by processing static files"""
        try:
            # Check if static data folder exists
            if not os.path.exists(self.static_data_folder):
                logger.info(f"Static data folder '{self.static_data_folder}' does not exist. Skipping static file processing.")
                return
            
            # Get all files in static data folder
            static_files = []
            for filename in os.listdir(self.static_data_folder):
                # Skip hidden files and non-data files
                if filename.startswith('.'):
                    continue
                filepath = os.path.join(self.static_data_folder, filename)
                if os.path.isfile(filepath):
                    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    if file_ext in ['pdf', 'csv']:
                        static_files.append((filepath, file_ext))
            
            if not static_files:
                logger.info("No static files found in static_data folder")
                return
            
            logger.info(f"Found {len(static_files)} static file(s) to process")
            
            # Process each static file
            total_chunks = 0
            for filepath, file_ext in static_files:
                try:
                    if file_ext == 'pdf':
                        result = self.process_pdf(filepath)
                    elif file_ext == 'csv':
                        result = self.process_csv(filepath)
                    else:
                        continue
                    
                    if result.get('success'):
                        chunks = result.get('chunks', 0)
                        total_chunks += chunks
                        logger.info(f"✓ Processed static file: {os.path.basename(filepath)} ({chunks} chunks)")
                    else:
                        logger.warning(f"✗ Failed to process static file: {os.path.basename(filepath)} - {result.get('error', 'Unknown error')}")
                except Exception as e:
                    logger.error(f"Error processing static file {filepath}: {str(e)}")
            
            if total_chunks > 0:
                logger.info(f"RAG pipeline initialized successfully with {total_chunks} total chunks from static files")
            else:
                logger.warning("RAG pipeline initialized but no chunks were added from static files")
                
        except Exception as e:
            logger.error(f"Error initializing RAG pipeline: {str(e)}")
    
    def rebuild_pipeline(self):
        """Rebuild the RAG pipeline from static files"""
        logger.info("Rebuilding RAG pipeline from static files...")
        try:
            # Clear existing vector store
            if os.path.exists(self.vector_store_path):
                import shutil
                shutil.rmtree(self.vector_store_path)
            
            # Reset vector store to None
            self.vector_store = None
            os.makedirs(self.vector_store_path, exist_ok=True)
            
            # Reinitialize from static files
            self._initialize_rag_pipeline()
            logger.info("RAG pipeline rebuilt successfully")
            return True
        except Exception as e:
            logger.error(f"Error rebuilding pipeline: {str(e)}")
            raise

