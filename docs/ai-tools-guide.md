# Using AI Agents with unreal-blender-mcp

This guide explains how to use AI agents like Claude and ChatGPT to control Blender and Unreal Engine through the unreal-blender-mcp server.

## Overview

The unreal-blender-mcp server provides a set of AI-friendly tool definitions that allow AI agents to control Blender and Unreal Engine. This enables workflows like:

- Creating and manipulating 3D objects in Blender
- Exporting models from Blender and importing them into Unreal Engine
- Creating levels, actors, and blueprints in Unreal Engine
- Executing custom code in both platforms

## Setup Requirements

Before using AI agents with unreal-blender-mcp, ensure you have:

1. The unreal-blender-mcp server running
2. Blender with the MCP addon enabled and running
3. Unreal Engine with the MCP plugin enabled and running
4. Access to an AI agent (Claude, ChatGPT, or Cursor)

## Getting Started

### Starting the Server

Start the unreal-blender-mcp server:

```bash
cd /path/to/unreal-blender-mcp
python -m src.unreal_blender_mcp.server
```

Verify the server is running by accessing http://localhost:8000/ in your browser.

### Setting Up Claude (Anthropic)

Claude can be used either through the Anthropic API or through the Claude web interface.

#### Using Claude with the API

1. Use the system prompt from the server:
   ```
   GET http://localhost:8000/ai/prompts?ai_type=claude
   ```

2. Include this system prompt when making requests to the Claude API
3. Format tool calls according to the Claude API specification

#### Using Claude in the Web Interface

1. Go to https://claude.ai
2. Start a new conversation
3. Paste the system prompt from `http://localhost:8000/ai/prompts?ai_type=claude`
4. Ask Claude to perform actions in Blender or Unreal Engine

### Setting Up ChatGPT (OpenAI)

ChatGPT can be used either through the OpenAI API or through the ChatGPT web interface.

#### Using ChatGPT with the API

1. Use the system prompt from the server:
   ```
   GET http://localhost:8000/ai/prompts?ai_type=chatgpt
   ```

2. Include this system prompt when making requests to the OpenAI API
3. Define the functions using the tools available from `http://localhost:8000/ai/tools`

#### Using ChatGPT in the Web Interface

1. Go to https://chat.openai.com
2. Create a GPT with the system prompt from `http://localhost:8000/ai/prompts?ai_type=chatgpt`
3. Add example conversations from `http://localhost:8000/ai/examples`
4. Ask the GPT to perform actions in Blender or Unreal Engine

### Setting Up Cursor

Cursor can directly use the unreal-blender-mcp tools with minimal configuration:

1. Start Cursor
2. Open the Settings menu and go to the AI section
3. Set up a custom AI service with the tools from `http://localhost:8000/ai/tools`
4. Use the system prompt from `http://localhost:8000/ai/prompts?ai_type=cursor`

## Available Tools

The unreal-blender-mcp server provides tools for both Blender and Unreal Engine:

### Blender Tools

- `mcp_blender_get_scene_info`: Get information about the current Blender scene
- `mcp_blender_get_object_info`: Get information about a specific object
- `mcp_blender_create_primitive`: Create a primitive object (cube, sphere, etc.)
- `mcp_blender_create_material`: Create a new material
- `mcp_blender_assign_material`: Assign a material to an object
- `mcp_blender_transform_object`: Transform an object (move, rotate, scale)
- `mcp_blender_export_model`: Export a model to a file
- `mcp_blender_execute_code`: Execute arbitrary Python code in Blender

### Unreal Engine Tools

- `mcp_unreal_get_engine_version`: Get the Unreal Engine version
- `mcp_unreal_create_level`: Create a new level
- `mcp_unreal_create_actor`: Create a new actor
- `mcp_unreal_import_asset`: Import an asset from a file
- `mcp_unreal_create_blueprint`: Create a new Blueprint class
- `mcp_unreal_modify_actor`: Modify an existing actor
- `mcp_unreal_set_material`: Set or create a material for an object
- `mcp_unreal_execute_code`: Execute arbitrary Python code in Unreal Engine

For detailed information about each tool and its parameters, refer to the API documentation or use:

```
GET http://localhost:8000/ai/tools
```

## Example Workflows

Here are some common workflows that can be performed with AI agents:

### Creating and Exporting a 3D Model

1. Create a primitive object in Blender
2. Modify its transform properties
3. Apply a material
4. Export the model to an FBX file

Example conversation:

```
User: Create a red cube in Blender, move it up by 2 units, and export it as an FBX file.

AI: I'll create a red cube in Blender, move it up, and export it as an FBX file.

[AI uses mcp_blender_create_primitive to create a cube]
[AI uses mcp_blender_transform_object to move it]
[AI uses mcp_blender_export_model to export it]

I've created a red cube, moved it 2 units up, and exported it to "/tmp/cube.fbx".
```

### Creating a Level in Unreal Engine

1. Create a new level in Unreal Engine
2. Import an asset from Blender
3. Create a blueprint for the asset
4. Place the actor in the level

Example conversation:

```
User: Create a new level in Unreal called "TestLevel" and import the cube we just created.

AI: I'll create a new level and import the cube.

[AI uses mcp_unreal_create_level to create a level]
[AI uses mcp_unreal_import_asset to import the cube]
[AI uses mcp_unreal_create_actor to place it in the level]

I've created a new level called "TestLevel" and imported the cube from "/tmp/cube.fbx".
The cube has been placed at the center of the level.
```

## Troubleshooting

### Connection Issues

If the AI agent reports connection errors:

1. Ensure the unreal-blender-mcp server is running
2. Check that Blender and Unreal Engine are running
3. Verify the respective addons/plugins are enabled
4. Check the server logs for any error messages

### Tool Call Errors

If a tool call fails:

1. Check the parameters being sent to the tool
2. Ensure required parameters are provided
3. Verify that the values are in the correct format
4. Look for typos in object names or paths

### AI Understanding Issues

If the AI agent doesn't understand how to use the tools:

1. Make sure you're using the correct system prompt
2. Provide clear and specific instructions
3. Use example conversations to guide the AI
4. Break complex tasks into smaller steps

## Advanced Usage

### Custom Tool Development

You can extend the unreal-blender-mcp server with custom tools:

1. Add new tool definitions in `src/unreal_blender_mcp/ai_tools/tool_definitions.py`
2. Implement the tool handlers in `src/unreal_blender_mcp/ai_tools/tool_handler.py`
3. Update the system prompts in `src/unreal_blender_mcp/ai_tools/prompt_engineering.py`

### Integration with Other AI Platforms

The unreal-blender-mcp server can be integrated with other AI platforms:

1. Use the API endpoints to get tool definitions and system prompts
2. Format the tools according to the platform's specifications
3. Implement the necessary communication layer between the AI platform and the server

## Resources

- [unreal-blender-mcp GitHub Repository](https://github.com/yourusername/unreal-blender-mcp)
- [Blender Python API Documentation](https://docs.blender.org/api/current/index.html)
- [Unreal Engine Python API Documentation](https://docs.unrealengine.com/5.0/en-US/PythonAPI/)
- [Claude Documentation](https://docs.anthropic.com/claude/docs)
- [ChatGPT API Documentation](https://platform.openai.com/docs/api-reference)
- [Cursor Documentation](https://cursor.sh/docs) 