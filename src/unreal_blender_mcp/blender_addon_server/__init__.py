"""
Server Extension Module for unreal-blender-mcp

This module extends the original BlenderMCP server to provide additional
functionality while maintaining compatibility with upstream updates.
"""

from .extended_server import ExtendedBlenderMCPServer, run_extended_server
from .interface import ServerExtensionManager

__all__ = [
    'ExtendedBlenderMCPServer',
    'run_extended_server',
    'ServerExtensionManager'
] 