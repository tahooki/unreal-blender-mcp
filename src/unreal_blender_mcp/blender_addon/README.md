# Extended Blender MCP Addon

This module extends the functionality of the original `blender-mcp` addon while maintaining compatibility with upstream updates. It follows a pattern similar to class inheritance, where the original addon is used as a base, and additional functionality is added on top.

## Structure

- `__init__.py` - Package definition with imports
- `extended_addon.py` - Main extension class inheriting from the original `BlenderMCPServer`
- `extended_blender_connection.py` - Extended connection class for the MCP server
- `interface.py` - Tools for installing the extended addon and managing Blender integration

## How It Works

The extension pattern works as follows:

1. The original `BlenderMCPServer` class from `blender-mcp/addon.py` is imported
2. A new `ExtendedBlenderMCPServer` class inherits from it, adding and overriding methods as needed
3. Custom UI elements are created specifically for the extended functionality
4. The `BlenderAddonManager` class provides tools to create an installable version of the addon

## Usage

### Installing the Extended Addon

The addon can be installed programmatically:

```python
from unreal_blender_mcp.blender_addon.interface import BlenderAddonManager

# Create a manager instance
manager = BlenderAddonManager()

# Install to Blender
manager.install_to_blender(blender_version="3.6", force=True)
```

Or manually:

```python
# Create the installable addon
addon_dir = manager.create_installable_addon(output_dir="/path/to/output")

# The addon can then be installed manually through Blender preferences
```

### Starting the Extended Server

To start the server programmatically:

```python
# Generate a startup script
startup_script = manager.generate_blender_startup_script(port=8401)

# This script can be executed in Blender's Python console or passed to Blender via command line
```

### Connecting from the MCP Server

To connect to the extended server:

```python
from unreal_blender_mcp.blender_addon.extended_blender_connection import ExtendedBlenderConnection

# Create a connection to the extended server
connection = ExtendedBlenderConnection(host="localhost", port=8401)

# Connect and use extended commands
await connection.connect()
version_info = await connection.get_version_info()
```

## Development

### Adding New Commands

To add new commands to the extended server:

1. Add a new method to the `ExtendedBlenderMCPServer` class
2. Modify the `_execute_command_internal` method to handle the new command type
3. Add a corresponding method to the `ExtendedBlenderConnection` class

Example:

```python
# In extended_addon.py
def my_new_command(self, param1, param2):
    """My new custom command"""
    result = do_something(param1, param2)
    return {"custom_result": result}

# In the _execute_command_internal method, add:
if cmd_type == "my_new_command":
    return {"status": "success", "result": self.my_new_command(**params)}

# In extended_blender_connection.py
async def my_new_command(self, param1, param2):
    """Execute my new command."""
    return await self.execute_command("my_new_command", {
        "param1": param1,
        "param2": param2
    })
```

## Benefits

This approach allows:

1. Maintaining compatibility with the original `blender-mcp` addon
2. Easily pulling in updates from the original addon without conflicts
3. Adding custom functionality that might not be appropriate for the upstream project
4. Customizing the behavior for specific needs of the `unreal-blender-mcp` project 