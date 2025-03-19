#!/usr/bin/env python
"""
Run script for the extended BlenderMCP server.

This script configures the environment and starts the extended server.
"""

import os
import sys
import logging
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("run_extended_server")

# Add the project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Run the extended BlenderMCP server")
    
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Host address to bind the server to (default: 0.0.0.0)")
    
    parser.add_argument("--port", type=int, default=8000,
                        help="Port to run the server on (default: 8000)")
    
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level (default: INFO)")
    
    parser.add_argument("--check-only", action="store_true",
                        help="Only check the environment without starting the server")
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Import the server extension
    try:
        from src.unreal_blender_mcp.blender_addon_server import ServerExtensionManager
        from src.unreal_blender_mcp.blender_addon_server import run_extended_server
    except ImportError as e:
        logger.error(f"Failed to import server extension: {e}")
        logger.error("Make sure you're running this script from the project root directory")
        return 1
    
    # Create a manager instance
    manager = ServerExtensionManager()
    
    # Check the environment
    env_check = manager.check_environment()
    
    logger.info("Environment check results:")
    for key, value in env_check.items():
        if key != "issues":
            logger.info(f"- {key}: {value}")
    
    if env_check["issues"]:
        logger.warning("Issues found:")
        for issue in env_check["issues"]:
            logger.warning(f"- {issue}")
    else:
        logger.info("No issues found!")
        
    # If check-only flag is set, exit now
    if args.check_only:
        return 0
        
    # Print server info
    logger.info(f"Starting extended BlenderMCP server on {args.host}:{args.port}")
    
    try:
        # Run the server
        run_extended_server(host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 