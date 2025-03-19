"""
Test script to create a material in Blender.
"""

import bpy

# Create a new material
material_name = "TestMaterial"
material = bpy.data.materials.new(name=material_name)

# Enable nodes
material.use_nodes = True
nodes = material.node_tree.nodes

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create a diffuse BSDF node
diffuse = nodes.new(type='ShaderNodeBsdfDiffuse')
diffuse.location = (0, 0)
diffuse.inputs[0].default_value = (1.0, 0.0, 0.0, 1.0)  # Red color

# Create an output node
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (300, 0)

# Link the nodes
links = material.node_tree.links
links.new(diffuse.outputs[0], output.inputs[0])

# Print result
print(f"Created material: {material_name}")

# Return a result object
result = {
    "status": "success",
    "message": f"Created material: {material_name}",
    "material_name": material_name,
    "color": "red"
}

# This is picked up by the MCP system
result 