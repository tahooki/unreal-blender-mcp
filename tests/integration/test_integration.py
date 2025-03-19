"""
Integration tests for unreal-blender-mcp system.
"""

import os
import sys
import json
import asyncio
import unittest
import tempfile
from typing import Dict, Any, List, Tuple

from tests.integration.test_config import (
    get_test_script_path,
    TEST_SCENARIOS
)
from tests.integration.connections import (
    ping_blender,
    ping_unreal,
    ping_mcp,
    execute_script_file,
    execute_cross_platform_workflow,
    send_mcp_message,
    ConnectionError
)

class IntegrationTests(unittest.TestCase):
    """Integration tests for the unreal-blender-mcp system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Ensure all components are running
        try:
            asyncio.run(cls.check_services())
        except ConnectionError as e:
            print(f"Service check failed: {e}")
            print("Please ensure all components (MCP, Blender, Unreal) are running")
            sys.exit(1)
    
    @classmethod
    async def check_services(cls):
        """Check if all required services are running."""
        tasks = [
            ping_blender(),
            ping_unreal(),
            ping_mcp()
        ]
        
        blender_alive, unreal_alive, mcp_alive = await asyncio.gather(*tasks)
        
        if not blender_alive:
            raise ConnectionError("Blender server is not running")
        
        if not unreal_alive:
            raise ConnectionError("Unreal Engine server is not running")
        
        if not mcp_alive:
            raise ConnectionError("MCP server is not running")
    
    def test_blender_connection(self):
        """Test connection to Blender."""
        result = asyncio.run(ping_blender())
        self.assertTrue(result, "Failed to connect to Blender")
    
    def test_unreal_connection(self):
        """Test connection to Unreal Engine."""
        result = asyncio.run(ping_unreal())
        self.assertTrue(result, "Failed to connect to Unreal Engine")
    
    def test_mcp_connection(self):
        """Test connection to MCP server."""
        result = asyncio.run(ping_mcp())
        self.assertTrue(result, "Failed to connect to MCP server")
    
    def test_blender_create_cube(self):
        """Test creating a cube in Blender."""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_data', 'create_cube.py')
        result = asyncio.run(execute_script_file(script_path, 'blender'))
        self.assertEqual(result.get('status'), 'success', f"Failed to create cube: {result.get('message')}")
        self.assertEqual(result.get('object_name'), 'TestCube')
    
    def test_blender_create_material(self):
        """Test creating a material in Blender."""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_data', 'create_material.py')
        result = asyncio.run(execute_script_file(script_path, 'blender'))
        self.assertEqual(result.get('status'), 'success', f"Failed to create material: {result.get('message')}")
        self.assertEqual(result.get('material_name'), 'TestMaterial')
    
    def test_unreal_create_actor(self):
        """Test creating an actor in Unreal Engine."""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_data', 'create_actor.py')
        result = asyncio.run(execute_script_file(script_path, 'unreal'))
        self.assertEqual(result.get('status'), 'success', f"Failed to create actor: {result.get('message')}")
        self.assertEqual(result.get('actor_label'), 'TestCube')
    
    def test_unreal_create_blueprint(self):
        """Test creating a blueprint in Unreal Engine."""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_data', 'create_blueprint.py')
        result = asyncio.run(execute_script_file(script_path, 'unreal'))
        self.assertEqual(result.get('status'), 'success', f"Failed to create blueprint: {result.get('message')}")
        self.assertEqual(result.get('blueprint_name'), 'TestBlueprint')
    
    def test_cross_platform_workflow(self):
        """Test cross-platform workflow (export from Blender, import to Unreal)."""
        blender_script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'test_data', 
            'export_from_blender.py'
        )
        unreal_script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'test_data', 
            'import_to_unreal.py'
        )
        
        result = asyncio.run(execute_cross_platform_workflow(blender_script_path, unreal_script_path))
        self.assertEqual(result.get('status'), 'success', f"Cross-platform workflow failed: {result.get('message')}")
        self.assertEqual(result.get('blender_result', {}).get('object_name'), 'ExportSphere')
        self.assertEqual(result.get('unreal_result', {}).get('asset_name'), 'ImportedSphere')
    
    def test_mcp_blender_tool_execution(self):
        """Test executing a Blender tool through the MCP server."""
        message = {
            "type": "tool_call",
            "tool": "mcp_blender_create_primitive",
            "args": {
                "type": "CUBE",
                "location": [0, 0, 0],
                "color": [1, 0, 0]
            }
        }
        
        result = asyncio.run(send_mcp_message(message))
        self.assertEqual(result.get('status'), 'success', f"MCP Blender tool execution failed: {result.get('message')}")
    
    def test_mcp_unreal_tool_execution(self):
        """Test executing an Unreal tool through the MCP server."""
        message = {
            "type": "tool_call",
            "tool": "mcp_unreal_execute_code",
            "args": {
                "code": """
import unreal
actor_location = unreal.Vector(0, 0, 0)
actor_rotation = unreal.Rotator(0, 0, 0)
cube = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.StaticMeshActor, 
    actor_location, 
    actor_rotation
)
print(f"Created actor: {cube.get_name()}")
"""
            }
        }
        
        result = asyncio.run(send_mcp_message(message))
        self.assertEqual(result.get('status'), 'success', f"MCP Unreal tool execution failed: {result.get('message')}")

if __name__ == '__main__':
    unittest.main() 