"""
Tool handler for AI agent tool calls.

This module processes tool calls from AI agents and routes them to the appropriate
Blender or Unreal Engine connection for execution.
"""

import json
import logging
from typing import Dict, Any, Union, Optional, List, Tuple

from ..blender_addon_server.extended_server import ExtendedBlenderConnection as BlenderConnection
from ..unreal_connection import UnrealConnection
from .tool_definitions import get_tool_by_name, ALL_TOOLS

# Set up logging
logger = logging.getLogger(__name__)

class ToolHandler:
    """
    Handler for AI agent tool calls.
    
    This class processes tool calls from AI agents and routes them to the
    appropriate connection for execution.
    """
    
    def __init__(self, blender_connection: BlenderConnection, unreal_connection: UnrealConnection):
        """
        Initialize the tool handler.
        
        Args:
            blender_connection: Connection to Blender
            unreal_connection: Connection to Unreal Engine
        """
        self.blender_connection = blender_connection
        self.unreal_connection = unreal_connection
        
    def handle_tool_call(self, tool_name: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle a tool call from an AI agent.
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments for the tool execution
            
        Returns:
            Result of the tool execution
        """
        logger.info(f"Handling tool call: {tool_name} with args: {args}")
        
        # Get tool definition
        tool_def = get_tool_by_name(tool_name)
        if not tool_def:
            error_msg = f"Unknown tool: {tool_name}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        # Ensure args is a dictionary
        if args is None:
            args = {}
            
        # Validate required parameters
        missing_params = []
        for param_name, param_desc in tool_def.get("parameters", {}).items():
            if "(required)" in param_desc and param_name not in args:
                missing_params.append(param_name)
                
        if missing_params:
            error_msg = f"Missing required parameters for {tool_name}: {', '.join(missing_params)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        # Route to the appropriate handler based on the tool category
        category = tool_def.get("category")
        if category == "blender":
            return self._handle_blender_tool(tool_name, args)
        elif category == "unreal":
            return self._handle_unreal_tool(tool_name, args)
        else:
            error_msg = f"Unknown tool category: {category} for tool: {tool_name}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _handle_blender_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a Blender tool call.
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments for the tool execution
            
        Returns:
            Result of the tool execution
        """
        # Check if Blender is connected
        if not self.blender_connection.is_connected:
            try:
                self.blender_connection.connect()
            except Exception as e:
                error_msg = f"Failed to connect to Blender: {str(e)}"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg}
        
        # Route to the appropriate Blender method based on tool name
        try:
            if tool_name == "mcp_blender_get_scene_info":
                result = self.blender_connection.get_scene_info()
            elif tool_name == "mcp_blender_get_object_info":
                result = self.blender_connection.get_object_info(args["object_name"])
            elif tool_name == "mcp_blender_create_primitive":
                # Extract required and optional parameters
                obj_type = args["type"]
                location = args.get("location")
                rotation = args.get("rotation")
                scale = args.get("scale")
                name = args.get("name")
                color = args.get("color")
                
                # Create the object
                result = self.blender_connection.create_object(
                    type=obj_type,
                    name=name,
                    location=location,
                    rotation=rotation,
                    scale=scale
                )
                
                # Apply color if provided
                if color and result.get("status") == "success" and name:
                    self.blender_connection.execute_command("set_material", {
                        "object_name": name,
                        "color": color
                    })
            elif tool_name == "mcp_blender_create_material":
                result = self.blender_connection.execute_command("create_material", args)
            elif tool_name == "mcp_blender_assign_material":
                result = self.blender_connection.execute_command("assign_material", args)
            elif tool_name == "mcp_blender_transform_object":
                result = self.blender_connection.execute_command("transform_object", args)
            elif tool_name == "mcp_blender_export_model":
                result = self.blender_connection.execute_command("export_model", args)
            elif tool_name == "mcp_blender_execute_code":
                result = self.blender_connection.execute_code(args["code"])
            else:
                # For any other commands, pass through to the generic execute_command
                command_name = tool_name.replace("mcp_blender_", "")
                result = self.blender_connection.execute_command(command_name, args)
                
            logger.info(f"Blender tool {tool_name} executed with result: {result}")
            return result
        except Exception as e:
            error_msg = f"Error executing Blender tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _handle_unreal_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an Unreal Engine tool call.
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments for the tool execution
            
        Returns:
            Result of the tool execution
        """
        # Check if Unreal Engine is connected
        if not self.unreal_connection.is_connected:
            try:
                self.unreal_connection.connect()
            except Exception as e:
                error_msg = f"Failed to connect to Unreal Engine: {str(e)}"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg}
        
        # Route to the appropriate Unreal method based on tool name
        try:
            if tool_name == "mcp_unreal_get_engine_version":
                result = self.unreal_connection.get_engine_version()
            elif tool_name == "mcp_unreal_create_level":
                result = self.unreal_connection.create_level(args["level_name"])
            elif tool_name == "mcp_unreal_create_actor":
                result = self.unreal_connection.execute_command("create_actor", args)
            elif tool_name == "mcp_unreal_import_asset":
                result = self.unreal_connection.import_asset(
                    args["file_path"],
                    args["destination_path"],
                    args.get("asset_name")
                )
            elif tool_name == "mcp_unreal_create_blueprint":
                result = self.unreal_connection.execute_command("create_blueprint", args)
            elif tool_name == "mcp_unreal_modify_actor":
                result = self.unreal_connection.execute_command("modify_actor", args)
            elif tool_name == "mcp_unreal_set_material":
                result = self.unreal_connection.execute_command("set_material", args)
            elif tool_name == "mcp_unreal_execute_code":
                result = self.unreal_connection.execute_code(args["code"])
            else:
                # For any other commands, pass through to the generic execute_command
                command_name = tool_name.replace("mcp_unreal_", "")
                result = self.unreal_connection.execute_command(command_name, args)
                
            logger.info(f"Unreal tool {tool_name} executed with result: {result}")
            return result
        except Exception as e:
            error_msg = f"Error executing Unreal tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available tools.
        
        Returns:
            List of tool definitions
        """
        return ALL_TOOLS
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool definition or None if not found
        """
        return get_tool_by_name(tool_name) 