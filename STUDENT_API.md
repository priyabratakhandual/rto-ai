# Student Management API

The API includes a complete student management system with auto-generated student IDs and database storage.

## Student ID Format

Student IDs are automatically generated in the format: `STU-YYYYMMDD-XXXX`

- **STU**: Prefix for Student
- **YYYYMMDD**: Date of registration (e.g., 20251125)
- **XXXX**: Random 4-character alphanumeric code (e.g., A3B7)

Example: `STU-20251125-A3B7`

## Endpoints

### 1. Register Student

**Endpoint:** `POST /student/register`

**Request:**
```json
{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "address": "123 Main St, City, State",
    "enrollment_date": "2025-11-25"
}
```

**Required Fields:**
- `name`: Student's full name
- `email`: Student's email address (must be unique)

**Optional Fields:**
- `phone`: Phone number
- `address`: Physical address
- `enrollment_date`: Date in YYYY-MM-DD format (defaults to today)

**Response:**
```json
{
    "message": "Student registered successfully",
    "student": {
        "student_id": "STU-20251125-A3B7",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "address": "123 Main St, City, State",
        "enrollment_date": "2025-11-25",
        "created_at": "2025-11-25T16:30:00",
        "updated_at": "2025-11-25T16:30:00"
    }
}
```

---

### 2. Get Student by ID

**Endpoint:** `GET /student/<student_id>`

**Example:** `GET /student/STU-20251125-A3B7`

**Response:**
```json
{
    "student": {
        "student_id": "STU-20251125-A3B7",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "address": "123 Main St, City, State",
        "enrollment_date": "2025-11-25",
        "created_at": "2025-11-25T16:30:00",
        "updated_at": "2025-11-25T16:30:00"
    }
}
```

---

### 3. Get Student by Email

**Endpoint:** `GET /student/email/<email>`

**Example:** `GET /student/email/john.doe@example.com`

**Response:** Same as Get Student by ID

---

### 4. List All Students

**Endpoint:** `GET /students`

**Query Parameters:**
- `limit`: Number of records to return (default: 100)
- `offset`: Number of records to skip (default: 0)

**Example:** `GET /students?limit=50&offset=0`

**Response:**
```json
{
    "students": [
        {
            "student_id": "STU-20251125-A3B7",
            "name": "John Doe",
            "email": "john.doe@example.com",
            ...
        },
        ...
    ],
    "count": 2
}
```

---

### 5. Search Students

**Endpoint:** `GET /student/search?q=<query>`

**Example:** `GET /student/search?q=john`

Searches by:
- Name
- Email
- Student ID

**Response:** Same format as List All Students

---

### 6. Update Student

**Endpoint:** `PUT /student/<student_id>`

**Request:**
```json
{
    "name": "John Updated",
    "email": "john.updated@example.com",
    "phone": "+9876543210",
    "address": "456 New St, City, State"
}
```

All fields are optional - only include fields you want to update.

**Response:**
```json
{
    "message": "Student updated successfully",
    "student": {
        "student_id": "STU-20251125-A3B7",
        "name": "John Updated",
        ...
    }
}
```

---

### 7. Delete Student

**Endpoint:** `DELETE /student/<student_id>`

**Example:** `DELETE /student/STU-20251125-A3B7`

**Response:**
```json
{
    "message": "Student deleted successfully"
}
```

---

## Database

- **Database File:** `students.db` (SQLite)
- **Location:** Project root directory
- **Auto-created:** Database and tables are created automatically on first run

## Error Responses

### 400 Bad Request
```json
{
    "error": "Email is required"
}
```

### 404 Not Found
```json
{
    "error": "Student not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "Database not initialized"
}
```

## Example Usage in Postman

1. **Register a new student:**
   - POST `http://localhost:5000/student/register`
   - Body: `{"name": "John Doe", "email": "john@example.com"}`

2. **Get student by ID:**
   - GET `http://localhost:5000/student/STU-20251125-A3B7`

3. **Search for students:**
   - GET `http://localhost:5000/student/search?q=john`

4. **Update student:**
   - PUT `http://localhost:5000/student/STU-20251125-A3B7`
   - Body: `{"phone": "+1234567890"}`

5. **Delete student:**
   - DELETE `http://localhost:5000/student/STU-20251125-A3B7`

