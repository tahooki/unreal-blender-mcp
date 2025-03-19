"""
Test script to import a model into Unreal Engine.
"""

import unreal
import os
import json

# This script assumes that the export_from_blender.py script has been run
# and the export_path is passed as a parameter to this script

# Get the import path from the provided data string (if any)
# The data parameter should be a JSON string containing the export_path
data_str = locals().get('data', '{}')
try:
    data = json.loads(data_str)
    import_path = data.get('export_path', '')
except:
    import_path = ''

# If no path was provided, use a default path
if not import_path:
    import_path = os.path.join(os.environ.get('TEMP', '/tmp'), 'test_export.fbx')

# Define import parameters
import_destination = '/Game/ImportedModels'
asset_name = 'ImportedSphere'

# Make sure the destination directory exists
if not unreal.EditorAssetLibrary.does_directory_exist(import_destination):
    unreal.EditorAssetLibrary.make_directory(import_destination)

# Create import task
import_task = unreal.AssetImportTask()
import_task.filename = import_path
import_task.destination_path = import_destination
import_task.destination_name = asset_name
import_task.replace_existing = True
import_task.automated = True
import_task.save = True

# Define FBX import options
options = unreal.FbxImportUI()
options.import_mesh = True
options.import_textures = True
options.import_materials = True
options.import_as_skeletal = False
import_task.options = options

# Execute import
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
asset_tools.import_asset_tasks([import_task])

# Check if import was successful
asset_path = f"{import_destination}/{asset_name}"
success = unreal.EditorAssetLibrary.does_asset_exist(asset_path)

# Print the result
if success:
    print(f"Successfully imported: {asset_path}")
    # Return a result object
    result = {
        "status": "success",
        "message": f"Successfully imported: {asset_path}",
        "asset_name": asset_name,
        "asset_path": asset_path,
        "import_source": import_path
    }
else:
    print(f"Failed to import: {import_path}")
    # Return a result object
    result = {
        "status": "error",
        "message": f"Failed to import: {import_path}",
        "import_source": import_path
    }

# This string will be captured by the MCP system
str(result) 