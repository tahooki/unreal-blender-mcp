# Extended BlenderMCP Server

This module extends the functionality of the original `blender-mcp` server while maintaining compatibility with upstream updates. It follows a pattern similar to class inheritance, where the original server code is used as a base, and additional functionality is added on top.

## Structure

- `__init__.py` - Package definition with imports
- `extended_server.py` - Main extension that builds on the original server
- `interface.py` - Utilities for managing and running the extended server

## How It Works

The extension pattern works as follows:

1. The original BlenderMCP server code is imported from `blender-mcp/src/blender_mcp/server.py`
2. New tools and functionality are added using the original server's `mcp` instance
3. A custom `ExtendedBlenderConnection` class enhances the connection to Blender
4. The `ExtendedBlenderMCPServer` class provides a wrapper around the original FastMCP server

## Usage

### Running the Extended Server

You can run the server using the provided utility:

```python
from unreal_blender_mcp.server_extension import run_extended_server

# Start the server on the default port (8000)
run_extended_server()

# Or specify host and port
run_extended_server(host="127.0.0.1", port=8080)
```

### Using the Server Extension Manager

The `ServerExtensionManager` class provides utilities for managing the extended server:

```python
from unreal_blender_mcp.server_extension import ServerExtensionManager

# Create a manager instance
manager = ServerExtensionManager()

# Generate a startup script
script_path = manager.save_startup_script(port=8080)
print(f"Startup script saved to: {script_path}")

# Run the server in a subprocess
server_process = manager.run_server(port=8080)
```

### Accessing Extended Features in Blender

The extended server is designed to work with both standard and extended Blender addons:

1. If connected to the standard addon, the server will function with basic features
2. If connected to the extended addon, additional functionality will be available
3. Extended tools will automatically detect capabilities and adapt

## Available Extended Tools

The extended server adds these additional tools to the standard MCP server:

- `extended_scene_info` - Get enhanced scene information
- `extended_command_example` - Example tool demonstrating extended functionality

## Development

### Adding New Tools

To add new tools to the extended server:

1. Import the `mcp` instance from `extended_server.py`
2. Define new tools using the `@mcp.tool()` decorator
3. Use the `ExtendedBlenderConnection` class for Blender communication

Example:

```python
from unreal_blender_mcp.server_extension.extended_server import mcp, get_extended_blender_connection

@mcp.tool()
def my_new_tool(ctx, param1: str = "") -> str:
    """My custom tool description"""
    blender = get_extended_blender_connection()
    
    # Call a command in the extended Blender addon
    if blender.extended_features_enabled:
        result = blender.send_extended_command("my_custom_command", {"param1": param1})
        return json.dumps(result, indent=2)
    else:
        return "This tool requires the extended Blender addon"
```

## Benefits

This approach allows:

1. Maintaining compatibility with the original `blender-mcp` server
2. Easily pulling in updates from the original server without conflicts
3. Adding custom functionality that might not be appropriate for the upstream project
4. Creating a tighter integration with the extended Blender addon 