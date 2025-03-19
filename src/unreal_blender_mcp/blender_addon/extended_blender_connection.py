"""
Extended Blender Connection for unreal-blender-mcp.

This module extends the BlenderConnection class to communicate with the extended Blender addon.
"""

import logging
import json
import aiohttp
from typing import Dict, Any, Optional, Union, List

from ..blender_connection import BlenderConnection

logger = logging.getLogger(__name__)

class ExtendedBlenderConnection(BlenderConnection):
    """Class for managing connections to the extended Blender addon."""
    
    def __init__(self, host: str = "localhost", port: int = 8401):
        """
        Initialize an Extended Blender connection.
        
        Args:
            host: Host where Blender is running
            port: Port where the extended Blender addon server is listening
                (default is 8401 to avoid conflicts with the original addon)
        """
        # Call the parent constructor with the extended port
        super().__init__(host=host, port=port)
        
    async def get_version_info(self) -> Dict[str, Any]:
        """Get version information from the extended Blender server."""
        return await self.execute_command("get_version_info", {})
    
    async def extended_command_example(self, **params) -> Dict[str, Any]:
        """Execute the example extended command."""
        return await self.execute_command("extended_command_example", params)
    
    # Add any additional extended command methods as needed
    
    async def is_extended_server(self) -> bool:
        """
        Check if the connected server is the extended server by testing an extended command.
        
        Returns:
            bool: True if connected to an extended server, False otherwise
        """
        try:
            response = await self.extended_command_example()
            # If we get a success response, it's an extended server
            return response.get("status") == "success"
        except Exception as e:
            logger.error(f"Error checking if server is extended: {str(e)}")
            return False
    
    async def ensure_extended_server(self) -> bool:
        """
        Ensure we're connected to an extended server. If not, try to reconnect.
        
        Returns:
            bool: True if connected to an extended server, False otherwise
        """
        # First check if we're already connected to an extended server
        if await self.is_extended_server():
            return True
            
        # If not, try to reconnect
        await self.close()
        if await self.connect():
            # Check again if it's an extended server
            return await self.is_extended_server()
        
        return False 