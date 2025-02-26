"""
Entry point for Vercel Serverless Functions
"""
import os
from mangum import Mangum
from app.core.application import create_app

# Set environment flags
os.environ["VERCEL"] = "True"
os.environ["USE_POLLING"] = "False"

# Create FastAPI application instance
app = create_app()

# Create ASGI handler for Vercel
handler = Mangum(app, lifespan="off") 