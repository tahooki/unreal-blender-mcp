# Unreal-Blender MCP

Unreal-Blender MCP is a unified server for controlling both Blender and Unreal Engine via AI agents using the MCP (Machine Control Protocol) approach.

## Overview

This project extends the [blender-mcp](https://github.com/ahujasid/blender-mcp.git) framework to include support for Unreal Engine, allowing AI agents like Claude and ChatGPT to simultaneously control both platforms through a single interface.

## Features

- **Unified Control**: Single MCP server to control both Blender and Unreal Engine
- **AI Agent Integration**: Designed to work with Claude, ChatGPT, and other AI assistants
- **Blender Features**: Retains all blender-mcp functionality including:
  - Scene manipulation
  - Object creation and editing
  - Material management
  - PolyHaven asset integration
  - Hyper3D Rodin model generation
- **Unreal Engine Features**:
  - Level creation and management
  - Asset importing
  - Python code execution
  - Scene manipulation

## Architecture

The system consists of three main components:

1. **MCP Server**: Central hub communicating with AI agents via SSE (Server-Sent Events) on port 8300
2. **Blender Addon**: Socket server within Blender on port 8400
3. **Unreal Plugin**: HTTP server within Unreal Engine on port 8500

```
[AI Agent] <--SSE--> [MCP Server (8300)] 
                        |
                        |--HTTP--> [Blender Addon (8400)]
                        |
                        |--HTTP--> [Unreal Plugin (8500)]
```

## Installation

### Requirements

- Python 3.10 or later
- Blender 3.0 or later
- Unreal Engine 5.0 or later
- uv package manager

### Installation Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/[username]/unreal-blender-mcp.git
   cd unreal-blender-mcp
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   uv pip install -e .
   ```

3. Install the Blender addon:
   - Open Blender
   - Go to Edit > Preferences > Add-ons
   - Click "Install..." and select `blender-mcp/addon.py`
   - Enable the "Interface: Blender MCP" addon

4. Install the Unreal plugin:
   - Copy the `UEPythonServer` folder to your Unreal project's `Plugins` directory
   - Start Unreal Engine and enable the plugin in Edit > Plugins
   - Restart the engine

## Usage

1. Start the MCP server:
   ```bash
   python main.py
   ```

2. Start Blender and enable the MCP server from the BlenderMCP panel in the 3D viewport sidebar

3. Start Unreal Engine with your project

4. Configure your AI agent to communicate with the MCP server

### Integration with Claude

Add the following to Claude for Desktop's configuration:

```json
{
    "mcpServers": {
        "unreal-blender": {
            "command": "uvx",
            "args": [
                "unreal-blender-mcp"
            ]
        }
    }
}
```

### Integration with Cursor

Add the following command in Cursor Settings > MCP:

```
uvx unreal-blender-mcp
```

## Development

See the [Project Document](Project-document.md) and [workflow](workflow/) directory for detailed development information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- This project builds upon [blender-mcp](https://github.com/ahujasid/blender-mcp.git) by Siddharth Ahuja.