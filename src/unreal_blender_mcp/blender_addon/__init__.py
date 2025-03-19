"""
Blender Addon Extension Module for unreal-blender-mcp

This module extends the original BlenderMCPServer to provide additional
functionality while maintaining compatibility with upstream updates.
"""

from .extended_addon import ExtendedBlenderMCPServer, register_extended, unregister_extended
from .extended_blender_connection import ExtendedBlenderConnection
from .interface import BlenderAddonManager

__all__ = [
    'ExtendedBlenderMCPServer', 
    'register_extended', 
    'unregister_extended',
    'ExtendedBlenderConnection',
    'BlenderAddonManager'
] 