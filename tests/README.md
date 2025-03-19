# Integration Testing for unreal-blender-mcp

This directory contains integration tests for the unreal-blender-mcp system, which verify that all components (MCP server, Blender addon, and Unreal plugin) work together correctly.

## Requirements

- Python 3.7 or later
- Running MCP server (port 8000)
- Running Blender with the blender-mcp addon (port 8400)
- Running Unreal Engine with the UEPythonServer plugin (port 8500)

## Directory Structure

- `integration/`: Contains the integration test scripts
- `test_data/`: Contains test scripts to run in Blender and Unreal Engine
- `run_integration_tests.py`: Script to run the integration tests

## Running Tests

Before running tests, ensure that:

1. The MCP server is running (`python -m unreal_blender_mcp.server`)
2. Blender is running with the blender-mcp addon enabled
3. Unreal Engine is running with the UEPythonServer plugin enabled

### Run all integration tests:

```bash
python tests/run_integration_tests.py
```

### Run with verbose output:

```bash
python tests/run_integration_tests.py -v
```

### Run a specific test:

```bash
python tests/run_integration_tests.py -t test_blender_connection
```

## Available Tests

### Connection Tests

- `test_blender_connection`: Verify connection to Blender
- `test_unreal_connection`: Verify connection to Unreal Engine
- `test_mcp_connection`: Verify connection to MCP server

### Blender Tests

- `test_blender_create_cube`: Test creating a cube in Blender
- `test_blender_create_material`: Test creating a material in Blender

### Unreal Tests

- `test_unreal_create_actor`: Test creating an actor in Unreal Engine
- `test_unreal_create_blueprint`: Test creating a blueprint in Unreal Engine

### Cross-Platform Tests

- `test_cross_platform_workflow`: Test exporting from Blender and importing to Unreal

### MCP Integration Tests

- `test_mcp_blender_tool_execution`: Test executing a Blender tool via MCP
- `test_mcp_unreal_tool_execution`: Test executing an Unreal tool via MCP

## Adding New Tests

To add a new test:

1. Add a test script to the `test_data/` directory
2. Add a test method to `integration/test_integration.py`
3. Update this documentation if necessary 