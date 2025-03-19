# UE Python Server Plugin

This plugin provides an HTTP server for executing Python code in Unreal Engine, designed to work with the unreal-blender-mcp system.

## Features

- HTTP server on port 8500 for executing Python code in Unreal Engine
- Editor UI for server configuration and control
- Status indicators in the editor toolbar
- Secure, local-only execution environment

## Installation

1. Copy the `UEPythonServer` directory to your Unreal Engine project's `Plugins` directory
2. Enable the plugin in Edit > Plugins > Scripting > UE Python Server

## Requirements

- Unreal Engine 4.26 or later
- Python 3.7 or later
- PythonScriptPlugin must be enabled

## Usage

### Starting the Server

1. Click the "Start Python Server" button in the editor toolbar, or
2. Open the UE Python Server configuration panel by clicking the button and change settings

### API Endpoints

- **GET /status**: Check server status
  - Returns: `{"status": "running", "version": "0.1.0", "port": 8500, "python_available": true}`

- **POST /execute**: Execute Python code
  - Request Body: `{"code": "import unreal\nprint('Hello from Python')"}`
  - Returns: `{"status": "success", "result": "Hello from Python\n"}`

### Example Python Code

```python
# Get the current level
import unreal
current_level = unreal.EditorLevelLibrary.get_editor_world()
print(f"Current level: {current_level.get_name()}")

# Create an actor
actor_location = unreal.Vector(0, 0, 0)
actor_rotation = unreal.Rotator(0, 0, 0)
cube = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.StaticMeshActor, 
    actor_location, 
    actor_rotation
)
print(f"Created actor: {cube.get_name()}")

# Set the mesh to a cube
mesh_path = "/Engine/BasicShapes/Cube.Cube"
mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
cube.static_mesh_component.set_static_mesh(mesh)
print("Set mesh to cube")
```

## Integration with MCP Server

This plugin is designed to work with the unreal-blender-mcp system, allowing AI agents to control Unreal Engine through a unified interface.

1. Start the UE Python Server in your Unreal Engine project
2. Start the MCP server which will connect to this plugin
3. AI agents can now execute Python code in Unreal Engine through the MCP server

## Security Considerations

- The server only accepts connections from localhost by default
- All code is executed in the Unreal Engine Python interpreter
- Be careful when executing arbitrary Python code, as it has full access to the Unreal Engine API

## Troubleshooting

- If the server fails to start, check if the port (8500) is already in use
- Ensure the PythonScriptPlugin is enabled in your project
- Check the Output Log in Unreal Engine for error messages 