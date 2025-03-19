"""
Test script to export a model from Blender.
"""

import bpy
import os
import tempfile

# Create a temporary directory for the export
temp_dir = tempfile.gettempdir()
export_path = os.path.join(temp_dir, "test_export.fbx")

# Clear existing objects
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Create a simple model (a UV sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0), segments=32, ring_count=16)
sphere = bpy.context.active_object
sphere.name = "ExportSphere"

# Select the object for export
bpy.ops.object.select_all(action='DESELECT')
sphere.select_set(True)
bpy.context.view_layer.objects.active = sphere

# Export to FBX
bpy.ops.export_scene.fbx(
    filepath=export_path,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    bake_space_transform=False,
    object_types={'MESH'},
    use_mesh_modifiers=True,
    mesh_smooth_type='OFF',
    use_mesh_edges=False,
    use_custom_props=False,
    path_mode='AUTO',
    embed_textures=False,
    batch_mode='OFF',
    axis_forward='-Z',
    axis_up='Y'
)

# Print result
print(f"Exported sphere to: {export_path}")

# Return a result object
result = {
    "status": "success",
    "message": f"Exported sphere to: {export_path}",
    "object_name": sphere.name,
    "export_path": export_path,
    "format": "fbx"
}

# This is picked up by the MCP system
result 