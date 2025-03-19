"""
Unreal Engine Connection management for unreal-blender-mcp.

This module provides functionality to communicate with the Unreal Engine plugin.
"""

import logging
import json
import requests
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
        self.is_connected = False
    
    def connect(self) -> bool:
        """
        Establish connection to Unreal Engine.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Test connection with a simple request
            response = requests.get(f"{self.base_url}/status", timeout=5)
            if response.status_code == 200:
                logger.info(f"Connected to Unreal Engine on {self.host}:{self.port}")
                self.is_connected = True
                return True
            else:
                logger.error(f"Failed to connect to Unreal Engine: {response.status_code}")
                self.is_connected = False
                return False
        except Exception as e:
            logger.error(f"Error connecting to Unreal Engine: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> None:
        """Close the connection to Unreal Engine."""
        self.is_connected = False
        logger.info("Unreal Engine connection closed")
    
    def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code in Unreal Engine.
        
        Args:
            code: Python code to execute
            
        Returns:
            Dict with the execution result and/or error information
        """
        if not self.is_connected:
            connected = self.connect()
            if not connected:
                return {"status": "error", "message": "Not connected to Unreal Engine"}
        
        try:
            payload = {
                "code": code
            }
            
            response = requests.post(
                f"{self.base_url}/execute", 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_text = response.text
                logger.error(f"Error from Unreal Engine: {error_text}")
                return {"status": "error", "message": f"Unreal Engine returned {response.status_code}: {error_text}"}
        except Exception as e:
            logger.error(f"Error executing Unreal Engine code: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # Convenience methods for common Unreal Engine operations
    def create_level(self, level_name: str) -> Dict[str, Any]:
        """Create a new level in Unreal Engine."""
        code = f"import unreal\nunreal.EditorLevelLibrary.new_level('{level_name}')"
        return self.execute_code(code)
    
    def import_asset(self, file_path: str, destination_path: str, asset_name: Optional[str] = None) -> Dict[str, Any]:
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
        return self.execute_code(code)
    
    def get_engine_version(self) -> Dict[str, Any]:
        """Get the Unreal Engine version."""
        code = """
import unreal
version = unreal.SystemLibrary.get_engine_version()
print(version)
"""
        return self.execute_code(code)
        
    def execute_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """일반 명령 실행 메서드 추가"""
        if params is None:
            params = {}
        
        logger.info(f"Executing Unreal command: {command_type} with params: {params}")
        
        if not self.is_connected:
            return {"status": "error", "message": "Not connected to Unreal Engine"}
            
        try:
            return {"status": "success", "message": f"Command {command_type} not implemented yet", "params": params}
        except Exception as e:
            return {"status": "error", "message": f"Error executing command {command_type}: {str(e)}"}

# Create a global instance for convenience
unreal_connection = UnrealConnection() 