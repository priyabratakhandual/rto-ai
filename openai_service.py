import os
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenAI API interactions"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    def generate_response(self, user_message, context=None):
        """Generate chatbot response using OpenAI with RAG context"""
        try:
            # Build system message with context
            system_message = """You are a helpful AI assistant that answers questions based on the provided context. 
            Use the context information to provide accurate and relevant answers. 
            If the context doesn't contain enough information to answer the question, 
            say so politely and provide a general answer if possible."""
            
            # Format context for the prompt
            context_text = ""
            
            if context and len(context) > 0:
                context_text = "\n\nRelevant Context:\n"
                for i, ctx in enumerate(context, 1):
                    context_text += f"\n[{i}] {ctx['content']}\n"
            
            # Build messages
            messages = [
                {"role": "system", "content": system_message}
            ]
            
            # Add current context and user message
            user_prompt = f"{context_text}\n\nQuestion: {user_message}\n\nAnswer based on the context provided above."
            messages.append({"role": "user", "content": user_prompt})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message.content
            
            return {
                'message': assistant_message
            }
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            raise

