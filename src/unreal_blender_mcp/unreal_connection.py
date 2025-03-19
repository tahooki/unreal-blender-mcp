"""
Unreal Engine Connection management for unreal-blender-mcp.

This module provides functionality to communicate with the Unreal Engine plugin.
"""

import logging
import json
import aiohttp
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class UnrealConnection:
    """Class for managing connections to Unreal Engine."""
    
    def __init__(self, host: str = "localhost", port: int = 8500):
        """
        Initialize an Unreal Engine connection.
        
        Args:
            host: Host where Unreal Engine is running
            port: Port where the Unreal plugin server is listening
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.session = None
    
    async def connect(self) -> bool:
        """
        Establish connection to Unreal Engine.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.session is not None:
            await self.close()
            
        self.session = aiohttp.ClientSession()
        try:
            # Test connection with a simple request
            async with self.session.get(f"{self.base_url}/status", timeout=5) as response:
                if response.status == 200:
                    logger.info(f"Connected to Unreal Engine on {self.host}:{self.port}")
                    return True
                else:
                    logger.error(f"Failed to connect to Unreal Engine: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error connecting to Unreal Engine: {str(e)}")
            return False
    
    async def close(self) -> None:
        """Close the connection to Unreal Engine."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Unreal Engine connection closed")
    
    async def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code in Unreal Engine.
        
        Args:
            code: Python code to execute
            
        Returns:
            Dict with the execution result and/or error information
        """
        if not self.session:
            connected = await self.connect()
            if not connected:
                return {"status": "error", "message": "Not connected to Unreal Engine"}
        
        try:
            payload = {
                "code": code
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
                    logger.error(f"Error from Unreal Engine: {error_text}")
                    return {"status": "error", "message": f"Unreal Engine returned {response.status}: {error_text}"}
        except Exception as e:
            logger.error(f"Error executing Unreal Engine code: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # Convenience methods for common Unreal Engine operations
    
    async def create_level(self, level_name: str) -> Dict[str, Any]:
        """Create a new level in Unreal Engine."""
        code = f"import unreal\nunreal.EditorLevelLibrary.new_level('{level_name}')"
        return await self.execute_code(code)
    
    async def import_asset(self, file_path: str, destination_path: str) -> Dict[str, Any]:
        """Import an asset into Unreal Engine."""
        code = f"""
import unreal
import os

file_path = '{file_path}'
destination_path = '{destination_path}'

task = unreal.AssetImportTask()
task.filename = file_path
task.destination_path = destination_path
task.automated = True
task.save = True

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
print(f"Imported {os.path.basename(file_path)} to {destination_path}")
"""
        return await self.execute_code(code)
    
    async def get_engine_version(self) -> Dict[str, Any]:
        """Get the Unreal Engine version."""
        code = """
import unreal
version = unreal.SystemLibrary.get_engine_version()
print(version)
"""
        return await self.execute_code(code) 