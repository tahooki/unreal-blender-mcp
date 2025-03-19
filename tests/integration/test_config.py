"""
Configuration settings for integration tests.
"""

import os
from typing import Dict, Any

# MCP Server settings
MCP_SERVER_HOST = "localhost"
MCP_SERVER_PORT = 8000

# Blender connection settings
BLENDER_HOST = "localhost"
BLENDER_PORT = 8400

# Unreal Engine connection settings
UNREAL_HOST = "localhost"
UNREAL_PORT = 8500

# Test data paths
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data")

# Sample Python scripts
SAMPLE_BLENDER_SCRIPT = """
import bpy
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
print("Cube created successfully")
return {"status": "success", "message": "Cube created"}
"""

SAMPLE_UNREAL_SCRIPT = """
import unreal
actor_location = unreal.Vector(0, 0, 0)
actor_rotation = unreal.Rotator(0, 0, 0)
cube = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.StaticMeshActor, 
    actor_location, 
    actor_rotation
)
print(f"Created actor: {cube.get_name()}")
return f"Created actor: {cube.get_name()}"
"""

# Test scenario configurations
TEST_SCENARIOS = {
    "blender_basic": {
        "description": "Basic Blender operations through MCP",
        "scripts": ["create_cube.py", "create_material.py"]
    },
    "unreal_basic": {
        "description": "Basic Unreal operations through MCP",
        "scripts": ["create_actor.py", "create_blueprint.py"]
    },
    "cross_platform": {
        "description": "Operations that involve both Blender and Unreal",
        "scripts": ["export_from_blender.py", "import_to_unreal.py"]
    }
}

def get_test_script_path(script_name: str) -> str:
    """Get the full path to a test script."""
    return os.path.join(TEST_DATA_DIR, script_name)

def get_mcp_server_url() -> str:
    """Get the URL for the MCP server."""
    return f"http://{MCP_SERVER_HOST}:{MCP_SERVER_PORT}"

def get_blender_server_url() -> str:
    """Get the URL for the Blender server."""
    return f"http://{BLENDER_HOST}:{BLENDER_PORT}"

def get_unreal_server_url() -> str:
    """Get the URL for the Unreal server."""
    return f"http://{UNREAL_HOST}:{UNREAL_PORT}" 