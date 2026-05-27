import sys
import os

# Add the root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Vercel entry point for FastAPI
# This file is required for Vercel to serve the FastAPI application

# Export the ASGI app for Vercel
app_handler = app

# For Vercel serverless function
def handler(request, context):
    return app_handler(request, context)
