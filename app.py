from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from rag_service import RAGService
from openai_service import OpenAIService
from database import StudentDatabase
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Configuration for static files
STATIC_DATA_FOLDER = 'static_data'

# Create necessary folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_DATA_FOLDER, exist_ok=True)
os.makedirs('vector_store', exist_ok=True)

# Initialize services (RAG service will automatically process static files)
logger.info("Initializing RAG service and processing static files...")
try:
    rag_service = RAGService(static_data_folder=STATIC_DATA_FOLDER)
    openai_service = OpenAIService()
    student_db = StudentDatabase()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    logger.error("Please check your .env file and ensure OPENAI_API_KEY is set")
    # Set to None so the app can still start, but endpoints will show errors
    rag_service = None
    openai_service = None
    student_db = None


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def index():
    """API information endpoint"""
    return jsonify({
        'name': 'RAG Chatbot API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': 'GET /health',
            'list_static_files': 'GET /static-files',
            'list_uploaded_files': 'GET /files',
            'upload_file': 'POST /upload (form-data: file)',
            'chat': 'POST /chat (JSON: message)',
            'clear_store': 'POST /clear',
            'rebuild_pipeline': 'POST /rebuild',
            'register_student': 'POST /student/register (JSON: name, email, phone?, address?)',
            'get_student': 'GET /student/<student_id>',
            'get_student_by_email': 'GET /student/email/<email>',
            'list_students': 'GET /students?limit=100&offset=0',
            'search_students': 'GET /student/search?q=<query>',
            'update_student': 'PUT /student/<student_id>',
            'delete_student': 'DELETE /student/<student_id>'
        },
        'base_url': 'http://localhost:5000'
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'RAG Chatbot API is running'}), 200


@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload and process PDF or CSV file"""
    if rag_service is None:
        return jsonify({'error': 'RAG service not initialized. Please check your configuration.'}), 500
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF and CSV files are allowed'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"Processing file: {filename}")
        
        # Process file based on type
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        if file_extension == 'pdf':
            result = rag_service.process_pdf(filepath)
        elif file_extension == 'csv':
            result = rag_service.process_csv(filepath)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
        
        if result['success']:
            return jsonify({
                'message': 'File processed successfully',
                'filename': filename,
                'chunks': result.get('chunks', 0)
            }), 200
        else:
            return jsonify({'error': result.get('error', 'Failed to process file')}), 500
            
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500


@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint with RAG"""
    if rag_service is None or openai_service is None:
        return jsonify({'error': 'Services not initialized. Please check your configuration.'}), 500
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required. Please send JSON with "message" field.'}), 400
        
        if 'message' not in data:
            return jsonify({'error': 'Message is required. Please include "message" field in your request.'}), 400
        
        user_message = data['message']
        
        if not user_message or not user_message.strip():
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        logger.info(f"Received chat message: {user_message[:100]}...")
        
        # Retrieve relevant context from RAG
        relevant_docs = rag_service.retrieve_context(user_message, top_k=3)
        
        if not relevant_docs:
            logger.warning("No relevant context found in vector store")
            return jsonify({
                'response': 'I apologize, but I don\'t have any information in my knowledge base to answer your question. Please make sure files have been uploaded and processed.'
            }), 200
        
        # Generate response using OpenAI with RAG context
        response = openai_service.generate_response(
            user_message=user_message,
            context=relevant_docs
        )
        
        return jsonify({
            'response': response['message']
        }), 200
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Error generating response: {str(e)}',
            'hint': 'Make sure your OpenAI API key is set correctly in .env file'
        }), 500


@app.route('/clear', methods=['POST'])
def clear_data():
    """Clear all uploaded data and vector store"""
    if rag_service is None:
        return jsonify({'error': 'RAG service not initialized. Please check your configuration.'}), 500
    try:
        rag_service.clear_vector_store()
        return jsonify({'message': 'Vector store cleared successfully'}), 200
    except Exception as e:
        logger.error(f"Error clearing vector store: {str(e)}")
        return jsonify({'error': f'Error clearing data: {str(e)}'}), 500


@app.route('/rebuild', methods=['POST'])
def rebuild_pipeline():
    """Rebuild RAG pipeline from static files"""
    if rag_service is None:
        return jsonify({'error': 'RAG service not initialized. Please check your configuration.'}), 500
    try:
        rag_service.rebuild_pipeline()
        return jsonify({'message': 'RAG pipeline rebuilt successfully from static files'}), 200
    except Exception as e:
        logger.error(f"Error rebuilding pipeline: {str(e)}")
        return jsonify({'error': f'Error rebuilding pipeline: {str(e)}'}), 500


@app.route('/static-files', methods=['GET'])
def list_static_files():
    """List all static files in static_data folder (PDF and CSV only)"""
    try:
        files = []
        if os.path.exists(STATIC_DATA_FOLDER):
            for filename in os.listdir(STATIC_DATA_FOLDER):
                # Skip hidden files and non-data files
                if filename.startswith('.'):
                    continue
                filepath = os.path.join(STATIC_DATA_FOLDER, filename)
                if os.path.isfile(filepath):
                    # Only include PDF and CSV files
                    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    if file_ext in ['pdf', 'csv']:
                        files.append({
                            'filename': filename,
                            'size': os.path.getsize(filepath),
                            'type': file_ext
                        })
        return jsonify({'static_files': files}), 200
    except Exception as e:
        logger.error(f"Error listing static files: {str(e)}")
        return jsonify({'error': f'Error listing static files: {str(e)}'}), 500


@app.route('/files', methods=['GET'])
def list_files():
    """List all uploaded files"""
    try:
        files = []
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    files.append({
                        'filename': filename,
                        'size': os.path.getsize(filepath),
                        'type': filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
                    })
        return jsonify({'files': files}), 200
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': f'Error listing files: {str(e)}'}), 500


# Student Management Endpoints
@app.route('/student/register', methods=['POST'])
def register_student():
    """Register a new student"""
    if student_db is None:
        return jsonify({'error': 'Database not initialized'}), 500
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Required fields
        if 'name' not in data or not data['name'].strip():
            return jsonify({'error': 'Name is required'}), 400
        
        if 'email' not in data or not data['email'].strip():
            return jsonify({'error': 'Email is required'}), 400
        
        # Optional fields
        name = data['name'].strip()
        email = data['email'].strip()
        phone = data.get('phone', '').strip() if data.get('phone') else None
        address = data.get('address', '').strip() if data.get('address') else None
        enrollment_date = data.get('enrollment_date', '').strip() if data.get('enrollment_date') else None
        
        result = student_db.create_student(
            name=name,
            email=email,
            phone=phone,
            address=address,
            enrollment_date=enrollment_date
        )
        
        if result['success']:
            student = student_db.get_student_by_id(result['student_id'])
            return jsonify({
                'message': result['message'],
                'student': student
            }), 201
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error registering student: {str(e)}")
        return jsonify({'error': f'Error registering student: {str(e)}'}), 500


@app.route('/student/<student_id>', methods=['GET'])
def get_student(student_id):
    """Get student information by student ID"""
    if student_db is None:
        return jsonify({'error': 'Database not initialized'}), 500
    try:
        student = student_db.get_student_by_id(student_id)
        if student:
            return jsonify({'student': student}), 200
        else:
            return jsonify({'error': 'Student not found'}), 404
    except Exception as e:
        logger.error(f"Error getting student: {str(e)}")
        return jsonify({'error': f'Error getting student: {str(e)}'}), 500


@app.route('/student/email/<email>', methods=['GET'])
def get_student_by_email(email):
    """Get student information by email"""
    if student_db is None:
        return jsonify({'error': 'Database not initialized'}), 500
    try:
        student = student_db.get_student_by_email(email)
        if student:
            return jsonify({'student': student}), 200
        else:
            return jsonify({'error': 'Student not found'}), 404
    except Exception as e:
        logger.error(f"Error getting student: {str(e)}")
        return jsonify({'error': f'Error getting student: {str(e)}'}), 500


@app.route('/students', methods=['GET'])
def list_students():
    """List all students with pagination"""
    if student_db is None:
        return jsonify({'error': 'Database not initialized'}), 500
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        students = student_db.get_all_students(limit=limit, offset=offset)
        return jsonify({
            'students': students,
            'count': len(students)
        }), 200
    except Exception as e:
        logger.error(f"Error listing students: {str(e)}")
        return jsonify({'error': f'Error listing students: {str(e)}'}), 500


@app.route('/student/search', methods=['GET'])
def search_students():
    """Search students by name, email, or student ID"""
    if student_db is None:
        return jsonify({'error': 'Database not initialized'}), 500
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        students = student_db.search_students(query)
        return jsonify({
            'students': students,
            'count': len(students),
            'query': query
        }), 200
    except Exception as e:
        logger.error(f"Error searching students: {str(e)}")
        return jsonify({'error': f'Error searching students: {str(e)}'}), 500


@app.route('/student/<student_id>', methods=['PUT'])
def update_student(student_id):
    """Update student information"""
    if student_db is None:
        return jsonify({'error': 'Database not initialized'}), 500
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        result = student_db.update_student(
            student_id=student_id,
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address')
        )
        
        if result['success']:
            student = student_db.get_student_by_id(student_id)
            return jsonify({
                'message': result['message'],
                'student': student
            }), 200
        else:
            return jsonify({'error': result['error']}), 400
    except Exception as e:
        logger.error(f"Error updating student: {str(e)}")
        return jsonify({'error': f'Error updating student: {str(e)}'}), 500


@app.route('/student/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student record"""
    if student_db is None:
        return jsonify({'error': 'Database not initialized'}), 500
    try:
        result = student_db.delete_student(student_id)
        if result['success']:
            return jsonify({'message': result['message']}), 200
        else:
            return jsonify({'error': result['error']}), 404
    except Exception as e:
        logger.error(f"Error deleting student: {str(e)}")
        return jsonify({'error': f'Error deleting student: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

