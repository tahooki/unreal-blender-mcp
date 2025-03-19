"""
Test script to create a blueprint in Unreal Engine.
"""

import unreal

# Set the blueprint name and location
blueprint_name = "TestBlueprint"
save_path = "/Game/TestBlueprints"

# Make sure the directory exists
if not unreal.EditorAssetLibrary.does_directory_exist(save_path):
    unreal.EditorAssetLibrary.make_directory(save_path)

# Create a new blueprint factory
factory = unreal.BlueprintFactory()
factory.set_editor_property("ParentClass", unreal.Actor)

# Create the blueprint asset
blueprint_path = f"{save_path}/{blueprint_name}"
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
new_blueprint = asset_tools.create_asset(blueprint_name, save_path, None, factory)

# Add a static mesh component to the blueprint
if new_blueprint is not None:
    # Add component
    mesh_component = unreal.EditorStaticMeshLibrary.add_static_mesh_component_to_blueprint(
        new_blueprint,
        unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere.Sphere")
    )
    
    # Save the blueprint
    unreal.EditorAssetLibrary.save_asset(blueprint_path)
    
    # Print result
    print(f"Created blueprint: {blueprint_path}")
    
    # Return a result object
    result = {
        "status": "success",
        "message": f"Created blueprint: {blueprint_path}",
        "blueprint_name": blueprint_name,
        "blueprint_path": blueprint_path
    }
else:
    # Failed to create blueprint
    print("Failed to create blueprint")
    
    # Return a result object
    result = {
        "status": "error",
        "message": "Failed to create blueprint"
    }

# This string will be captured by the MCP system
str(result) 