"""
Simple test script for the RAG Chatbot API
Run this after starting the Flask server to test the endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"


def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_upload(filepath):
    """Test file upload endpoint"""
    print(f"Testing file upload: {filepath}")
    with open(filepath, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_chat(message):
    """Test chat endpoint"""
    print(f"Testing chat with message: {message}")
    data = {
        "message": message,
        "history": []
    }
    response = requests.post(
        f"{BASE_URL}/chat",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result.get('response', 'No response')}")
    if result.get('sources'):
        print(f"Sources: {result['sources']}")
    print()


def test_list_files():
    """Test list files endpoint"""
    print("Testing list files...")
    response = requests.get(f"{BASE_URL}/files")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


if __name__ == "__main__":
    print("=" * 50)
    print("RAG Chatbot API Test Script")
    print("=" * 50)
    print()
    
    # Test health check
    try:
        test_health()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the Flask server is running on http://localhost:5000\n")
        exit(1)
    
    # Test file upload (uncomment and provide a file path)
    # test_upload("path/to/your/file.pdf")
    # test_upload("path/to/your/file.csv")
    
    # Test list files
    test_list_files()
    
    # Test chat (uncomment after uploading files)
    # test_chat("What information do you have?")
    # test_chat("Tell me about the enrollment process")
    
    print("=" * 50)
    print("Tests completed!")
    print("=" * 50)

