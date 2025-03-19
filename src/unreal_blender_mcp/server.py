"""
MCP Server implementation for unreal-blender-mcp.

This module provides the core server functionality for the unified MCP server
that connects AI agents with Blender and Unreal Engine.
"""

import logging
import json
import uuid
import asyncio
import traceback
from typing import Dict, List, Any, Optional, AsyncGenerator, Union
from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError
import time
from sse_starlette.sse import EventSourceResponse

from .blender_connection import BlenderConnection
from .unreal_connection import UnrealConnection
from .langchain_integration import LangchainManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Unreal-Blender MCP Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections
active_connections: Dict[str, Dict[str, Any]] = {}

# Message models
class Message(BaseModel):
    """Model for messages exchanged with the AI agent."""
    role: str = Field(..., description="Role of the message sender (e.g., user, assistant, system)")
    content: str = Field(..., description="Content of the message")
    id: Optional[str] = Field(None, description="Message ID")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls requested by the agent")

class StreamRequest(BaseModel):
    """Model for stream requests."""
    messages: List[Message] = Field(..., description="List of messages in the conversation")

class ErrorResponse(BaseModel):
    """Model for standardized error responses."""
    status: str = "error"
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None

class SuccessResponse(BaseModel):
    """Model for standardized success responses."""
    status: str = "success"
    data: Dict[str, Any]
    message: Optional[str] = None

# Connection initialization
blender_connection = BlenderConnection()
unreal_connection = UnrealConnection()
langchain_manager = LangchainManager()

# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors in a standardized way."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation error",
            details={"errors": exc.errors()}
        ).dict(),
    )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions in a standardized way."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.status_code,
            message=exc.detail,
            details=None
        ).dict(),
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions in a standardized way."""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            details={"error": str(exc)}
        ).dict(),
    )

# Utility functions
def generate_id() -> str:
    """Generate a unique ID for messages."""
    return str(uuid.uuid4())

def create_success_response(data: Dict[str, Any], message: Optional[str] = None) -> Dict[str, Any]:
    """Create a standardized success response."""
    return SuccessResponse(
        data=data,
        message=message
    ).dict()

def create_error_response(code: int, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a standardized error response."""
    return ErrorResponse(
        code=code,
        message=message,
        details=details
    ).dict()

async def handle_tool_call(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a tool call from the AI agent.
    
    Args:
        tool_name: Name of the tool to call
        tool_args: Arguments for the tool
        
    Returns:
        Dict with the result of the tool call
    """
    logger.info(f"Handling tool call: {tool_name} with args: {tool_args}")
    
    try:
        # Blender tool calls
        if tool_name == "get_scene_info":
            return await blender_connection.get_scene_info()
        elif tool_name == "get_object_info":
            if "object_name" not in tool_args:
                raise ValueError("Missing required argument: object_name")
            return await blender_connection.get_object_info(tool_args.get("object_name"))
        elif tool_name == "create_object":
            if "type" not in tool_args:
                raise ValueError("Missing required argument: type")
            return await blender_connection.create_object(
                object_type=tool_args.get("type"),
                name=tool_args.get("name"),
                location=tool_args.get("location"),
                rotation=tool_args.get("rotation"),
                scale=tool_args.get("scale")
            )
        elif tool_name == "execute_blender_code":
            if "code" not in tool_args:
                raise ValueError("Missing required argument: code")
            return await blender_connection.execute_code(tool_args.get("code"))
        
        # Unreal tool calls
        elif tool_name == "create_level":
            if "level_name" not in tool_args:
                raise ValueError("Missing required argument: level_name")
            return await unreal_connection.create_level(tool_args.get("level_name"))
        elif tool_name == "import_asset":
            if "file_path" not in tool_args or "destination_path" not in tool_args:
                raise ValueError("Missing required arguments: file_path and/or destination_path")
            return await unreal_connection.import_asset(
                tool_args.get("file_path"),
                tool_args.get("destination_path")
            )
        elif tool_name == "get_engine_version":
            return await unreal_connection.get_engine_version()
        elif tool_name == "execute_unreal_code":
            if "code" not in tool_args:
                raise ValueError("Missing required argument: code")
            return await unreal_connection.execute_code(tool_args.get("code"))
        
        # Unknown tool
        else:
            return {
                "status": "error", 
                "message": f"Unknown tool: {tool_name}"
            }
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": f"Error executing tool {tool_name}: {str(e)}"
        }

async def process_message(message: Message) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Process a message from the AI agent.
    
    Args:
        message: The message to process
        
    Yields:
        Dict with the processed message or tool call result
    """
    try:
        # Store message in Langchain memory
        langchain_manager.store_memory(f"message_{int(time.time())}", message.dict())
        
        # If message has tool calls, process them
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})
                
                try:
                    result = await handle_tool_call(tool_name, tool_args)
                    yield {
                        "event": "tool_result",
                        "data": json.dumps({
                            "tool_call_id": tool_call.get("id"),
                            "result": result
                        })
                    }
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {str(e)}")
                    logger.error(traceback.format_exc())
                    yield {
                        "event": "tool_error",
                        "data": json.dumps({
                            "tool_call_id": tool_call.get("id"),
                            "error": str(e)
                        })
                    }
        else:
            # Regular message, just acknowledge receipt
            yield {
                "event": "message_received",
                "data": json.dumps({
                    "id": message.id or generate_id(),
                    "content": "Message received"
                })
            }
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        logger.error(traceback.format_exc())
        yield {
            "event": "error",
            "data": json.dumps({
                "message": f"Error processing message: {str(e)}"
            })
        }

# API Endpoints
@app.get("/")
async def root():
    """
    Root endpoint providing server information.
    """
    return create_success_response({
        "server": "Unreal-Blender MCP",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "stream": "SSE endpoint for AI agent communication",
            "status": "Status information about connected services"
        }
    })

@app.get("/stream")
async def stream_endpoint(request: Request):
    """
    SSE endpoint for AI agent communication.
    This endpoint establishes a long-lived connection with the AI agent.
    """
    try:
        # Generate a connection ID
        connection_id = generate_id()
        
        # Register the connection
        active_connections[connection_id] = {
            "created_at": time.time(),
            "last_active": time.time(),
            "request": request
        }
        
        logger.info(f"New connection established: {connection_id}")
        
        async def event_generator():
            try:
                # Send initial welcome message
                yield {
                    "event": "connected",
                    "data": json.dumps({
                        "connection_id": connection_id,
                        "message": "Connected to Unreal-Blender MCP Server"
                    })
                }
                
                # Keep the connection alive
                while True:
                    if await request.is_disconnected():
                        logger.info(f"Client disconnected: {connection_id}")
                        if connection_id in active_connections:
                            del active_connections[connection_id]
                        break
                    
                    # Send a heartbeat every 30 seconds
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps({
                            "timestamp": time.time()
                        })
                    }
                    
                    # Update last active time
                    if connection_id in active_connections:
                        active_connections[connection_id]["last_active"] = time.time()
                    
                    await asyncio.sleep(30)
                    
            except Exception as e:
                logger.error(f"Error in event generator: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Send error to client
                yield {
                    "event": "error",
                    "data": json.dumps({
                        "message": f"Stream error: {str(e)}"
                    })
                }
                
                if connection_id in active_connections:
                    del active_connections[connection_id]
        
        return EventSourceResponse(event_generator())
    except Exception as e:
        logger.error(f"Error in stream endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stream error: {str(e)}"
        )

@app.post("/message")
async def message_endpoint(message: Message):
    """
    Endpoint for receiving individual messages.
    This is useful for clients that can't maintain an SSE connection.
    """
    try:
        # Process the message
        results = []
        async for result in process_message(message):
            results.append(result)
        
        # Return the results
        return create_success_response({"results": results})
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )

@app.post("/stream/send")
async def send_to_stream(message: Message, connection_id: str):
    """
    Send a message to a specific SSE stream.
    This is useful for sending messages from one client to another.
    """
    try:
        if connection_id not in active_connections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connection {connection_id} not found"
            )
        
        # Process the message and get results
        results = []
        async for result in process_message(message):
            results.append(result)
        
        return create_success_response({"sent": True, "results": results})
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error sending to stream: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending to stream: {str(e)}"
        )

@app.get("/status")
async def status_endpoint():
    """
    Status information about connected services.
    """
    try:
        # Check Blender connection
        blender_status = "Connected" if await blender_connection.connect() else "Disconnected"
        if blender_status == "Connected":
            await blender_connection.close()
        
        # Check Unreal connection
        unreal_status = "Connected" if await unreal_connection.connect() else "Disconnected"
        if unreal_status == "Connected":
            await unreal_connection.close()
        
        return create_success_response({
            "server": "running",
            "active_connections": len(active_connections),
            "blender": blender_status,
            "unreal": unreal_status,
            "langchain": "Active"
        })
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking status: {str(e)}"
        )

@app.on_event("startup")
async def startup_event():
    """
    Executed when the server starts up.
    """
    logger.info("Starting Unreal-Blender MCP Server")
    
@app.on_event("shutdown")
async def shutdown_event():
    """
    Executed when the server shuts down.
    """
    logger.info("Shutting down Unreal-Blender MCP Server")
    
    try:
        await blender_connection.close()
    except Exception as e:
        logger.error(f"Error closing Blender connection: {str(e)}")
    
    try:
        await unreal_connection.close()
    except Exception as e:
        logger.error(f"Error closing Unreal connection: {str(e)}")
        
    logger.info("Connections closed") 