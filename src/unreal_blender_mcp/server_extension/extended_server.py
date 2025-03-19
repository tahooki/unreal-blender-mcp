"""
Extended Server for unreal-blender-mcp

This module extends the original BlenderMCP server from blender-mcp to provide
additional functionality while maintaining compatibility with upstream updates.
"""

import sys
import os
import importlib.util
import logging
from typing import Dict, Any, Optional, Union, List, AsyncIterator
import json
import asyncio

# Get the path to the original blender-mcp addon
BLENDER_MCP_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'blender-mcp'))
BLENDER_MCP_SRC_PATH = os.path.join(BLENDER_MCP_PATH, 'src')

# Add the blender-mcp directory to the Python path
if BLENDER_MCP_PATH not in sys.path:
    sys.path.append(BLENDER_MCP_PATH)
if BLENDER_MCP_SRC_PATH not in sys.path:
    sys.path.append(BLENDER_MCP_SRC_PATH)

# Import the original BlenderMCP server module
try:
    # First try to import directly
    from blender_mcp.server import mcp, BlenderConnection, get_blender_connection
except ImportError:
    # If direct import fails, use importlib to load from the absolute path
    spec = importlib.util.spec_from_file_location(
        "blender_mcp.server", 
        os.path.join(BLENDER_MCP_SRC_PATH, "blender_mcp", "server.py")
    )
    server_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_module)
    mcp = server_module.mcp
    BlenderConnection = server_module.BlenderConnection
    get_blender_connection = server_module.get_blender_connection

# Set up logger
logger = logging.getLogger("ExtendedBlenderMCPServer")

# Custom extended connection class that inherits from original
class ExtendedBlenderConnection(BlenderConnection):
    """Extended version of BlenderConnection with additional functionality."""
    
    def __init__(self, host: str = "localhost", port: int = 9876):
        """
        Initialize an extended Blender connection.
        
        Args:
            host: Host where Blender is running
            port: Port where the Blender addon server is listening
        """
        super().__init__(host, port)
        self.extended_features_enabled = False
    
    def connect(self) -> bool:
        """Connect and check for extended features support"""
        if super().connect():
            # After connecting, check if the server supports extended features
            try:
                result = self.send_command("get_version_info", {})
                self.extended_features_enabled = "extended_version" in result
                if self.extended_features_enabled:
                    logger.info(f"Connected to extended Blender addon v{result['extended_version']}")
                else:
                    logger.info("Connected to standard Blender addon (no extended features)")
                return True
            except Exception as e:
                # If the command fails, it's likely not an extended server
                logger.info("Connected to standard Blender addon (extended features check failed)")
                self.extended_features_enabled = False
                return True
        return False
    
    def send_extended_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command that's only available in the extended addon"""
        if not self.extended_features_enabled:
            raise Exception("Extended features not available in connected Blender addon")
        return self.send_command(command_type, params)

# Create global extended connection variable
_extended_blender_connection = None

def get_extended_blender_connection():
    """Get or create a persistent extended Blender connection"""
    global _extended_blender_connection
    
    # If we have an existing connection, check if it's still valid
    if _extended_blender_connection is not None:
        try:
            # Test the connection with a ping
            result = _extended_blender_connection.send_command("get_scene_info")
            return _extended_blender_connection
        except Exception as e:
            # Connection is dead, close it and create a new one
            logger.warning(f"Existing extended connection is no longer valid: {str(e)}")
            try:
                _extended_blender_connection.disconnect()
            except:
                pass
            _extended_blender_connection = None
    
    # Create a new connection if needed
    if _extended_blender_connection is None:
        _extended_blender_connection = ExtendedBlenderConnection(host="localhost", port=9876)
        if not _extended_blender_connection.connect():
            logger.error("Failed to connect to Blender")
            _extended_blender_connection = None
            raise Exception("Could not connect to Blender. Make sure the Blender addon is running.")
        logger.info("Created new persistent extended connection to Blender")
    
    return _extended_blender_connection

# Define additional tools using the original MCP server as a base
@mcp.tool()
def extended_scene_info(ctx) -> str:
    """
    Get enhanced scene information with additional details not available in the standard addon.
    This tool uses the extended Blender addon functionality if available.
    """
    try:
        blender = get_extended_blender_connection()
        
        # If extended features are available, use them
        if blender.extended_features_enabled:
            result = blender.send_extended_command("get_version_info", {})
            extended_info = {
                "extended_info_available": True,
                "extended_version": result.get("extended_version", "unknown"),
                "scene_info": blender.send_command("get_scene_info")
            }
            return json.dumps(extended_info, indent=2)
        else:
            # Fall back to standard scene info
            result = blender.send_command("get_scene_info")
            return json.dumps({
                "extended_info_available": False,
                "scene_info": result
            }, indent=2)
    except Exception as e:
        logger.error(f"Error getting extended scene info: {str(e)}")
        return f"Error getting extended scene info: {str(e)}"

@mcp.tool()
def extended_command_example(ctx, param1: str = "", param2: int = 0) -> str:
    """
    Example of a tool that uses the extended Blender addon's custom commands.
    This tool will only work if the Blender addon has the extended functionality.
    
    Parameters:
    - param1: A string parameter
    - param2: An integer parameter
    """
    try:
        blender = get_extended_blender_connection()
        
        # Check if extended features are available
        if not blender.extended_features_enabled:
            return "This tool requires the extended Blender addon. Please install and enable it."
        
        # Call the extended command
        result = blender.send_extended_command("extended_command_example", {
            "param1": param1,
            "param2": param2
        })
        
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error executing extended command: {str(e)}")
        return f"Error executing extended command: {str(e)}"

# Extended server class that enhances the original server
class ExtendedBlenderMCPServer:
    """
    Extended version of the BlenderMCP server with additional tools and features.
    """
    
    def __init__(self):
        """Initialize the extended server."""
        self.mcp = mcp
        
        # Register any additional configuration or setup here
        logger.info("Extended BlenderMCP server initialized")
    
    def register_additional_tools(self):
        """Register additional tools not defined in this module."""
        # This method can be used to dynamically register more tools
        pass
    
    async def start(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the extended server."""
        logger.info(f"Starting extended BlenderMCP server on {host}:{port}")
        
        # Register any additional tools
        self.register_additional_tools()
        
        # Start the FastAPI server that powers MCP
        await self.mcp.start(host=host, port=port)

def run_extended_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the extended MCP server."""
    server = ExtendedBlenderMCPServer()
    
    # Create and run the asyncio event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(server.start(host=host, port=port))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        loop.close()

# Allow direct execution
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_extended_server() 