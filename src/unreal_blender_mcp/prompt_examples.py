"""
Example workflows for AI agent interactions with the unreal-blender-mcp system.

This module contains complete examples of interactions between users and AI assistants,
demonstrating how to use the various tools and features of the system.
"""

# Example of creating a simple scene in Blender
BLENDER_SIMPLE_SCENE_EXAMPLE = (
    "User: Can you create a simple scene in Blender with a red cube and a blue sphere?\n\n"
    "Assistant: I'll create a simple scene with a red cube and a blue sphere in Blender.\n\n"
    "I'll first create a cube and set its color to red:\n"
    "1. Creating a cube at the origin\n"
    "2. Creating a new red material\n"
    "3. Assigning the red material to the cube\n\n"
    "Now I'll create a blue sphere:\n"
    "1. Creating a sphere at position (2, 0, 0)\n"
    "2. Creating a new blue material\n"
    "3. Assigning the blue material to the sphere\n\n"
    "The scene has been created successfully with a red cube at the origin and a blue sphere two units to the right."
)

# Example of creating a basic level in Unreal Engine
UNREAL_BASIC_LEVEL_EXAMPLE = (
    "User: Can you create a new level in Unreal Engine with a floor and a few cubes?\n\n"
    "Assistant: I'll create a new level in Unreal Engine with a floor and some cubes.\n\n"
    "First, I'll create a new level:\n"
    "1. Creating a new level called 'BasicCubesLevel'\n\n"
    "Now I'll add a floor to the level:\n"
    "1. Creating a floor plane with size 1000x1000 units\n"
    "2. Positioning it at (0, 0, 0)\n\n"
    "Next, I'll add a few cubes:\n"
    "1. Creating a cube at position (200, 0, 100)\n"
    "2. Creating a second cube at position (-200, 200, 100)\n"
    "3. Creating a third cube at position (0, -200, 100)\n\n"
    "The level has been created successfully with a floor and three cubes positioned in different locations."
)

# Example of transferring a model from Blender to Unreal
BLENDER_TO_UNREAL_EXAMPLE = (
    "User: Can you help me create a character in Blender and then import it into Unreal Engine?\n\n"
    "Assistant: I'll help you create a simple character in Blender and then import it into Unreal Engine.\n\n"
    "Let's break this down into steps:\n\n"
    "First, let's create a basic character in Blender:\n"
    "1. Creating a base mesh for the character using primitives\n"
    "2. Adding a torso (cylinder) at the origin\n"
    "3. Adding a head (sphere) at position (0, 0, 2)\n"
    "4. Adding arms (cylinders) at positions (-1, 0, 0) and (1, 0, 0)\n"
    "5. Adding legs (cylinders) at positions (-0.5, 0, -2) and (0.5, 0, -2)\n"
    "6. Joining all the meshes into a single character mesh\n"
    "7. Adding a simple material to the character\n\n"
    "Now, let's export the character from Blender to FBX format:\n"
    "1. Selecting the character mesh\n"
    "2. Exporting to FBX format with appropriate settings\n"
    "3. Saving the FBX file to 'character.fbx'\n\n"
    "Finally, let's import the character into Unreal Engine:\n"
    "1. Importing the FBX file into Unreal Engine\n"
    "2. Configuring import settings (skeletal mesh vs. static mesh)\n"
    "3. Creating a material in Unreal for the character\n"
    "4. Assigning the material to the imported character\n"
    "5. Placing the character in the current level\n\n"
    "The character has been successfully created in Blender and imported into Unreal Engine."
)

# Example of debugging an error in Blender
ERROR_HANDLING_EXAMPLE = (
    "User: I tried to create a complex mesh in Blender but I'm getting an error about non-manifold geometry. Can you help fix it?\n\n"
    "Assistant: I'll help you diagnose and fix the non-manifold geometry error in your Blender mesh.\n\n"
    "Non-manifold geometry typically occurs when:\n"
    "1. There are edges connected to more than two faces\n"
    "2. There are holes in the mesh\n"
    "3. There are overlapping vertices or edges\n\n"
    "Let's check your current scene:\n"
    "1. Getting information about the current scene\n"
    "2. Analyzing the mesh for non-manifold elements\n\n"
    "I found several issues:\n"
    "1. There are 5 edges connected to more than two faces\n"
    "2. There are 3 small holes in the mesh\n"
    "3. There are 12 overlapping vertices\n\n"
    "Let's fix these issues one by one:\n"
    "1. Merging the overlapping vertices first\n"
    "2. Repairing the edges with improper face connections\n"
    "3. Filling the holes in the mesh\n\n"
    "The mesh has been repaired successfully. All non-manifold geometry has been fixed, and the mesh is now ready for further work or export."
) 