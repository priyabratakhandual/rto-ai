import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StudentDatabase:
    """Database service for managing student records"""
    
    def __init__(self, db_path='students.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database and create tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create students table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT,
                    address TEXT,
                    enrollment_date TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def _generate_student_id(self):
        """Generate a unique student ID"""
        import random
        import string
        
        # Format: STU-YYYYMMDD-XXXX (e.g., STU-20251125-A3B7)
        date_prefix = datetime.now().strftime("%Y%m%d")
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        student_id = f"STU-{date_prefix}-{random_suffix}"
        
        # Ensure uniqueness
        while self.get_student_by_id(student_id):
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            student_id = f"STU-{date_prefix}-{random_suffix}"
        
        return student_id
    
    def create_student(self, name, email, phone=None, address=None, enrollment_date=None):
        """Create a new student record"""
        try:
            # Check if email already exists
            if self.get_student_by_email(email):
                return {'success': False, 'error': 'Email already exists'}
            
            # Generate student ID
            student_id = self._generate_student_id()
            
            # Set enrollment date to today if not provided
            if not enrollment_date:
                enrollment_date = datetime.now().strftime("%Y-%m-%d")
            
            created_at = datetime.now().isoformat()
            updated_at = created_at
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO students 
                (student_id, name, email, phone, address, enrollment_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (student_id, name, email, phone, address, enrollment_date, created_at, updated_at))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Student created: {student_id} - {name}")
            return {
                'success': True,
                'student_id': student_id,
                'message': 'Student registered successfully'
            }
        except sqlite3.IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            return {'success': False, 'error': 'Email already exists'}
        except Exception as e:
            logger.error(f"Error creating student: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_student_by_id(self, student_id):
        """Get student by student ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT student_id, name, email, phone, address, enrollment_date, created_at, updated_at
                FROM students WHERE student_id = ?
            ''', (student_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'student_id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'address': row[4],
                    'enrollment_date': row[5],
                    'created_at': row[6],
                    'updated_at': row[7]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting student by ID: {str(e)}")
            return None
    
    def get_student_by_email(self, email):
        """Get student by email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT student_id, name, email, phone, address, enrollment_date, created_at, updated_at
                FROM students WHERE email = ?
            ''', (email,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'student_id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'address': row[4],
                    'enrollment_date': row[5],
                    'created_at': row[6],
                    'updated_at': row[7]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting student by email: {str(e)}")
            return None
    
    def get_all_students(self, limit=100, offset=0):
        """Get all students with pagination"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT student_id, name, email, phone, address, enrollment_date, created_at, updated_at
                FROM students 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            
            students = []
            for row in rows:
                students.append({
                    'student_id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'address': row[4],
                    'enrollment_date': row[5],
                    'created_at': row[6],
                    'updated_at': row[7]
                })
            
            return students
        except Exception as e:
            logger.error(f"Error getting all students: {str(e)}")
            return []
    
    def update_student(self, student_id, name=None, email=None, phone=None, address=None):
        """Update student information"""
        try:
            student = self.get_student_by_id(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}
            
            # Check if email is being changed and if new email exists
            if email and email != student['email']:
                if self.get_student_by_email(email):
                    return {'success': False, 'error': 'Email already exists'}
            
            updated_at = datetime.now().isoformat()
            
            # Build update query dynamically
            updates = []
            values = []
            
            if name:
                updates.append('name = ?')
                values.append(name)
            if email:
                updates.append('email = ?')
                values.append(email)
            if phone is not None:
                updates.append('phone = ?')
                values.append(phone)
            if address is not None:
                updates.append('address = ?')
                values.append(address)
            
            if not updates:
                return {'success': False, 'error': 'No fields to update'}
            
            updates.append('updated_at = ?')
            values.append(updated_at)
            values.append(student_id)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Student updated: {student_id}")
            return {'success': True, 'message': 'Student updated successfully'}
        except Exception as e:
            logger.error(f"Error updating student: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_student(self, student_id):
        """Delete a student record"""
        try:
            student = self.get_student_by_id(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Student deleted: {student_id}")
            return {'success': True, 'message': 'Student deleted successfully'}
        except Exception as e:
            logger.error(f"Error deleting student: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def search_students(self, query):
        """Search students by name, email, or student ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            search_term = f"%{query}%"
            cursor.execute('''
                SELECT student_id, name, email, phone, address, enrollment_date, created_at, updated_at
                FROM students 
                WHERE name LIKE ? OR email LIKE ? OR student_id LIKE ?
                ORDER BY created_at DESC
                LIMIT 50
            ''', (search_term, search_term, search_term))
            
            rows = cursor.fetchall()
            conn.close()
            
            students = []
            for row in rows:
                students.append({
                    'student_id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'address': row[4],
                    'enrollment_date': row[5],
                    'created_at': row[6],
                    'updated_at': row[7]
                })
            
            return students
        except Exception as e:
            logger.error(f"Error searching students: {str(e)}")
            return []

