"""
Test script to create an actor in Unreal Engine.
"""

import unreal

# Create a new actor (static mesh) at origin
actor_location = unreal.Vector(0, 0, 0)
actor_rotation = unreal.Rotator(0, 0, 0)
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.StaticMeshActor, 
    actor_location, 
    actor_rotation
)

# Set the actor name
actor.set_actor_label("TestCube")

# Set the mesh to a cube
mesh_path = "/Engine/BasicShapes/Cube.Cube"
mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
actor.static_mesh_component.set_static_mesh(mesh)

# Print the result
print(f"Created actor: {actor.get_name()}")

# Return a result object
result = {
    "status": "success",
    "message": f"Created actor: {actor.get_name()}",
    "actor_name": actor.get_name(),
    "actor_label": actor.get_actor_label(),
    "location": [0, 0, 0]
}

# This string will be captured by the MCP system
str(result) 