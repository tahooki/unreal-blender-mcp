import logging
import uvicorn
import argparse
from src.unreal_blender_mcp.server import app

def main():
    """Start the unified MCP server."""
    parser = argparse.ArgumentParser(description="Start the Unreal-Blender MCP server")
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host to run the server on"
    )
    parser.add_argument(
        "--port", type=int, default=8300, help="Port to run the server on"
    )
    parser.add_argument(
        "--log-level", type=str, default="info", 
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level"
    )
    args = parser.parse_args()
    
    # Configure logging
    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    logging.info(f"Starting Unified MCP server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main() 