"""
Extended Blender Addon for unreal-blender-mcp

This module extends the original BlenderMCPServer from blender-mcp to provide
additional functionality while maintaining compatibility with upstream updates.
"""

import bpy
import os
import importlib.util
from typing import Dict, Any, Optional, List, Tuple
from addon import BlenderMCPServer, register as original_register, unregister as original_unregister

# 파일 상단에 bl_info 딕셔너리 추가
bl_info = {
    "name": "Extended Blender MCP",
    "author": "Wall-E_No.46024",
    "version": (0, 2),
    "blender": (3, 3, 0),
    "location": "View3D > Sidebar > ExtBlenderMCP",
    "description": "Extended version of Blender MCP with additional features",
    "category": "Interface",
}

# 직접 파일 로드하는 방식으로 변경 - 기존 방식은 모두 제거
addon_module = None
BlenderMCPServer = None
original_register = None
original_unregister = None

try:
    # 방법 1: 기존 애드온 찾기
    addon_dirs = [bpy.utils.user_resource('SCRIPTS', path="addons")]
    
    # 추가적인 애드온 폴더 (시스템, 사용자 등)
    for resource_type in ['USER', 'LOCAL', 'SYSTEM']:
        try:
            addon_path = os.path.join(bpy.utils.resource_path(resource_type), "scripts", "addons")
            if os.path.exists(addon_path) and addon_path not in addon_dirs:
                addon_dirs.append(addon_path)
        except:
            pass
    
    # 각 애드온 폴더에서 blender-mcp 찾기
    addon_file_path = None
    for addon_dir in addon_dirs:
        # 1. 설치된 blender-mcp 애드온 찾기
        potential_path = os.path.join(addon_dir, "blender-mcp", "addon.py")
        if os.path.exists(potential_path):
            addon_file_path = potential_path
            print(f"Found addon.py in addon directory: {addon_file_path}")
            break
            
        # 2. 현재 애드온이 있는 폴더에서 addon.py 찾기
        potential_path = os.path.join(addon_dir, "addon.py")
        if os.path.exists(potential_path):
            addon_file_path = potential_path
            print(f"Found addon.py in same directory: {addon_file_path}")
            break
    
    # 3. 현재 파일 위치 기준 상대 경로 시도
    if not addon_file_path:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        potential_paths = [
            os.path.join(current_dir, "addon.py"),  # 같은 디렉토리
            os.path.join(current_dir, "blender-mcp", "addon.py"),  # 하위 디렉토리
            os.path.join(os.path.dirname(current_dir), "blender-mcp", "addon.py"),  # 상위 디렉토리
        ]
        
        for path in potential_paths:
            if os.path.exists(path):
                addon_file_path = path
                print(f"Found addon.py via relative path: {addon_file_path}")
                break
    
    # 모듈 직접 로드
    if addon_file_path and os.path.exists(addon_file_path):
        print(f"Loading addon module from: {addon_file_path}")
        
        # importlib를 사용하여 파일에서 직접 모듈 로드
        spec = importlib.util.spec_from_file_location("addon_direct", addon_file_path)
        addon_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(addon_module)
        
        # 필요한 클래스와 함수 참조
        BlenderMCPServer = addon_module.BlenderMCPServer
        original_register = addon_module.register
        original_unregister = addon_module.unregister
        
        print("Successfully loaded BlenderMCPServer from file")
    else:
        raise ImportError(f"Could not find addon.py in any location. Searched dirs: {addon_dirs}")
        
except Exception as e:
    print(f"ERROR loading addon.py: {str(e)}")
    
    # 오류 발생 시 더미 클래스 생성
    class BlenderMCPServer:
        def __init__(self, host='localhost', port=8400):
            self.host = host
            self.port = port
            print("WARNING: Using dummy BlenderMCPServer")
        
        def start(self):
            print("Dummy server start")
            
        def stop(self):
            print("Dummy server stop")
            
        def get_simple_info(self):
            return {"error": "Original module not loaded"}
    
    def original_register():
        print("Original register not available")
        
    def original_unregister():
        print("Original unregister not available")

# 나머지 클래스와 함수는 그대로 유지
class ExtendedBlenderMCPServer(BlenderMCPServer):
    """
    Extended version of BlenderMCPServer with additional functionality.
    """
    
    def __init__(self, host='localhost', port=8400):
        super().__init__(host=host, port=port)
        self.running = False
        self.socket = None
        self.server_thread = None
        print("Extended BlenderMCPServer initialized")
    
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
        
        # Stop any existing server first
        if hasattr(bpy.types, "blendermcp_server") and bpy.types.blendermcp_server:
            bpy.types.blendermcp_server.stop()
            del bpy.types.blendermcp_server
            
        if hasattr(bpy.types, "extended_blendermcp_server") and bpy.types.extended_blendermcp_server:
            bpy.types.extended_blendermcp_server.stop()
            del bpy.types.extended_blendermcp_server
        
        # Create and start new server instance
        bpy.types.extended_blendermcp_server = ExtendedBlenderMCPServer(port=scene.extended_blendermcp_port)
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
        default=8400,
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


# 파일 하단에 표준 register 및 unregister 함수 추가
def register():
    # 원본 애드온 등록 (선택적)
    original_register()
    # 확장 기능 등록
    register_extended()

def unregister():
    # 확장 기능 등록 해제
    unregister_extended()
    # 원본 애드온 등록 해제 (선택적)
    original_unregister()

if __name__ == "__main__":
    register() 