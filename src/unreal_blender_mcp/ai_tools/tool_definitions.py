"""
Tool definitions for AI agents in unreal-blender-mcp.

This module provides comprehensive tool definitions for AI agents to interact
with Blender and Unreal Engine through the MCP server.
"""

from typing import Dict, List, Any, Optional, Union

# Blender tool definitions
BLENDER_TOOLS = [
    {
        "name": "mcp_blender_get_scene_info",
        "description": "Get detailed information about the current Blender scene, including objects, materials, and settings.",
        "category": "blender",
        "parameters": {},
        "example": """
        {
            "tool": "mcp_blender_get_scene_info"
        }
        """,
        "returns": "JSON object with scene information, including object names, counts, and scene statistics."
    },
    {
        "name": "mcp_blender_get_object_info",
        "description": "Get detailed information about a specific object in the Blender scene.",
        "category": "blender",
        "parameters": {
            "object_name": "The name of the object to get information about (required)"
        },
        "example": """
        {
            "tool": "mcp_blender_get_object_info",
            "args": {
                "object_name": "Cube"
            }
        }
        """,
        "returns": "JSON object with object information, including location, rotation, scale, and material data."
    },
    {
        "name": "mcp_blender_create_primitive",
        "description": "Create a basic primitive object in Blender.",
        "category": "blender",
        "parameters": {
            "type": "Object type (CUBE, SPHERE, CYLINDER, PLANE, CONE, TORUS, EMPTY) (required)",
            "name": "Optional name for the object",
            "location": "Optional [x, y, z] location coordinates",
            "rotation": "Optional [x, y, z] rotation in radians",
            "scale": "Optional [x, y, z] scale factors",
            "color": "Optional [R, G, B] color values (0.0-1.0)"
        },
        "example": """
        {
            "tool": "mcp_blender_create_primitive",
            "args": {
                "type": "CUBE",
                "name": "MyCube",
                "location": [0, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1],
                "color": [1.0, 0.0, 0.0]
            }
        }
        """,
        "returns": "JSON object with status, message, and object information if successful."
    },
    {
        "name": "mcp_blender_create_material",
        "description": "Create a new material in Blender with specified properties.",
        "category": "blender",
        "parameters": {
            "name": "Name for the material (required)",
            "color": "Base color as [R, G, B] values (0.0-1.0) (required)",
            "metallic": "Optional metallic value (0.0-1.0)",
            "roughness": "Optional roughness value (0.0-1.0)",
            "specular": "Optional specular value (0.0-1.0)"
        },
        "example": """
        {
            "tool": "mcp_blender_create_material",
            "args": {
                "name": "RedMaterial",
                "color": [1.0, 0.0, 0.0],
                "metallic": 0.0,
                "roughness": 0.5,
                "specular": 0.5
            }
        }
        """,
        "returns": "JSON object with status, message, and material information if successful."
    },
    {
        "name": "mcp_blender_assign_material",
        "description": "Assign a material to an object in Blender.",
        "category": "blender",
        "parameters": {
            "object_name": "Name of the object to assign the material to (required)",
            "material_name": "Name of the material to assign (required)"
        },
        "example": """
        {
            "tool": "mcp_blender_assign_material",
            "args": {
                "object_name": "Cube",
                "material_name": "RedMaterial"
            }
        }
        """,
        "returns": "JSON object with status and message."
    },
    {
        "name": "mcp_blender_transform_object",
        "description": "Transform an object in Blender by modifying its location, rotation, or scale.",
        "category": "blender",
        "parameters": {
            "object_name": "Name of the object to transform (required)",
            "location": "Optional [x, y, z] location coordinates",
            "rotation": "Optional [x, y, z] rotation in radians",
            "scale": "Optional [x, y, z] scale factors"
        },
        "example": """
        {
            "tool": "mcp_blender_transform_object",
            "args": {
                "object_name": "Cube",
                "location": [1, 2, 3],
                "rotation": [0, 0, 0],
                "scale": [2, 2, 2]
            }
        }
        """,
        "returns": "JSON object with status, message, and updated transform information."
    },
    {
        "name": "mcp_blender_export_model",
        "description": "Export a model from Blender to a file.",
        "category": "blender",
        "parameters": {
            "object_name": "Name of the object to export (required)",
            "file_path": "Path where the file should be saved (required)",
            "format": "Export format (FBX, OBJ, GLTF, etc.) (required)"
        },
        "example": """
        {
            "tool": "mcp_blender_export_model",
            "args": {
                "object_name": "Cube",
                "file_path": "/tmp/exported_cube.fbx",
                "format": "FBX"
            }
        }
        """,
        "returns": "JSON object with status, message, and file path."
    },
    {
        "name": "mcp_blender_execute_code",
        "description": "Execute arbitrary Python code in Blender. Use with caution and only when specific tool functions are not available.",
        "category": "blender",
        "parameters": {
            "code": "Python code to execute in Blender (required)"
        },
        "example": """
        {
            "tool": "mcp_blender_execute_code",
            "args": {
                "code": "import bpy\\nbpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))\\nprint('Cube created')"
            }
        }
        """,
        "returns": "JSON object with status, message, and execution result."
    }
]

# Unreal Engine tool definitions
UNREAL_TOOLS = [
    {
        "name": "mcp_unreal_get_engine_version",
        "description": "Get the version of Unreal Engine that is currently running.",
        "category": "unreal",
        "parameters": {},
        "example": """
        {
            "tool": "mcp_unreal_get_engine_version"
        }
        """,
        "returns": "JSON object with status, message, and engine version."
    },
    {
        "name": "mcp_unreal_create_level",
        "description": "Create a new level in Unreal Engine.",
        "category": "unreal",
        "parameters": {
            "level_name": "Name of the level to create (required)"
        },
        "example": """
        {
            "tool": "mcp_unreal_create_level",
            "args": {
                "level_name": "MyNewLevel"
            }
        }
        """,
        "returns": "JSON object with status and message."
    },
    {
        "name": "mcp_unreal_create_actor",
        "description": "Create a new actor in the current Unreal Engine level.",
        "category": "unreal",
        "parameters": {
            "actor_class": "Class of actor to create (e.g., StaticMeshActor) (required)",
            "location": "Optional [x, y, z] location coordinates",
            "rotation": "Optional [pitch, yaw, roll] rotation in degrees",
            "scale": "Optional [x, y, z] scale factors",
            "name": "Optional name for the actor"
        },
        "example": """
        {
            "tool": "mcp_unreal_create_actor",
            "args": {
                "actor_class": "StaticMeshActor",
                "location": [0, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1],
                "name": "MyCube"
            }
        }
        """,
        "returns": "JSON object with status, message, and actor information if successful."
    },
    {
        "name": "mcp_unreal_import_asset",
        "description": "Import an asset (model, texture, etc.) into Unreal Engine.",
        "category": "unreal",
        "parameters": {
            "file_path": "Path to the file to import (required)",
            "destination_path": "Content browser path where the asset should be imported (required)",
            "asset_name": "Optional name for the imported asset"
        },
        "example": """
        {
            "tool": "mcp_unreal_import_asset",
            "args": {
                "file_path": "/tmp/exported_cube.fbx",
                "destination_path": "/Game/Models",
                "asset_name": "ImportedCube"
            }
        }
        """,
        "returns": "JSON object with status, message, and asset information if successful."
    },
    {
        "name": "mcp_unreal_create_blueprint",
        "description": "Create a new Blueprint class in Unreal Engine.",
        "category": "unreal",
        "parameters": {
            "name": "Name for the blueprint (required)",
            "parent_class": "Parent class for the blueprint (required)",
            "save_path": "Content browser path where the blueprint should be saved (required)"
        },
        "example": """
        {
            "tool": "mcp_unreal_create_blueprint",
            "args": {
                "name": "MyActor",
                "parent_class": "Actor",
                "save_path": "/Game/Blueprints"
            }
        }
        """,
        "returns": "JSON object with status, message, and blueprint information if successful."
    },
    {
        "name": "mcp_unreal_modify_actor",
        "description": "Modify an existing actor in the current Unreal Engine level.",
        "category": "unreal",
        "parameters": {
            "actor_name": "Name of the actor to modify (required)",
            "location": "Optional [x, y, z] location coordinates",
            "rotation": "Optional [pitch, yaw, roll] rotation in degrees",
            "scale": "Optional [x, y, z] scale factors",
            "visible": "Optional boolean to set visibility"
        },
        "example": """
        {
            "tool": "mcp_unreal_modify_actor",
            "args": {
                "actor_name": "MyCube",
                "location": [10, 0, 0],
                "rotation": [0, 45, 0],
                "scale": [2, 2, 2],
                "visible": true
            }
        }
        """,
        "returns": "JSON object with status, message, and updated actor information."
    },
    {
        "name": "mcp_unreal_set_material",
        "description": "Set or create a material for an object in Unreal Engine.",
        "category": "unreal",
        "parameters": {
            "actor_name": "Name of the actor to apply the material to (required)",
            "material_path": "Content browser path to an existing material, or path to create a new material",
            "color": "Optional [R, G, B] color values (0.0-1.0)"
        },
        "example": """
        {
            "tool": "mcp_unreal_set_material",
            "args": {
                "actor_name": "MyCube",
                "material_path": "/Game/Materials/M_Red",
                "color": [1.0, 0.0, 0.0]
            }
        }
        """,
        "returns": "JSON object with status, message, and material information."
    },
    {
        "name": "mcp_unreal_execute_code",
        "description": "Execute arbitrary Python code in Unreal Engine. Use with caution and only when specific tool functions are not available.",
        "category": "unreal",
        "parameters": {
            "code": "Python code to execute in Unreal Engine (required)"
        },
        "example": """
        {
            "tool": "mcp_unreal_execute_code",
            "args": {
                "code": "import unreal\\nactor_location = unreal.Vector(0, 0, 0)\\nactor_rotation = unreal.Rotator(0, 0, 0)\\ncube = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, actor_location, actor_rotation)\\nprint(f'Created actor: {cube.get_name()}')"
            }
        }
        """,
        "returns": "JSON object with status, message, and execution result."
    }
]

# Combined tool definitions
ALL_TOOLS = BLENDER_TOOLS + UNREAL_TOOLS

def get_tool_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Get a tool definition by name.
    
    Args:
        name: The name of the tool
        
    Returns:
        The tool definition or None if not found
    """
    for tool in ALL_TOOLS:
        if tool["name"] == name:
            return tool
    return None

def get_tools_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Get all tool definitions in a category.
    
    Args:
        category: The category to filter by ('blender' or 'unreal')
        
    Returns:
        List of tool definitions in the specified category
    """
    return [tool for tool in ALL_TOOLS if tool["category"] == category]

def format_tool_for_prompt(tool: Dict[str, Any]) -> str:
    """
    Format a tool definition for inclusion in a prompt.
    
    Args:
        tool: The tool definition
        
    Returns:
        Formatted string describing the tool
    """
    result = f"Tool: {tool['name']}\n"
    result += f"Description: {tool['description']}\n"
    
    if tool["parameters"]:
        result += "Parameters:\n"
        for param_name, param_desc in tool["parameters"].items():
            result += f"  - {param_name}: {param_desc}\n"
    else:
        result += "Parameters: None\n"
        
    result += f"Example: {tool['example']}\n"
    
    return result

def get_formatted_tools_for_prompt(category: Optional[str] = None) -> str:
    """
    Get formatted tool definitions for inclusion in a prompt.
    
    Args:
        category: Optional category to filter by ('blender' or 'unreal')
        
    Returns:
        Formatted string describing the tools
    """
    tools = ALL_TOOLS
    if category:
        tools = get_tools_by_category(category)
        
    return "\n".join([format_tool_for_prompt(tool) for tool in tools]) 