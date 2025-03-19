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

from .blender_addon_server.extended_server import (
    get_extended_blender_connection,
    DummyBlenderConnection,
    BlenderConnection
)
from .unreal_connection import UnrealConnection
from .langchain_integration import LangchainManager
from .ai_tools import ToolHandler
from .ai_tools.prompt_engineering import (
    get_claude_system_prompt,
    get_chatgpt_system_prompt,
    get_cursor_system_prompt,
    get_example_conversations,
    get_error_recovery_prompts
)

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

# Connection initialization (ExtendedBlenderConnection 사용)
try:
    logger.info("Attempting to connect to Blender...")
    blender_connection = get_extended_blender_connection()
    logger.info("Successfully connected to Blender")
except Exception as e:
    logger.warning(f"Failed to connect to Blender: {str(e)}")
    logger.warning("Using dummy Blender connection instead. Some features may not work.")
    blender_connection = DummyBlenderConnection()

# Initialize Unreal connection
unreal_connection = UnrealConnection()
langchain_manager = LangchainManager()
tool_handler = ToolHandler(blender_connection, unreal_connection)

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
        # Check if it's an AI tool (prefixed with mcp_)
        if tool_name.startswith("mcp_"):
            return tool_handler.handle_tool_call(tool_name, tool_args)
        
        # Legacy tool calls (for backward compatibility)
        # Blender tool calls
        elif tool_name == "get_scene_info":
            return blender_connection.get_scene_info()
        elif tool_name == "get_object_info":
            if "object_name" not in tool_args:
                raise ValueError("Missing required argument: object_name")
            return blender_connection.get_object_info(tool_args.get("object_name"))
        elif tool_name == "create_object":
            if "type" not in tool_args:
                raise ValueError("Missing required argument: type")
            return blender_connection.create_object(
                type=tool_args.get("type"),
                name=tool_args.get("name"),
                location=tool_args.get("location"),
                rotation=tool_args.get("rotation"),
                scale=tool_args.get("scale")
            )
        elif tool_name == "execute_blender_code":
            if "code" not in tool_args:
                raise ValueError("Missing required argument: code")
            return blender_connection.execute_code(tool_args.get("code"))
        
        # Unreal tool calls
        elif tool_name == "create_level":
            if "level_name" not in tool_args:
                raise ValueError("Missing required argument: level_name")
            return unreal_connection.create_level(tool_args.get("level_name"))
        elif tool_name == "import_asset":
            if "file_path" not in tool_args or "destination_path" not in tool_args:
                raise ValueError("Missing required arguments: file_path and/or destination_path")
            return unreal_connection.import_asset(
                tool_args.get("file_path"),
                tool_args.get("destination_path"),
                tool_args.get("asset_name")
            )
        elif tool_name == "get_engine_version":
            return unreal_connection.get_engine_version()
        elif tool_name == "execute_unreal_code":
            if "code" not in tool_args:
                raise ValueError("Missing required argument: code")
            return unreal_connection.execute_code(tool_args.get("code"))
        
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
                    "status": "success"
                })
            }
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        logger.error(traceback.format_exc())
        yield {
            "event": "error",
            "data": json.dumps({
                "status": "error",
                "message": str(e)
            })
        }

# Routes

@app.get("/")
async def root():
    """Root endpoint that returns server information."""
    try:
        # is_connected 속성 대신 extended_features_enabled 속성 사용
        blender_status = "connected" if blender_connection.extended_features_enabled else "disconnected"
        unreal_status = "connected" if unreal_connection.is_connected else "disconnected"
        
        return create_success_response({
            "name": "Unreal-Blender MCP Server",
            "status": "running",
            "connections": {
                "blender": blender_status,
                "unreal": unreal_status
            },
            "active_streams": len(active_connections)
        }, "Server is running")
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sse")
async def stream_endpoint(request: Request):
    """
    Establish a server-sent events stream for real-time communication.
    
    Returns:
        EventSourceResponse: A stream of server-sent events
    """
    try:
        # Generate a unique connection ID
        connection_id = generate_id()
        
        # Create a new queue for this connection
        queue = asyncio.Queue()
        
        # Store connection in active_connections
        active_connections[connection_id] = {
            "queue": queue,
            "created_at": time.time()
        }
        
        logger.info(f"New SSE connection established: {connection_id}")
        
        # Send initial connection message
        await queue.put({
            "event": "connected",
            "data": json.dumps({
                "connection_id": connection_id,
                "message": "Connection established"
            })
        })
        
        async def event_generator():
            try:
                # Keep the connection open
                while True:
                    # Get the next message from the queue
                    message = await queue.get()
                    
                    # Check if the message is a disconnect signal
                    if message.get("event") == "disconnect":
                        break
                    
                    # Yield the message to the client
                    yield message
                    
                    # Mark the task as done
                    queue.task_done()
            except asyncio.CancelledError:
                logger.info(f"Stream connection closed: {connection_id}")
            finally:
                # Remove connection when client disconnects
                if connection_id in active_connections:
                    del active_connections[connection_id]
                logger.info(f"Stream connection removed: {connection_id}")
        
        # Return the event stream
        return EventSourceResponse(event_generator())
    except Exception as e:
        logger.error(f"Error in stream endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/message")
async def message_endpoint(message: Message):
    """
    Process a message from an AI agent.
    
    Args:
        message: The message to process
        
    Returns:
        Dict with the result
    """
    try:
        # For non-streaming responses, collect all results
        results = []
        async for result in process_message(message):
            results.append(result)
        
        return create_success_response({
            "results": results
        }, "Message processed")
    except Exception as e:
        logger.error(f"Error in message endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream/send")
async def send_to_stream(message: Message, connection_id: str):
    """
    Send a message to a specific stream connection.
    
    Args:
        message: The message to send
        connection_id: ID of the connection to send to
        
    Returns:
        Dict with the result
    """
    try:
        # Check if the connection exists
        if connection_id not in active_connections:
            raise HTTPException(status_code=404, detail=f"Connection not found: {connection_id}")
        
        # Get the connection queue
        queue = active_connections[connection_id]["queue"]
        
        # Process the message and send results to the queue
        background_tasks = BackgroundTasks()
        
        async def process_and_queue():
            async for result in process_message(message):
                await queue.put(result)
        
        # Add the task to the background tasks
        background_tasks.add_task(process_and_queue)
        
        return JSONResponse(
            content=create_success_response({
                "connection_id": connection_id,
                "message": "Message sent to stream"
            }),
            background=background_tasks
        )
    except Exception as e:
        logger.error(f"Error in send_to_stream endpoint: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/prompts")
async def get_ai_prompts(
    platform: Optional[str] = None,
    ai_type: Optional[str] = "claude"
):
    """
    Get system prompts for AI agents.
    
    Args:
        platform: Platform to include in prompts (blender, unreal, or both)
        ai_type: Type of AI agent (claude, chatgpt, cursor)
        
    Returns:
        Dict with the system prompt
    """
    try:
        include_blender = platform in [None, "blender", "both"]
        include_unreal = platform in [None, "unreal", "both"]
        
        if ai_type == "claude":
            prompt = get_claude_system_prompt(include_blender, include_unreal)
        elif ai_type == "chatgpt":
            prompt = get_chatgpt_system_prompt(include_blender, include_unreal)
        elif ai_type == "cursor":
            prompt = get_cursor_system_prompt(include_blender, include_unreal)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported AI type: {ai_type}")
        
        return create_success_response({
            "prompt": prompt,
            "ai_type": ai_type,
            "platforms": {
                "blender": include_blender,
                "unreal": include_unreal
            }
        })
    except Exception as e:
        logger.error(f"Error in get_ai_prompts endpoint: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/examples")
async def get_ai_examples():
    """
    Get example conversations for AI agents.
    
    Returns:
        Dict with example conversations
    """
    try:
        examples = get_example_conversations()
        return create_success_response({
            "examples": examples
        })
    except Exception as e:
        logger.error(f"Error in get_ai_examples endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/tools")
async def get_ai_tools(category: Optional[str] = None):
    """
    Get available AI tools.
    
    Args:
        category: Optional category to filter by (blender or unreal)
        
    Returns:
        Dict with available tools
    """
    try:
        tools = tool_handler.list_available_tools()
        
        if category:
            tools = [tool for tool in tools if tool.get("category") == category]
        
        return create_success_response({
            "tools": tools,
            "category": category
        })
    except Exception as e:
        logger.error(f"Error in get_ai_tools endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def status_endpoint():
    """Get the status of all connections."""
    try:
        # Try to connect to Blender if not already connected
        blender_status = {
            "connected": blender_connection.extended_features_enabled
        }
        if not blender_connection.extended_features_enabled:
            try:
                blender_connection.connect()  # 이제 동기 메서드 사용
                blender_status["connected"] = True
                blender_status["message"] = "Connected successfully"
            except Exception as e:
                blender_status["error"] = str(e)
        
        # Try to connect to Unreal if not already connected
        unreal_status = {
            "connected": unreal_connection.is_connected
        }
        if not unreal_connection.is_connected:
            try:
                unreal_connection.connect()
                unreal_status["connected"] = True
                unreal_status["message"] = "Connected successfully"
            except Exception as e:
                unreal_status["error"] = str(e)
        
        return create_success_response({
            "server": {
                "status": "running",
                "uptime": time.time() - startup_time
            },
            "connections": {
                "blender": blender_status,
                "unreal": unreal_status
            },
            "active_streams": len(active_connections)
        })
    except Exception as e:
        logger.error(f"Error in status endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Server events
startup_time = 0

@app.on_event("startup")
async def startup_event():
    """Initialize connections on server startup."""
    global startup_time
    startup_time = time.time()
    logger.info("Server starting up...")
    
    # Connect to Blender and Unreal
    global blender_connection
    if isinstance(blender_connection, DummyBlenderConnection):
        # 더미 연결 사용 중이면 다시 연결 시도
        try:
            logger.info("Attempting to reconnect to Blender...")
            real_connection = get_extended_blender_connection()
            # 성공하면 글로벌 변수 업데이트
            blender_connection = real_connection
            logger.info("Connected to Blender")
        except Exception as e:
            logger.warning(f"Could not connect to Blender: {str(e)}")
    else:
        # 이미 연결된 경우 연결 확인
        try:
            logger.info("Validating Blender connection...")
            blender_connection.send_command("get_scene_info")
            logger.info("Connected to Blender")
        except Exception as e:
            logger.warning(f"Blender connection validation failed: {str(e)}")
            try:
                # 다시 연결 시도
                blender_connection.connect()
                logger.info("Reconnected to Blender")
            except Exception as reconnect_error:
                logger.warning(f"Could not reconnect to Blender: {str(reconnect_error)}")
    
    try:
        unreal_connection.connect()
        logger.info("Connected to Unreal Engine")
    except Exception as e:
        logger.warning(f"Could not connect to Unreal Engine: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up when the server shuts down."""
    logger.info("Server shutting down...")
    
    # Clean up connections
    try:
        # Get all extended connection instances
        if hasattr(blender_connection, "disconnect"):
            blender_connection.disconnect()
        else:
            logger.warning("Blender connection does not have disconnect method")
    except Exception as e:
        logger.error(f"Error disconnecting from Blender: {str(e)}")
    
    try:
        # Properly close the Unreal connection
        if hasattr(unreal_connection, "disconnect"):
            unreal_connection.disconnect()
        else:
            logger.warning("Unreal connection does not have disconnect method")
    except Exception as e:
        logger.error(f"Error disconnecting from Unreal Engine: {str(e)}")
    
    # Clean up all active connections
    for conn_id, conn_data in list(active_connections.items()):
        try:
            active_connections.pop(conn_id)
        except Exception as e:
            logger.error(f"Error cleaning up connection {conn_id}: {str(e)}")
    
    logger.info("Server shutdown complete") 