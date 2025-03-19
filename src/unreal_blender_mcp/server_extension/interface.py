"""
Interface module for the extended BlenderMCP server.

This module provides utilities for managing the extended server,
configuring it, and launching it with various options.
"""

import os
import sys
import logging
import subprocess
import tempfile
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

class ServerExtensionManager:
    """
    Manages the extended BlenderMCP server installation and execution.
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the ServerExtensionManager.
        
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
            
        self.original_server_dir = os.path.join(self.base_dir, "blender-mcp", "src", "blender_mcp")
        self.extended_server_dir = os.path.join(self.base_dir, "src", "unreal_blender_mcp", "server_extension")
        
        # Verify directories exist
        if not os.path.isdir(self.original_server_dir):
            logger.warning(f"Original server directory not found: {self.original_server_dir}")
        if not os.path.isdir(self.extended_server_dir):
            logger.warning(f"Extended server directory not found: {self.extended_server_dir}")
    
    def create_startup_script(self, host: str = "0.0.0.0", port: int = 8000, 
                             logging_level: str = "INFO") -> str:
        """
        Generate a Python script to start the extended server.
        
        Args:
            host: Host address to bind the server to
            port: Port number to use
            logging_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            
        Returns:
            String containing Python code to start the server
        """
        script = f"""
import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.{logging_level},
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the extended server
from src.unreal_blender_mcp.server_extension import run_extended_server

# Run the server
run_extended_server(host="{host}", port={port})
"""
        return script
    
    def save_startup_script(self, output_path: Optional[str] = None,
                           host: str = "0.0.0.0", port: int = 8000,
                           logging_level: str = "INFO") -> str:
        """
        Generate and save a startup script to a file.
        
        Args:
            output_path: Path where to save the script. If None, use a default location.
            host: Host address to bind the server to
            port: Port number to use
            logging_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            
        Returns:
            Path to the saved script
        """
        if output_path is None:
            output_path = os.path.join(self.base_dir, "run_extended_server.py")
            
        script = self.create_startup_script(
            host=host,
            port=port,
            logging_level=logging_level
        )
        
        with open(output_path, "w") as f:
            f.write(script)
            
        logger.info(f"Startup script saved to: {output_path}")
        return output_path
    
    def run_server(self, host: str = "0.0.0.0", port: int = 8000,
                  logging_level: str = "INFO", 
                  python_executable: Optional[str] = None) -> subprocess.Popen:
        """
        Start the extended server in a subprocess.
        
        Args:
            host: Host address to bind the server to
            port: Port number to use
            logging_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            python_executable: Path to Python executable to use. If None, use sys.executable.
            
        Returns:
            Subprocess object for the running server
        """
        # Create a temporary script
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            script_path = tmp.name
            tmp.write(self.create_startup_script(
                host=host,
                port=port,
                logging_level=logging_level
            ))
        
        # Use the current Python executable if not specified
        if python_executable is None:
            python_executable = sys.executable
            
        # Start the server as a subprocess
        server_process = subprocess.Popen(
            [python_executable, script_path],
            cwd=self.base_dir,
            # Don't capture stdout/stderr to let them go to the console
            stdout=None,
            stderr=None
        )
        
        logger.info(f"Started extended server on {host}:{port} (PID: {server_process.pid})")
        
        # Clean up the temporary script (on Windows, this might fail while the process is running)
        try:
            os.unlink(script_path)
        except:
            pass
            
        return server_process
    
    def check_environment(self) -> Dict[str, Any]:
        """
        Check the environment to ensure everything is set up correctly for the extended server.
        
        Returns:
            Dictionary with check results
        """
        results = {
            "original_server_dir_exists": os.path.isdir(self.original_server_dir),
            "extended_server_dir_exists": os.path.isdir(self.extended_server_dir),
            "python_version": sys.version,
            "issues": []
        }
        
        # Check for required modules
        try:
            import fastapi
            results["fastapi_version"] = fastapi.__version__
        except ImportError:
            results["issues"].append("FastAPI not installed. Install with: pip install fastapi")
        
        try:
            import uvicorn
            results["uvicorn_version"] = uvicorn.__version__
        except ImportError:
            results["issues"].append("Uvicorn not installed. Install with: pip install uvicorn")
        
        # Try importing the extended server
        try:
            from .extended_server import ExtendedBlenderMCPServer
            results["can_import_extended_server"] = True
        except ImportError as e:
            results["can_import_extended_server"] = False
            results["issues"].append(f"Cannot import ExtendedBlenderMCPServer: {str(e)}")
        
        return results

def main():
    """
    Main function for testing the ServerExtensionManager.
    """
    logging.basicConfig(level=logging.INFO)
    
    # Create an instance of ServerExtensionManager
    manager = ServerExtensionManager()
    
    # Check the environment
    env_check = manager.check_environment()
    print("\nEnvironment check results:")
    for key, value in env_check.items():
        if key != "issues":
            print(f"- {key}: {value}")
    
    if env_check["issues"]:
        print("\nIssues found:")
        for issue in env_check["issues"]:
            print(f"- {issue}")
    else:
        print("\nNo issues found!")
    
    # Generate and save a startup script
    script_path = manager.save_startup_script(port=8000)
    print(f"\nStartup script saved to: {script_path}")
    print("You can run this script to start the extended server.")
    
    print("\nTo start the server now, run:")
    print(f"python {script_path}")


if __name__ == "__main__":
    main() 