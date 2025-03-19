"""
Test script to create a cube in Blender.
"""

import bpy

# Clear existing objects
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))

# Get the created cube
cube = bpy.context.active_object
cube.name = "TestCube"

# Print result
print(f"Created cube: {cube.name}")

# Return a result object
result = {
    "status": "success",
    "message": f"Created cube: {cube.name}",
    "object_name": cube.name,
    "location": list(cube.location)
}

# This is picked up by the MCP system
result 