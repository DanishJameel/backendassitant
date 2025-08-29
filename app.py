#!/usr/bin/env python3
"""
Main application file for Hugging Face Spaces deployment
This is the entry point that Hugging Face will use to run the app
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables from .env if present
load_dotenv(dotenv_path=current_dir / ".env", override=False)

from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import uuid
import json
import re
from typing import Optional

# Import all the field definitions and prompts using absolute imports
from constants import *
from models import ChatRequest, GPTSelectionRequest, OfferToAvatarHandoffRequest, OfferToAvatarHandoffResponse, AvatarToBeforeHandoffRequest, AvatarToAfterHandoffRequest
from services import GPTService

# Initialize OpenAI client (ensure API key is available)
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Please set it in your Hugging Face Space environment variables."
    )

# Initialize OpenAI client with explicit httpx configuration
try:
    import httpx
    client = OpenAI(
        api_key=openai_api_key,
        http_client=httpx.Client(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    )
except Exception as e:
    # Fallback to basic initialization if httpx configuration fails
    client = OpenAI(api_key=openai_api_key)

app = FastAPI(
    title="EUREKA GPT Assistant Suite", 
    description="Complete suite of 13 specialized GPT assistants for marketing strategy",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GPT service
gpt_service = GPTService()

@app.post("/api/select-gpt")
def select_gpt(req: GPTSelectionRequest):
    """Select which GPT to use for the session"""
    return gpt_service.select_gpt(req.gpt_type)

@app.post("/api/chat")
def chat(req: ChatRequest):
    """Handle chat messages with the selected GPT"""
    return gpt_service.chat(req)

@app.post("/api/reset")
def reset_session(session_id: str = Body(...)):
    """Reset a conversation session"""
    return gpt_service.reset_session(session_id)

@app.post("/api/combined-summary")
def get_combined_summary(session_ids: list = Body(...)):
    """Generate a combined summary from multiple GPT sessions"""
    return gpt_service.get_combined_summary(session_ids)

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "sessions": gpt_service.get_session_count()}


@app.post("/api/handoff/offer-to-avatar", response_model=OfferToAvatarHandoffResponse)
def handoff_offer_to_avatar(req: OfferToAvatarHandoffRequest):
    """Create an Avatar Creator session prefilled from an Offer Clarifier session"""
    return gpt_service.handoff_offer_to_avatar(req.offer_session_id)


@app.post("/api/handoff/avatar-to-before")
def handoff_avatar_to_before(req: AvatarToBeforeHandoffRequest):
    """Create a Before State Research session with avatar context"""
    return gpt_service.handoff_avatar_to_before(req.avatar_session_id)


@app.post("/api/handoff/avatar-to-after")
def handoff_avatar_to_after(req: AvatarToAfterHandoffRequest):
    """Create an After State Research session with avatar context"""
    return gpt_service.handoff_avatar_to_after(req.avatar_session_id)

@app.get("/")
async def serve_frontend():
    """Serve the main frontend HTML file"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EUREKA GPT Assistant Suite</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; }
                .api-info { background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }
                .endpoint { background: #3498db; color: white; padding: 10px; border-radius: 3px; margin: 5px 0; }
                .docs-link { text-align: center; margin: 20px 0; }
                .docs-link a { background: #e74c3c; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 EUREKA GPT Assistant Suite</h1>
                <p>Welcome to the EUREKA GPT Assistant Suite - a comprehensive suite of 13 specialized GPT assistants for marketing strategy.</p>
                
                <div class="api-info">
                    <h3>📡 API Endpoints Available:</h3>
                    <div class="endpoint">POST /api/select-gpt - Select which GPT to use</div>
                    <div class="endpoint">POST /api/chat - Chat with the selected GPT</div>
                    <div class="endpoint">POST /api/reset - Reset a conversation session</div>
                    <div class="endpoint">POST /api/combined-summary - Get combined summary from multiple sessions</div>
                    <div class="endpoint">GET /api/health - Health check</div>
                </div>
                
                <div class="docs-link">
                    <a href="/docs">📚 View Full API Documentation</a>
                </div>
                
                <h3>🎯 Available GPT Assistants:</h3>
                <ul>
                    <li>Offer Clarifier - Define your product/service clearly</li>
                    <li>Avatar Creator & Empathy Map - Build complete customer avatars</li>
                    <li>Before State Research - Uncover deep emotional insights</li>
                    <li>After State Research - Create compelling transformation narratives</li>
                    <li>Avatar Validator - Analyze and improve customer avatars</li>
                    <li>Trigger GPT - Identify customer trigger events</li>
                    <li>EPO Builder - Generate compelling Entry Point Offers</li>
                    <li>SCAMPER Synthesizer - Innovate using SCAMPER framework</li>
                    <li>Wildcard Idea Bot - Inject bold, unexpected creative ideas</li>
                    <li>Concept Crafter Bot - Transform offerings into compelling messaging</li>
                    <li>Hook & Headline GPT - Generate scroll-stopping messaging</li>
                    <li>Campaign Concept Generator - Create complete campaign ideas</li>
                    <li>Idea Injection Bot - Capture creative insights</li>
                </ul>
            </div>
        </body>
        </html>
        """)

if __name__ == "__main__":
    import uvicorn
    import os
    # Get port from environment variable (for Render) or use default
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
