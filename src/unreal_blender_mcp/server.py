"""
MCP Server implementation for unreal-blender-mcp.

This module provides the core server functionality for the unified MCP server
that connects AI agents with Blender and Unreal Engine.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
from sse_starlette.sse import EventSourceResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Unreal-Blender MCP Server")

@app.get("/stream")
async def stream_endpoint(request: Request):
    """
    SSE endpoint for AI agent communication.
    """
    async def event_generator():
        while True:
            if await request.is_disconnected():
                logger.info("Client disconnected")
                break
                
            # Echo back a simple message for now
            yield {
                "event": "message",
                "data": "Server running on port 8300",
            }
            
            await asyncio.sleep(5)
    
    return EventSourceResponse(event_generator())

@app.get("/")
async def root():
    """
    Root endpoint providing server information.
    """
    return {
        "server": "Unreal-Blender MCP",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "stream": "SSE endpoint for AI agent communication",
        }
    } 