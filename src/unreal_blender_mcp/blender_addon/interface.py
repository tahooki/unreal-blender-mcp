"""
Interface module to connect the MCP server with the extended Blender addon.

This module provides functions to install, load, and use the extended Blender addon.
"""

import os
import sys
import shutil
import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class BlenderAddonManager:
    """
    Manages installation and interaction with the extended Blender addon.
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the BlenderAddonManager.
        
        Args:
            base_dir: Base directory of the project. If None, will try to determine automatically.
        """
        if base_dir is None:
            # Try to determine the base directory
            self.base_dir = os.path.abspath(os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            ))
        else:
            self.base_dir = os.path.abspath(base_dir)
            
        self.original_addon_dir = os.path.join(self.base_dir, "blender-mcp")
        self.extended_addon_dir = os.path.join(self.base_dir, "src", "unreal_blender_mcp", "blender_addon")
        
        # Verify directories exist
        if not os.path.isdir(self.original_addon_dir):
            logger.warning(f"Original addon directory not found: {self.original_addon_dir}")
        if not os.path.isdir(self.extended_addon_dir):
            logger.warning(f"Extended addon directory not found: {self.extended_addon_dir}")
    
    def create_installable_addon(self, output_dir: Optional[str] = None) -> str:
        """
        Create an installable version of the extended Blender addon.
        
        This will copy the original addon files and the extended addon implementation
        into a single installable directory structure.
        
        Args:
            output_dir: Directory where to create the installable addon.
                If None, a temporary directory will be used.
                
        Returns:
            Path to the created installable addon.
        """
        # Create a temporary directory if no output directory specified
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="unreal_blender_mcp_addon_")
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        addon_dir = os.path.join(output_dir, "blender_mcp_extended")
        os.makedirs(addon_dir, exist_ok=True)
        
        # Copy the original addon.py to the installable directory
        shutil.copy(
            os.path.join(self.original_addon_dir, "addon.py"),
            os.path.join(addon_dir, "original_addon.py")
        )
        
        # Copy extended addon files
        for filename in os.listdir(self.extended_addon_dir):
            # Skip __pycache__ directory
            if filename == "__pycache__":
                continue
                
            src_path = os.path.join(self.extended_addon_dir, filename)
            dst_path = os.path.join(addon_dir, filename)
            
            if os.path.isfile(src_path):
                shutil.copy(src_path, dst_path)
            elif os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        
        # Create a new __init__.py file that imports and uses the extended addon
        init_path = os.path.join(addon_dir, "__init__.py")
        with open(init_path, "w") as f:
            f.write("""
# Extended BlenderMCP Addon for unreal-blender-mcp
#
# This is an extension of the original BlenderMCP addon that adds new functionality
# while maintaining compatibility with the original.

import bpy
import os
import sys

# Add the current directory to the Python path to ensure imports work
if __file__ not in sys.path:
    sys.path.append(os.path.dirname(__file__))

# Import from extended_addon
from extended_addon import ExtendedBlenderMCPServer, register_extended, unregister_extended

bl_info = {
    "name": "Extended Blender MCP",
    "author": "unreal-blender-mcp",
    "version": (0, 4),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > ExtBlenderMCP",
    "description": "Extended version of BlenderMCP for unreal-blender-mcp",
    "category": "Interface",
}

def register():
    # Register the extended addon
    register_extended()

def unregister():
    # Unregister the extended addon
    unregister_extended()

if __name__ == "__main__":
    register()
""")
        
        logger.info(f"Created installable extended addon at: {addon_dir}")
        return addon_dir
    
    def get_blender_addon_path(self, blender_version: str = "3.0") -> Optional[str]:
        """
        Get the path where Blender addons should be installed.
        
        Args:
            blender_version: Blender version string (e.g., "3.0")
            
        Returns:
            Path to the Blender addons directory, or None if not found.
        """
        # Get platform-specific Blender addon paths
        addon_paths = []
        
        # Check for user preferences addon path - this is where most users install addons
        if sys.platform == "win32":
            # Windows
            appdata = os.environ.get("APPDATA")
            if appdata:
                addon_paths.append(os.path.join(appdata, "Blender Foundation", "Blender", blender_version, "scripts", "addons"))
        elif sys.platform == "darwin":
            # macOS
            home = os.path.expanduser("~")
            addon_paths.append(os.path.join(home, "Library", "Application Support", "Blender", blender_version, "scripts", "addons"))
        else:
            # Linux
            home = os.path.expanduser("~")
            addon_paths.append(os.path.join(home, ".config", "blender", blender_version, "scripts", "addons"))
        
        # Also check if BLENDER_USER_SCRIPTS environment variable is set
        user_scripts = os.environ.get("BLENDER_USER_SCRIPTS")
        if user_scripts:
            addon_paths.append(os.path.join(user_scripts, "addons"))
        
        # Return the first path that exists
        for path in addon_paths:
            if os.path.isdir(path):
                return path
        
        # If none of the paths exist, return the first one (it will need to be created)
        return addon_paths[0] if addon_paths else None
    
    def install_to_blender(self, blender_version: str = "3.0", force: bool = False) -> bool:
        """
        Install the extended addon to the Blender addons directory.
        
        Args:
            blender_version: Blender version string (e.g., "3.0")
            force: If True, overwrite existing installation
            
        Returns:
            True if installation was successful, False otherwise.
        """
        # Get Blender addon path
        blender_addon_path = self.get_blender_addon_path(blender_version)
        if not blender_addon_path:
            logger.error("Failed to determine Blender addon path")
            return False
        
        # Create the Blender addon directory if it doesn't exist
        os.makedirs(blender_addon_path, exist_ok=True)
        
        # Create the installable addon
        installable_addon = self.create_installable_addon()
        
        # Define the target directory in the Blender addons folder
        target_dir = os.path.join(blender_addon_path, "blender_mcp_extended")
        
        # Check if the addon is already installed
        if os.path.exists(target_dir):
            if force:
                # Remove existing installation
                shutil.rmtree(target_dir)
            else:
                logger.warning(f"Addon already installed at {target_dir}. Use force=True to overwrite.")
                return False
        
        # Copy the installable addon to the Blender addons directory
        shutil.copytree(installable_addon, target_dir)
        
        logger.info(f"Installed extended addon to Blender at: {target_dir}")
        return True
    
    def generate_blender_startup_script(self, port: int = 8401) -> str:
        """
        Generate a Python script that can be run in Blender to start the extended addon server.
        
        Args:
            port: Port number for the server to listen on
            
        Returns:
            String containing Python code to start the extended addon server
        """
        script = f"""
import bpy

# Try to load the extended addon if not already loaded
if not 'blender_mcp_extended' in bpy.context.preferences.addons:
    try:
        bpy.ops.preferences.addon_enable(module='blender_mcp_extended')
        print("Enabled blender_mcp_extended addon")
    except Exception as e:
        print(f"Error enabling blender_mcp_extended addon: {{str(e)}}")

# Import the extended addon module
try:
    from blender_mcp_extended.extended_addon import ExtendedBlenderMCPServer
    
    # Set port in scene settings
    bpy.context.scene.extended_blendermcp_port = {port}
    print(f"Set extended BlenderMCP port to {{bpy.context.scene.extended_blendermcp_port}}")
    
    # Create and start the server
    if not hasattr(bpy.types, "extended_blendermcp_server") or not bpy.types.extended_blendermcp_server:
        bpy.types.extended_blendermcp_server = ExtendedBlenderMCPServer(port={port})
    
    # Start the server
    bpy.types.extended_blendermcp_server.start()
    bpy.context.scene.extended_blendermcp_server_running = True
    print(f"Started extended BlenderMCP server on port {port}")
    
except Exception as e:
    print(f"Error starting extended BlenderMCP server: {{str(e)}}")
"""
        return script


def main():
    """
    Main function for testing the BlenderAddonManager.
    """
    logging.basicConfig(level=logging.INFO)
    
    # Create an instance of the BlenderAddonManager
    manager = BlenderAddonManager()
    
    # Create and install the addon
    addon_dir = manager.create_installable_addon()
    print(f"Created installable addon at: {addon_dir}")
    
    # Generate a startup script
    script = manager.generate_blender_startup_script(port=8401)
    print("\nBlender Startup Script:")
    print(script)
    
    print("\nYou can now install this addon in Blender by:")
    print(f"1. Copying {addon_dir} to your Blender addons directory")
    print("2. Enabling the 'Extended Blender MCP' addon in Blender preferences")
    print("3. Using the script above to start the extended server")


if __name__ == "__main__":
    main() 