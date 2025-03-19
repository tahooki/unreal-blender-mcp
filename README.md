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
- **Extension Structure**: Easily extend both Blender addon and server while maintaining compatibility with upstream updates

## Architecture

The system consists of three main components:

1. **MCP Server**: Central hub communicating with AI agents via SSE (Server-Sent Events) on port 8000
2. **Blender Addon**: Socket server within Blender on port 8400 (standard) or 8401 (extended)
3. **Unreal Plugin**: HTTP server within Unreal Engine on port 8500

```
[AI Agent] <--SSE--> [MCP Server (8000)] 
                        |
                        |--HTTP--> [Blender Addon (8400/8401)]
                        |
                        |--HTTP--> [Unreal Plugin (8500)]
```

## Extension Structure

This project uses an extension approach to maintain compatibility with upstream changes:

- **Blender Addon Extension**: Extends the original `BlenderMCPServer` while keeping the original code intact
- **Server Extension**: Enhances the original server with additional tools and Unreal Engine integration
- **Interface Tools**: Provides utilities for installing, configuring, and running extensions

This approach allows easy updates from the original projects without code conflicts.

## Installation

### Requirements

- Python 3.10 or later
- Blender 3.0 or later
- Unreal Engine 5.0 or later
- uv package manager

### Installation Steps

1. Clone this repository:
   ```bash
   git clone --recursive https://github.com/tahooki/unreal-blender-mcp.git
   cd unreal-blender-mcp
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   uv pip install -e .
   ```

3. Install the Blender addon (choose one option):
   
   **Option 1: Standard addon (Original blender-mcp)**
   - Open Blender
   - Go to Edit > Preferences > Add-ons
   - Click "Install..." and select `blender-mcp/addon.py`
   - Enable the "Interface: Blender MCP" addon

   **Option 2: Extended addon (With additional features)**
   - Run the extension installer script:
     ```bash
     python -c "from src.unreal_blender_mcp.blender_addon import BlenderAddonManager; BlenderAddonManager().install_to_blender(force=True)"
     ```
   - Open Blender
   - Go to Edit > Preferences > Add-ons
   - Enable the "Interface: Extended Blender MCP" addon

4. Install the Unreal plugin:
   - Copy the `UEPythonServer` folder to your Unreal project's `Plugins` directory
   - Start Unreal Engine and enable the plugin in Edit > Plugins
   - Restart the engine

## Usage

### Running the Standard Server

1. Start the MCP server:
   ```bash
   python main.py
   ```

2. Start Blender and enable the MCP server from the BlenderMCP panel in the 3D viewport sidebar

3. Start Unreal Engine with your project

4. Configure your AI agent to communicate with the MCP server

### Running the Extended Server

1. Start the extended MCP server:
   ```bash
   python run_extended_server.py
   ```
   
   You can customize server options:
   ```bash
   python run_extended_server.py --host 127.0.0.1 --port 8080 --log-level DEBUG
   ```

2. Start Blender and enable the Extended MCP server from the ExtBlenderMCP panel in the 3D viewport sidebar

3. Start Unreal Engine with your project

4. Configure your AI agent to communicate with the extended MCP server

### Using the Extension Interfaces Programmatically

**Blender Addon Extension:**
```python
from src.unreal_blender_mcp.blender_addon import BlenderAddonManager

# Create installer
manager = BlenderAddonManager()

# Install to Blender
manager.install_to_blender(blender_version="3.6", force=True)

# Generate startup script for Blender
script = manager.generate_blender_startup_script(port=8401)
print(script)  # Run this in Blender's Python console
```

**Server Extension:**
```python
from src.unreal_blender_mcp.server_extension import ServerExtensionManager

# Create manager
manager = ServerExtensionManager()

# Check environment
env_check = manager.check_environment()
print(env_check)

# Run server in subprocess
server_process = manager.run_server(port=8080)
```

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
        },
        "unreal-blender-ext": {
            "command": "python",
            "args": [
                "path/to/unreal-blender-mcp/run_extended_server.py"
            ]
        }
    }
}
```

### Integration with Cursor

Add the following commands in Cursor Settings > MCP:

- Standard Server: `uvx unreal-blender-mcp`
- Extended Server: `python path/to/unreal-blender-mcp/run_extended_server.py`

## Comparison: Standard vs Extended

| Feature | Standard Server | Extended Server |
|---------|----------------|----------------|
| Blender Control | ✅ | ✅ |
| Unreal Control | ✅ | ✅ |
| Custom Blender Commands | ❌ | ✅ |
| Enhanced Scene Info | ❌ | ✅ |
| Auto Feature Detection | ❌ | ✅ |
| Upstream Compatibility | ✅ | ✅ |

Choose the standard server for basic functionality or the extended server for advanced features.

## Development

See the [Project Document](Project-document.md) and [workflow](workflow/) directory for detailed development information.

For extending this project:
- To add new Blender addon features: Modify `src/unreal_blender_mcp/blender_addon/extended_addon.py`
- To add new server tools: Modify `src/unreal_blender_mcp/server_extension/extended_server.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- This project builds upon [blender-mcp](https://github.com/ahujasid/blender-mcp.git) by Siddharth Ahuja.

## 서브모듈 정보

이 프로젝트는 `blender-mcp`를 Git 서브모듈로 포함하고 있습니다. 저장소를 클론할 때 다음 명령어를 사용하세요:

```bash
# 서브모듈을 포함하여 클론
git clone --recursive https://github.com/tahooki/unreal-blender-mcp.git

# 또는 일반 클론 후 서브모듈 초기화
git clone https://github.com/tahooki/unreal-blender-mcp.git
cd unreal-blender-mcp
git submodule update --init --recursive
```