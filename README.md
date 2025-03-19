# Unreal-Blender MCP

Unreal-Blender MCP is a unified server for controlling both Blender and Unreal Engine via AI agents using the MCP (Machine Control Protocol) approach.

## Overview

This project extends the [blender-mcp](https://github.com/ahujasid/blender-mcp.git) framework to include support for Unreal Engine, allowing AI agents like Claude and ChatGPT to simultaneously control both platforms through a single interface.

## Submodule Information

This project includes `blender-mcp` as a Git submodule. When cloning the repository, use the following commands:

```bash
# Clone with submodules
git clone --recursive https://github.com/tahooki/unreal-blender-mcp.git

# Or clone normally and then initialize submodules
git clone https://github.com/tahooki/unreal-blender-mcp.git
cd unreal-blender-mcp
git submodule update --init --recursive
```

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
[AI Agent] <--SSE--> [MCP Server (8300)] 
                        |
                        |--HTTP--> [Blender Addon (8400)]
                        |
                        |--HTTP--> [Unreal Plugin (8500)]
```

## Extension Structure

This project uses an extension approach to maintain compatibility with upstream changes:

- **Blender Addon Extension**: Extends the original `BlenderMCPServer` while keeping the original code intact
- **Server Extension**: Enhances the original server with additional tools and Unreal Engine integration
- **Interface Tools**: Provides utilities for installing, configuring, and running extensions

This approach allows easy updates from the original projects without code conflicts.

## Step-by-Step Installation and Setup Guide

### Prerequisites

- Python 3.10 or later
- Blender 3.0 or later
- Unreal Engine 5.0 or later
- uv package manager (install with `pip install uv` if you don't have it)

### 1. Clone the Repository

```bash
# Clone with submodules (recommended)
git clone --recursive https://github.com/tahooki/unreal-blender-mcp.git
cd unreal-blender-mcp

# Or if you already cloned without --recursive:
git clone https://github.com/tahooki/unreal-blender-mcp.git
cd unreal-blender-mcp
git submodule update --init --recursive
```

### 2. Set Up Python Environment

```bash
# Create a virtual environment and activate it
uv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install project dependencies
uv pip install -e .
```

### 3. Install Blender Addon

Choose ONE of the following options:

#### Option A: Standard Addon (Original blender-mcp)
1. Open Blender
2. Navigate to Edit > Preferences > Add-ons
3. Click "Install..." button
4. Browse and select `blender-mcp/addon.py` file
5. Enable the "Interface: Blender MCP" addon (check the box)

#### Option B: Extended Addon (With additional features)
1. Run the extension installer script:
   ```bash
   python -c "from src.unreal_blender_mcp.blender_addon import BlenderAddonManager; BlenderAddonManager().install_to_blender(force=True)"
   ```
2. Open Blender
3. Navigate to Edit > Preferences > Add-ons
4. Find and enable the "Interface: Extended Blender MCP" addon (check the box)

### 4. Install Unreal Engine Plugin

1. Locate the `UEPythonServer` folder in this project
2. Copy the entire folder to your Unreal project's `Plugins` directory
   - If your project doesn't have a `Plugins` directory, create one
3. Start Unreal Engine with your project
4. Navigate to Edit > Plugins in the menu
5. Find and enable the Python Server plugin
6. Restart Unreal Engine when prompted

### 5. Start the MCP Server

Choose ONE of the following options:

#### Option A: Standard Server
```bash
# Make sure your virtual environment is activated
python main.py
```

#### Option B: Extended Server (More features)
```bash
# Make sure your virtual environment is activated
python run_extended_server.py

# Optional: Customize server options
python run_extended_server.py --host 127.0.0.1 --port 8080 --log-level DEBUG
```

### 6. Enable the Blender Server Connection

1. Start Blender (if not already running)
2. In the 3D viewport, press `N` to open the sidebar panel
3. Select the appropriate tab:
   - "BlenderMCP" (if using standard addon)
   - "ExtBlenderMCP" (if using extended addon)
4. Click the "Start Server" button
5. Verify the server starts successfully (check console output)

### 7. Verify Unreal Engine Connection

1. With Unreal Engine running and plugin enabled
2. The Python server should automatically start
3. Check the Output Log (Window > Developer Tools > Output Log) for any messages
4. The Unreal plugin should now be ready to receive commands

### 8. Connect an AI Agent

#### Option A: Integrate with Claude for Desktop

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
                "/path/to/unreal-blender-mcp/run_extended_server.py"
            ]
        }
    }
}
```
Replace `/path/to/` with your actual project path.

#### Option B: Integrate with Cursor

1. Open Cursor Settings
2. Navigate to MCP section
3. Add the following commands:
   - Standard Server: `uvx unreal-blender-mcp`
   - Extended Server: `python /path/to/unreal-blender-mcp/run_extended_server.py`
   
   Replace `/path/to/` with your actual project path.

#### Option C: Integrate with Other AI Tools

Refer to your AI tool's documentation for integrating with MCP servers, and point it to:
- MCP Server URL: `http://localhost:8000` (or custom port if specified)

### 9. Testing the System

Once all components are running:

1. Use your AI agent to interact with Blender by asking it to:
   - Create a simple cube or sphere
   - Modify object properties
   - Create materials

2. Use your AI agent to interact with Unreal Engine by asking it to:
   - Create a new level
   - Place assets
   - Modify scene properties

3. Try more complex operations that involve both platforms working together

### Troubleshooting

If you encounter issues:

1. Check that all servers are running (MCP, Blender, Unreal)
2. Verify port configurations match (default: 8000 for MCP, 8400/8401 for Blender, 8500 for Unreal)
3. Check console outputs for error messages
4. Restart components in the correct order: MCP server first, then Blender, then Unreal Engine

For more detailed information on development and extending the system, see the [Project Document](Project-document.md) and [workflow](workflow/) directory.

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

## Future Developments

The following improvements are planned for future releases:

### Structured Unreal Engine API

Currently, the Unreal Engine communication relies primarily on direct Python code execution. A planned enhancement is to implement a structured API similar to the Blender integration:

- Create predefined functions for common Unreal Engine operations
- Implement proper error handling and validation
- Improve security by limiting execution scope
- Enhance stability and predictability of operations
- Maintain backward compatibility while adding structure

This enhancement will create a more consistent experience across both engines and improve the overall reliability of the system. See the [workflow documentation](workflow/08-unreal-engine-refinement.md) for more details on this planned development.