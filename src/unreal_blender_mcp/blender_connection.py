"""
Blender Connection management for unreal-blender-mcp.

This module provides functionality to communicate with the Blender addon.
"""

import logging
import json
import aiohttp
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class BlenderConnection:
    """Class for managing connections to Blender."""
    
    def __init__(self, host: str = "localhost", port: int = 8400):
        """
        Initialize a Blender connection.
        
        Args:
            host: Host where Blender is running
            port: Port where the Blender addon server is listening
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.session = None
    
    async def connect(self) -> bool:
        """
        Establish connection to Blender.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.session is not None:
            await self.close()
            
        self.session = aiohttp.ClientSession()
        try:
            # Test connection with a simple ping
            async with self.session.get(f"{self.base_url}/ping", timeout=5) as response:
                if response.status == 200:
                    logger.info(f"Connected to Blender on {self.host}:{self.port}")
                    return True
                else:
                    logger.error(f"Failed to connect to Blender: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error connecting to Blender: {str(e)}")
            return False
    
    async def close(self) -> None:
        """Close the connection to Blender."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Blender connection closed")
    
    async def execute_command(self, command_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command on Blender.
        
        Args:
            command_type: Type of command to execute
            params: Parameters for the command
            
        Returns:
            Dict with the response from Blender
        """
        if not self.session:
            connected = await self.connect()
            if not connected:
                return {"status": "error", "message": "Not connected to Blender"}
        
        try:
            payload = {
                "type": command_type,
                "params": params
            }
            
            async with self.session.post(
                f"{self.base_url}/execute", 
                json=payload, 
                timeout=30
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Error from Blender: {error_text}")
                    return {"status": "error", "message": f"Blender returned {response.status}: {error_text}"}
        except Exception as e:
            logger.error(f"Error executing Blender command: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # Convenience methods for common Blender operations
    
    async def get_scene_info(self) -> Dict[str, Any]:
        """Get information about the current Blender scene."""
        return await self.execute_command("get_scene_info", {})
    
    async def get_object_info(self, object_name: str) -> Dict[str, Any]:
        """Get information about a specific object in Blender."""
        return await self.execute_command("get_object_info", {"object_name": object_name})
    
    async def create_object(
        self, 
        object_type: str, 
        name: Optional[str] = None,
        location: Optional[list] = None,
        rotation: Optional[list] = None,
        scale: Optional[list] = None
    ) -> Dict[str, Any]:
        """Create a new object in Blender."""
        params = {"type": object_type}
        if name is not None:
            params["name"] = name
        if location is not None:
            params["location"] = location
        if rotation is not None:
            params["rotation"] = rotation
        if scale is not None:
            params["scale"] = scale
            
        return await self.execute_command("create_object", params)
    
    async def execute_code(self, code: str) -> Dict[str, Any]:
        """Execute arbitrary Python code in Blender."""
        return await self.execute_command("execute_code", {"code": code}) 