"""
Request simulation utilities for testing the MCP server.

This module provides utilities for simulating AI agent requests to the MCP server,
allowing for automated testing of server responses and behavior.
"""

import json
import asyncio
import aiohttp
import uuid
from typing import Dict, List, Any, Optional, AsyncGenerator, Tuple


class RequestSimulator:
    """
    Simulate client requests to the MCP server.
    
    This class provides methods to simulate various kinds of requests
    that an AI agent would make to the MCP server.
    """
    
    def __init__(self, base_url: str = "http://localhost:8300"):
        """
        Initialize the request simulator.
        
        Args:
            base_url: Base URL of the MCP server
        """
        self.base_url = base_url
        self.session = None
        self.connection_id = None
        self.message_history = []
    
    async def __aenter__(self):
        """Enter the async context manager."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager."""
        if self.session:
            await self.session.close()
    
    async def get_server_status(self) -> Dict[str, Any]:
        """
        Get the status of the MCP server.
        
        Returns:
            Server status information
        """
        async with self.session.get(f"{self.base_url}/status") as response:
            return await response.json()
    
    async def send_message(self, role: str, content: str, message_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a message to the server.
        
        Args:
            role: The role of the message sender (user, assistant, system)
            content: The message content
            message_id: Optional message ID (generated if not provided)
            
        Returns:
            Server response
        """
        message_id = message_id or str(uuid.uuid4())
        message = {
            "role": role,
            "content": content,
            "id": message_id
        }
        self.message_history.append(message)
        
        async with self.session.post(
            f"{self.base_url}/message", 
            json=message
        ) as response:
            return await response.json()
    
    async def connect_stream(self) -> Tuple[str, aiohttp.ClientResponse]:
        """
        Connect to the SSE stream.
        
        Returns:
            Tuple of (connection_id, response)
        """
        connection_id = str(uuid.uuid4())
        response = await self.session.get(
            f"{self.base_url}/stream", 
            params={"connection_id": connection_id}
        )
        self.connection_id = connection_id
        return connection_id, response
    
    async def read_stream_events(self, response: aiohttp.ClientResponse) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Read events from an SSE stream.
        
        Args:
            response: The response from connecting to the stream
            
        Yields:
            Parsed events from the stream
        """
        async for line in response.content:
            line = line.decode('utf-8').strip()
            if line.startswith('data:'):
                data = line[5:].strip()
                if data:
                    try:
                        event_data = json.loads(data)
                        yield event_data
                    except json.JSONDecodeError:
                        # Handle non-JSON data
                        yield {"raw_data": data}
    
    async def send_stream_message(self, role: str, content: str, message_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a message to a specific stream.
        
        Args:
            role: The role of the message sender (user, assistant, system)
            content: The message content
            message_id: Optional message ID (generated if not provided)
            
        Returns:
            Server response
        """
        if not self.connection_id:
            raise ValueError("Not connected to a stream. Call connect_stream() first.")
        
        message_id = message_id or str(uuid.uuid4())
        message = {
            "role": role,
            "content": content,
            "id": message_id,
            "connection_id": self.connection_id
        }
        self.message_history.append(message)
        
        async with self.session.post(
            f"{self.base_url}/stream/send", 
            json=message
        ) as response:
            return await response.json()
    
    async def simulate_tool_call(self, tool_name: str, **parameters) -> Dict[str, Any]:
        """
        Simulate a tool call by sending a message that would trigger a tool.
        
        Args:
            tool_name: The name of the tool to call
            **parameters: Parameters to pass to the tool
            
        Returns:
            Server response
        """
        # Format the content to look like a tool call request from an AI agent
        content = f"I want to call the {tool_name} tool with these parameters: {json.dumps(parameters)}"
        return await self.send_message("user", content)
    
    async def simulate_conversation(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Simulate a conversation with the server by sending multiple messages.
        
        Args:
            messages: List of messages to send, each with 'role' and 'content' keys
            
        Returns:
            List of server responses
        """
        responses = []
        for message in messages:
            response = await self.send_message(message["role"], message["content"])
            responses.append(response)
        return responses


class MockConnection:
    """
    Mock connection for testing.
    
    This class simulates a connection to an application (Blender or Unreal Engine)
    for testing the MCP server without actual application connections.
    """
    
    def __init__(self, name: str, expected_responses: Dict[str, Any] = None):
        """
        Initialize the mock connection.
        
        Args:
            name: Name of the mocked connection (e.g., 'blender', 'unreal')
            expected_responses: Dictionary mapping method names to expected responses
        """
        self.name = name
        self.expected_responses = expected_responses or {}
        self.call_history = []
        self.connected = False
    
    async def connect(self) -> bool:
        """
        Simulate connecting to the application.
        
        Returns:
            Success status
        """
        self.connected = True
        self.call_history.append(("connect", {}))
        return self.expected_responses.get("connect", True)
    
    async def close(self) -> None:
        """Simulate closing the connection."""
        self.connected = False
        self.call_history.append(("close", {}))
    
    async def execute_code(self, code: str) -> Any:
        """
        Simulate executing code in the application.
        
        Args:
            code: The code to execute
            
        Returns:
            Simulated execution result
        """
        self.call_history.append(("execute_code", {"code": code}))
        
        # Check if there's a specific response for this code
        for pattern, response in self.expected_responses.items():
            if pattern in code and "execute_code" in pattern:
                return response
        
        # Default response
        return self.expected_responses.get("execute_code", "Code executed successfully")
    
    async def get_scene_info(self) -> Dict[str, Any]:
        """
        Simulate getting scene information.
        
        Returns:
            Simulated scene information
        """
        self.call_history.append(("get_scene_info", {}))
        return self.expected_responses.get("get_scene_info", {"objects": [], "materials": []})
    
    async def get_object_info(self, object_name: str) -> Dict[str, Any]:
        """
        Simulate getting object information.
        
        Args:
            object_name: Name of the object
            
        Returns:
            Simulated object information
        """
        self.call_history.append(("get_object_info", {"object_name": object_name}))
        return self.expected_responses.get(
            f"get_object_info_{object_name}", 
            {"name": object_name, "type": "MESH", "location": [0, 0, 0]}
        )
    
    def get_call_history(self) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get the history of calls made to this mock connection.
        
        Returns:
            List of (method_name, parameters) tuples
        """
        return self.call_history 