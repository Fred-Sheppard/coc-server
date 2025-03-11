import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_server_url():
    """
    Constructs the server URL based on environment variables.
    If running locally, uses localhost with the PORT from .env.
    Otherwise, uses the SERVER_URL environment variable.
    """
    # Check if SERVER_URL is explicitly set (for production environments)
    explicit_url = os.getenv('SERVER_URL')
    if explicit_url and not explicit_url.startswith('http://localhost'):
        return explicit_url
    
    # For local development, use localhost with the correct port
    port = os.getenv('PORT', '5001')
    return f"http://localhost:{port}" 