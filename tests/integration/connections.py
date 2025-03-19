"""
Utility module for handling connections to Blender and Unreal Engine during testing.
"""

import os
import json
import asyncio
import aiohttp
import tempfile
from typing import Dict, Any, Optional, Union

from tests.integration.test_config import (
    get_blender_server_url,
    get_unreal_server_url,
    get_mcp_server_url
)

class ConnectionError(Exception):
    """Exception raised for connection errors."""
    pass

async def ping_blender() -> bool:
    """
    Check if Blender server is running.
    
    Returns:
        bool: True if Blender server is running, False otherwise.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{get_blender_server_url()}/ping", timeout=5) as response:
                return response.status == 200
    except Exception:
        return False

async def ping_unreal() -> bool:
    """
    Check if Unreal server is running.
    
    Returns:
        bool: True if Unreal server is running, False otherwise.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{get_unreal_server_url()}/status", timeout=5) as response:
                return response.status == 200
    except Exception:
        return False

async def ping_mcp() -> bool:
    """
    Check if MCP server is running.
    
    Returns:
        bool: True if MCP server is running, False otherwise.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{get_mcp_server_url()}/status", timeout=5) as response:
                return response.status == 200
    except Exception:
        return False

async def execute_blender_script(script: str) -> Dict[str, Any]:
    """
    Execute a Python script in Blender.
    
    Args:
        script: The Python script to execute.
        
    Returns:
        dict: The result of the script execution.
        
    Raises:
        ConnectionError: If unable to connect to Blender.
    """
    if not await ping_blender():
        raise ConnectionError("Blender server is not running")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{get_blender_server_url()}/execute",
                json={"code": script},
                timeout=30
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    raise ConnectionError(f"Blender returned error: {error_text}")
    except aiohttp.ClientError as e:
        raise ConnectionError(f"Failed to connect to Blender: {str(e)}")

async def execute_unreal_script(script: str) -> Dict[str, Any]:
    """
    Execute a Python script in Unreal Engine.
    
    Args:
        script: The Python script to execute.
        
    Returns:
        dict: The result of the script execution.
        
    Raises:
        ConnectionError: If unable to connect to Unreal Engine.
    """
    if not await ping_unreal():
        raise ConnectionError("Unreal Engine server is not running")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{get_unreal_server_url()}/execute",
                json={"code": script},
                timeout=30
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    raise ConnectionError(f"Unreal Engine returned error: {error_text}")
    except aiohttp.ClientError as e:
        raise ConnectionError(f"Failed to connect to Unreal Engine: {str(e)}")

async def execute_script_file(file_path: str, app: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute a Python script file in the specified application.
    
    Args:
        file_path: Path to the script file.
        app: 'blender' or 'unreal'
        data: Optional data to pass to the script.
        
    Returns:
        dict: The result of the script execution.
        
    Raises:
        ValueError: If the app is not 'blender' or 'unreal'.
        FileNotFoundError: If the script file does not exist.
        ConnectionError: If unable to connect to the application.
    """
    if app not in ['blender', 'unreal']:
        raise ValueError("app must be 'blender' or 'unreal'")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Script file not found: {file_path}")
    
    # Read the script file
    with open(file_path, 'r') as f:
        script = f.read()
    
    # Add data to the script if provided
    if data:
        data_str = json.dumps(data)
        script = f"data = '''{data_str}'''\n{script}"
    
    # Execute the script
    if app == 'blender':
        return await execute_blender_script(script)
    else:  # app == 'unreal'
        return await execute_unreal_script(script)

async def send_mcp_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a message to the MCP server.
    
    Args:
        message: The message to send.
        
    Returns:
        dict: The response from the MCP server.
        
    Raises:
        ConnectionError: If unable to connect to the MCP server.
    """
    if not await ping_mcp():
        raise ConnectionError("MCP server is not running")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{get_mcp_server_url()}/message",
                json=message,
                timeout=30
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    raise ConnectionError(f"MCP server returned error: {error_text}")
    except aiohttp.ClientError as e:
        raise ConnectionError(f"Failed to connect to MCP server: {str(e)}")

async def execute_cross_platform_workflow(
    blender_script_path: str,
    unreal_script_path: str
) -> Dict[str, Any]:
    """
    Execute a cross-platform workflow, typically exporting from Blender and importing to Unreal.
    
    Args:
        blender_script_path: Path to the Blender script file.
        unreal_script_path: Path to the Unreal script file.
        
    Returns:
        dict: The combined results of both script executions.
        
    Raises:
        ConnectionError: If unable to connect to either application.
    """
    # Execute the Blender script
    blender_result = await execute_script_file(blender_script_path, 'blender')
    
    # Extract the export path from the Blender result
    if blender_result.get('status') != 'success':
        return {
            'status': 'error',
            'message': f"Blender script failed: {blender_result.get('message', 'Unknown error')}",
            'blender_result': blender_result
        }
    
    # Execute the Unreal script with the Blender result data
    unreal_result = await execute_script_file(unreal_script_path, 'unreal', blender_result)
    
    # Return the combined results
    return {
        'status': 'success' if unreal_result.get('status') == 'success' else 'error',
        'message': f"Cross-platform workflow completed: {unreal_result.get('message', 'Unknown result')}",
        'blender_result': blender_result,
        'unreal_result': unreal_result
    } 