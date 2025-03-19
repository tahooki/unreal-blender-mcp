"""
Extended Blender Addon for unreal-blender-mcp

This module extends the original BlenderMCPServer from blender-mcp to provide
additional functionality while maintaining compatibility with upstream updates.
"""

import bpy
import sys
import os
import importlib.util
from typing import Dict, Any, Optional, List, Tuple

# Get the path to the original blender-mcp addon
BLENDER_MCP_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'blender-mcp'))

# Add the blender-mcp directory to the Python path
if BLENDER_MCP_PATH not in sys.path:
    sys.path.append(BLENDER_MCP_PATH)

# Import the original BlenderMCPServer
try:
    # First try to import directly if the module is already in sys.path
    from addon import BlenderMCPServer, BlenderMCPHTTPHandler
    from addon import register as original_register
    from addon import unregister as original_unregister
except ImportError:
    # If direct import fails, use importlib to load from the absolute path
    spec = importlib.util.spec_from_file_location("addon", os.path.join(BLENDER_MCP_PATH, "addon.py"))
    addon_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(addon_module)
    BlenderMCPServer = addon_module.BlenderMCPServer
    BlenderMCPHTTPHandler = addon_module.BlenderMCPHTTPHandler
    original_register = addon_module.register
    original_unregister = addon_module.unregister


class ExtendedBlenderMCPServer(BlenderMCPServer):
    """
    Extended version of BlenderMCPServer with additional functionality.
    This class inherits from the original BlenderMCPServer and adds or overrides
    methods as needed.
    """
    
    def __init__(self, host='localhost', port=8400):
        # Call the parent class's __init__ method
        super().__init__(host=host, port=port)
        self.log_info("Extended BlenderMCPServer initialized")
    
    def _execute_command_internal(self, command):
        """Override the internal command execution to add custom commands"""
        cmd_type = command.get("type")
        params = command.get("params", {})
        
        # Check for extended commands first
        if cmd_type == "extended_command_example":
            return {"status": "success", "result": self.extended_command_example(**params)}
            
        # If not an extended command, call the parent class's method
        return super()._execute_command_internal(command)
    
    def extended_command_example(self, **params):
        """An example of an extended command"""
        self.log_info("Extended command example executed")
        return {
            "message": "This is an extended command",
            "params_received": params
        }

    # Add any additional methods or override existing ones as needed
    def get_version_info(self):
        """Get version information for this extended server"""
        original_info = self.get_simple_info()
        extended_info = {
            "extended_version": "1.0.0",
            "original_server": original_info
        }
        return extended_info


# Extended UI Panel for the extended server
class EXTENDED_BLENDERMCP_PT_Panel(bpy.types.Panel):
    bl_label = "Extended BlenderMCP"
    bl_idname = "EXTENDED_BLENDERMCP_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ExtBlenderMCP'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Server configuration section
        box = layout.box()
        box.label(text="Extended Server Configuration:", icon='SETTINGS')
        box.prop(scene, "extended_blendermcp_port")
        
        # Display connection status
        status_box = layout.box()
        if not scene.extended_blendermcp_server_running:
            status_row = status_box.row()
            status_row.label(text="Status: Not Running", icon='X')
            status_box.operator("extended_blendermcp.start_server", text="Start Extended Server", icon='PLAY')
        else:
            status_row = status_box.row()
            status_row.label(text=f"Status: Running on port {scene.extended_blendermcp_port}", icon='CHECKMARK')
            status_box.label(text=f"URL: http://localhost:{scene.extended_blendermcp_port}")
            status_box.operator("extended_blendermcp.stop_server", text="Stop Extended Server", icon='PAUSE')
        
        # Extended features section
        feature_box = layout.box()
        feature_box.label(text="Extended Features:", icon='TOOL_SETTINGS')
        feature_box.prop(scene, "extended_blendermcp_feature_1", text="Extended Feature 1")
        feature_box.prop(scene, "extended_blendermcp_feature_2", text="Extended Feature 2")
        
        # Link to logs panel
        layout.separator()
        logs_row = layout.row()
        logs_row.operator("extended_blendermcp.view_logs", text="View Extended Server Logs", icon='TEXT')


# Extended Start Server Operator
class EXTENDED_BLENDERMCP_OT_StartServer(bpy.types.Operator):
    bl_idname = "extended_blendermcp.start_server"
    bl_label = "Start Extended MCP Server"
    bl_description = "Start the Extended BlenderMCP server"
    
    def execute(self, context):
        scene = context.scene
        
        # Create a new server instance of the extended type
        if not hasattr(bpy.types, "extended_blendermcp_server") or not bpy.types.extended_blendermcp_server:
            bpy.types.extended_blendermcp_server = ExtendedBlenderMCPServer(port=scene.extended_blendermcp_port)
        
        # Start the server
        bpy.types.extended_blendermcp_server.start()
        scene.extended_blendermcp_server_running = True
        
        self.report({'INFO'}, f"Started Extended MCP server on port {scene.extended_blendermcp_port}")
        return {'FINISHED'}


# Extended Stop Server Operator
class EXTENDED_BLENDERMCP_OT_StopServer(bpy.types.Operator):
    bl_idname = "extended_blendermcp.stop_server"
    bl_label = "Stop Extended MCP Server"
    bl_description = "Stop the Extended MCP server"
    
    def execute(self, context):
        scene = context.scene
        
        # Stop the server if it exists
        if hasattr(bpy.types, "extended_blendermcp_server") and bpy.types.extended_blendermcp_server:
            bpy.types.extended_blendermcp_server.stop()
            del bpy.types.extended_blendermcp_server
        
        scene.extended_blendermcp_server_running = False
        
        return {'FINISHED'}


# Extended View Logs Operator
class EXTENDED_BLENDERMCP_OT_ViewLogs(bpy.types.Operator):
    bl_idname = "extended_blendermcp.view_logs"
    bl_label = "View Extended Logs"
    bl_description = "Open the logs panel to view extended server logs"
    
    def execute(self, context):
        self.report({'INFO'}, "Check the Extended Logs panel in the ExtBlenderMCP tab")
        
        # Trigger a redraw
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        return {'FINISHED'}


# Registration functions for the extended addon
def register_extended():
    # Register properties
    bpy.types.Scene.extended_blendermcp_port = bpy.props.IntProperty(
        name="Extended Port",
        description="Port for the Extended BlenderMCP server",
        default=8401,  # Different from the original to avoid conflicts
        min=1024,
        max=65535
    )
    
    bpy.types.Scene.extended_blendermcp_server_running = bpy.props.BoolProperty(
        name="Extended Server Running",
        default=False
    )
    
    bpy.types.Scene.extended_blendermcp_feature_1 = bpy.props.BoolProperty(
        name="Extended Feature 1",
        description="Enable extended feature 1",
        default=False
    )
    
    bpy.types.Scene.extended_blendermcp_feature_2 = bpy.props.BoolProperty(
        name="Extended Feature 2",
        description="Enable extended feature 2",
        default=False
    )
    
    # Register UI classes
    bpy.utils.register_class(EXTENDED_BLENDERMCP_PT_Panel)
    bpy.utils.register_class(EXTENDED_BLENDERMCP_OT_StartServer)
    bpy.utils.register_class(EXTENDED_BLENDERMCP_OT_StopServer)
    bpy.utils.register_class(EXTENDED_BLENDERMCP_OT_ViewLogs)
    
    print("Extended BlenderMCP addon registered")


def unregister_extended():
    # Stop the server if it's running
    if hasattr(bpy.types, "extended_blendermcp_server") and bpy.types.extended_blendermcp_server:
        bpy.types.extended_blendermcp_server.stop()
        del bpy.types.extended_blendermcp_server
    
    # Unregister UI classes
    bpy.utils.unregister_class(EXTENDED_BLENDERMCP_PT_Panel)
    bpy.utils.unregister_class(EXTENDED_BLENDERMCP_OT_StartServer)
    bpy.utils.unregister_class(EXTENDED_BLENDERMCP_OT_StopServer)
    bpy.utils.unregister_class(EXTENDED_BLENDERMCP_OT_ViewLogs)
    
    # Delete properties
    del bpy.types.Scene.extended_blendermcp_port
    del bpy.types.Scene.extended_blendermcp_server_running
    del bpy.types.Scene.extended_blendermcp_feature_1
    del bpy.types.Scene.extended_blendermcp_feature_2
    
    print("Extended BlenderMCP addon unregistered")


# Can be run directly in Blender for testing
if __name__ == "__main__":
    register_extended() 