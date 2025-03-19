"""
Prompt engineering for AI agents.

This module provides system prompts and examples for AI agents to interact with
Blender and Unreal Engine through the unreal-blender-mcp server.
"""

from typing import List, Dict, Any, Optional
from .tool_definitions import (
    get_formatted_tools_for_prompt,
    get_tools_by_category,
    ALL_TOOLS
)

def get_claude_system_prompt(include_blender: bool = True, include_unreal: bool = True) -> str:
    """
    Get a system prompt for Claude to use the unreal-blender-mcp tools.
    
    Args:
        include_blender: Whether to include Blender tools
        include_unreal: Whether to include Unreal Engine tools
        
    Returns:
        System prompt for Claude
    """
    prompt = """
You are Claude, an AI assistant with the ability to control Blender and Unreal Engine through specialized tools.
Your goal is to help users create and modify 3D content by translating their requests into the appropriate tool calls.

When a user asks you to perform an action in Blender or Unreal Engine, you should use the appropriate tool function from the list below.
Always provide clear explanations of what you're doing, but keep your responses concise and focused on the task at hand.
"""

    # Add tool sections based on parameters
    if include_blender:
        prompt += "\n\n## Blender Tools\n\nThese tools allow you to interact with Blender:\n\n"
        prompt += get_formatted_tools_for_prompt("blender")
        
    if include_unreal:
        prompt += "\n\n## Unreal Engine Tools\n\nThese tools allow you to interact with Unreal Engine:\n\n"
        prompt += get_formatted_tools_for_prompt("unreal")
    
    # Add general guidelines
    prompt += """
## Guidelines for Using Tools

1. **Choosing the Right Tool**: Select the most specific tool for the task. Only use the execute_code tools when no specific tool exists.

2. **Parameter Formatting**:
   - Location, rotation, and scale should be provided as arrays: [x, y, z]
   - Colors should be provided as RGB arrays with values between 0 and 1: [r, g, b]
   - Required parameters must always be included

3. **Error Handling**:
   - If a tool call fails, check the error message and try to fix the issue
   - Verify object names exist before trying to modify them
   - If connection issues occur, suggest the user check if Blender/Unreal is running

4. **Common Workflows**:
   - For creating and positioning objects, first create the object, then transform it
   - For material assignment, first create a material, then assign it to an object
   - For exporting to Unreal, export from Blender, then import to Unreal

Remember to be helpful, accurate, and to guide the user through complex workflows when needed.
"""
    
    return prompt.strip()

def get_chatgpt_system_prompt(include_blender: bool = True, include_unreal: bool = True) -> str:
    """
    Get a system prompt for ChatGPT to use the unreal-blender-mcp tools.
    
    Args:
        include_blender: Whether to include Blender tools
        include_unreal: Whether to include Unreal Engine tools
        
    Returns:
        System prompt for ChatGPT
    """
    prompt = """
You are an AI assistant with the ability to control Blender and Unreal Engine through specialized function calls.
Your goal is to help users create and modify 3D content by translating their requests into the appropriate function calls.

When a user asks you to perform an action in Blender or Unreal Engine, you should use the appropriate function from the list below.
Always provide clear explanations of what you're doing, but keep your responses concise and focused on the task at hand.

The following functions are available to you:
"""

    # Add tool sections based on parameters
    if include_blender:
        blender_tools = get_tools_by_category("blender")
        for tool in blender_tools:
            prompt += f"\n{tool['name']}:"
            prompt += f"\n  Description: {tool['description']}"
            if tool['parameters']:
                prompt += "\n  Parameters:"
                for param_name, param_desc in tool['parameters'].items():
                    prompt += f"\n    - {param_name}: {param_desc}"
            prompt += "\n"
        
    if include_unreal:
        unreal_tools = get_tools_by_category("unreal")
        for tool in unreal_tools:
            prompt += f"\n{tool['name']}:"
            prompt += f"\n  Description: {tool['description']}"
            if tool['parameters']:
                prompt += "\n  Parameters:"
                for param_name, param_desc in tool['parameters'].items():
                    prompt += f"\n    - {param_name}: {param_desc}"
            prompt += "\n"
    
    # Add general guidelines
    prompt += """
## Guidelines for Using Functions

1. **Choosing the Right Function**: Select the most specific function for the task. Only use the execute_code functions when no specific function exists.

2. **Parameter Formatting**:
   - Location, rotation, and scale should be provided as arrays: [x, y, z]
   - Colors should be provided as RGB arrays with values between 0 and 1: [r, g, b]
   - Required parameters must always be included

3. **Error Handling**:
   - If a function call fails, check the error message and try to fix the issue
   - Verify object names exist before trying to modify them
   - If connection issues occur, suggest the user check if Blender/Unreal is running

4. **Common Workflows**:
   - For creating and positioning objects, first create the object, then transform it
   - For material assignment, first create a material, then assign it to an object
   - For exporting to Unreal, export from Blender, then import to Unreal

Remember to be helpful, accurate, and to guide the user through complex workflows when needed.
"""
    
    return prompt.strip()

def get_cursor_system_prompt(include_blender: bool = True, include_unreal: bool = True) -> str:
    """
    Get a system prompt for Cursor to use the unreal-blender-mcp tools.
    
    Args:
        include_blender: Whether to include Blender tools
        include_unreal: Whether to include Unreal Engine tools
        
    Returns:
        System prompt for Cursor
    """
    # Cursor uses a format similar to Claude
    return get_claude_system_prompt(include_blender, include_unreal)

def get_example_conversations() -> List[Dict[str, Any]]:
    """
    Get example conversations for AI agents to learn from.
    
    Returns:
        List of example conversations
    """
    return [
        {
            "title": "Creating a red cube in Blender",
            "conversation": [
                {"role": "user", "content": "Create a red cube in Blender"},
                {"role": "assistant", "content": "I'll create a red cube in Blender for you."},
                {"role": "assistant", "function_call": {
                    "name": "mcp_blender_create_primitive",
                    "arguments": {
                        "type": "CUBE",
                        "name": "RedCube",
                        "location": [0, 0, 0],
                        "color": [1.0, 0.0, 0.0]
                    }
                }},
                {"role": "function", "name": "mcp_blender_create_primitive", "content": {
                    "status": "success",
                    "message": "Created cube 'RedCube' with red material"
                }},
                {"role": "assistant", "content": "I've created a red cube named 'RedCube' at the center of the scene in Blender. You should now be able to see it in your Blender viewport."}
            ]
        },
        {
            "title": "Creating a level in Unreal with a blueprint",
            "conversation": [
                {"role": "user", "content": "Create a new level in Unreal called TestLevel and add a simple actor blueprint"},
                {"role": "assistant", "content": "I'll create a new level in Unreal Engine called 'TestLevel' and add a simple actor blueprint. Let me do that step by step."},
                {"role": "assistant", "function_call": {
                    "name": "mcp_unreal_create_level",
                    "arguments": {
                        "level_name": "TestLevel"
                    }
                }},
                {"role": "function", "name": "mcp_unreal_create_level", "content": {
                    "status": "success",
                    "message": "Created level 'TestLevel'"
                }},
                {"role": "assistant", "content": "The new level 'TestLevel' has been created. Now I'll create a simple actor blueprint."},
                {"role": "assistant", "function_call": {
                    "name": "mcp_unreal_create_blueprint",
                    "arguments": {
                        "name": "SimpleActor",
                        "parent_class": "Actor",
                        "save_path": "/Game/Blueprints"
                    }
                }},
                {"role": "function", "name": "mcp_unreal_create_blueprint", "content": {
                    "status": "success",
                    "message": "Created blueprint 'SimpleActor' at '/Game/Blueprints'"
                }},
                {"role": "assistant", "content": "I've successfully created a new level called 'TestLevel' and added a simple actor blueprint named 'SimpleActor' in the '/Game/Blueprints' folder. You can now open the level in Unreal Engine and place instances of your new blueprint in the scene."}
            ]
        },
        {
            "title": "Cross-platform workflow: Create in Blender and import to Unreal",
            "conversation": [
                {"role": "user", "content": "I want to create a sphere in Blender, export it as FBX, and import it into Unreal Engine"},
                {"role": "assistant", "content": "I'll help you create a sphere in Blender, export it as an FBX file, and then import it into Unreal Engine. Let's do this step by step."},
                {"role": "assistant", "function_call": {
                    "name": "mcp_blender_create_primitive",
                    "arguments": {
                        "type": "SPHERE",
                        "name": "ExportSphere",
                        "location": [0, 0, 0],
                        "scale": [1, 1, 1]
                    }
                }},
                {"role": "function", "name": "mcp_blender_create_primitive", "content": {
                    "status": "success",
                    "message": "Created sphere 'ExportSphere'"
                }},
                {"role": "assistant", "content": "The sphere has been created in Blender. Now I'll export it as an FBX file."},
                {"role": "assistant", "function_call": {
                    "name": "mcp_blender_export_model",
                    "arguments": {
                        "object_name": "ExportSphere",
                        "file_path": "/tmp/export_sphere.fbx",
                        "format": "FBX"
                    }
                }},
                {"role": "function", "name": "mcp_blender_export_model", "content": {
                    "status": "success",
                    "message": "Exported 'ExportSphere' to '/tmp/export_sphere.fbx'",
                    "file_path": "/tmp/export_sphere.fbx"
                }},
                {"role": "assistant", "content": "The sphere has been exported as an FBX file. Now I'll import it into Unreal Engine."},
                {"role": "assistant", "function_call": {
                    "name": "mcp_unreal_import_asset",
                    "arguments": {
                        "file_path": "/tmp/export_sphere.fbx",
                        "destination_path": "/Game/Models",
                        "asset_name": "ImportedSphere"
                    }
                }},
                {"role": "function", "name": "mcp_unreal_import_asset", "content": {
                    "status": "success",
                    "message": "Imported '/tmp/export_sphere.fbx' to '/Game/Models/ImportedSphere'",
                    "asset_path": "/Game/Models/ImportedSphere"
                }},
                {"role": "assistant", "content": "I've completed all the steps:\n\n1. Created a sphere named 'ExportSphere' in Blender\n2. Exported the sphere as an FBX file to '/tmp/export_sphere.fbx'\n3. Imported the FBX file into Unreal Engine at '/Game/Models/ImportedSphere'\n\nYou can now use this sphere in your Unreal Engine project. Would you like me to place an instance of it in the current level as well?"}
            ]
        }
    ]

def get_error_recovery_prompts() -> Dict[str, str]:
    """
    Get prompts for recovering from common errors.
    
    Returns:
        Dictionary mapping error types to recovery prompts
    """
    return {
        "connection_error": """
It seems there's a connection issue with {platform}. Here are some steps to resolve this:

1. Make sure {platform} is running
2. Check that the {platform} addon/plugin is enabled
3. Verify the connection settings (default ports: Blender 8400, Unreal 8500)
4. Restart {platform} if needed

Would you like me to try connecting again once you've verified these?
        """.strip(),
        
        "invalid_object": """
The object '{object_name}' doesn't seem to exist in {platform}. This could be because:

1. The object hasn't been created yet
2. The object name has a typo
3. The object was deleted or renamed

Would you like me to:
1. List available objects to check what exists
2. Create a new object with this name
3. Try a different name
        """.strip(),
        
        "invalid_parameter": """
There was an issue with the parameter '{param_name}' in the {tool_name} call. The error is:

{error_message}

This usually happens when:
1. The parameter format is incorrect (check arrays, data types)
2. The parameter value is out of the allowed range
3. There's a typo in the parameter name

Let me fix this and try again.
        """.strip(),
        
        "execution_error": """
An error occurred while executing the command in {platform}:

{error_message}

This might be due to:
1. Limitations in {platform}'s current state
2. Conflicts with other operations
3. An internal error in {platform}

Let's try an alternative approach or simplify the operation.
        """.strip()
    } 