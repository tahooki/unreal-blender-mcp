"""
Tests for the MCP server.

This module contains tests for the MCP server functionality,
including API endpoints, error handling, and message processing.
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
from fastapi.testclient import TestClient

from src.unreal_blender_mcp.server import app, Message, StreamRequest, generate_id
from src.unreal_blender_mcp.blender_connection import BlenderConnection
from src.unreal_blender_mcp.unreal_connection import UnrealConnection
from src.unreal_blender_mcp.langchain_integration import LangchainManager

class TestMCPServer(unittest.TestCase):
    """Test the MCP server."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        
        # Patch connections and langchain manager
        self.blender_patcher = patch('src.unreal_blender_mcp.server.blender_connection')
        self.unreal_patcher = patch('src.unreal_blender_mcp.server.unreal_connection')
        self.langchain_patcher = patch('src.unreal_blender_mcp.server.langchain_manager')
        
        self.mock_blender = self.blender_patcher.start()
        self.mock_unreal = self.unreal_patcher.start()
        self.mock_langchain = self.langchain_patcher.start()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.blender_patcher.stop()
        self.unreal_patcher.stop()
        self.langchain_patcher.stop()
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("server", data["data"])
        self.assertIn("version", data["data"])
        self.assertIn("status", data["data"])
        self.assertIn("endpoints", data["data"])
    
    @patch('src.unreal_blender_mcp.server.BlenderConnection.connect')
    @patch('src.unreal_blender_mcp.server.UnrealConnection.connect')
    def test_status_endpoint(self, mock_unreal_connect, mock_blender_connect):
        """Test the status endpoint."""
        # Mock connections
        mock_blender_connect.return_value = AsyncMock(return_value=True)
        mock_unreal_connect.return_value = AsyncMock(return_value=False)
        
        response = self.client.get("/status")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("server", data["data"])
        self.assertIn("active_connections", data["data"])
        self.assertIn("blender", data["data"])
        self.assertIn("unreal", data["data"])
        self.assertIn("langchain", data["data"])
    
    def test_generate_id(self):
        """Test the generate_id function."""
        id1 = generate_id()
        id2 = generate_id()
        
        # IDs should be unique
        self.assertNotEqual(id1, id2)
        
        # IDs should be strings
        self.assertIsInstance(id1, str)
        self.assertIsInstance(id2, str)
    
    @patch('src.unreal_blender_mcp.server.process_message')
    def test_message_endpoint(self, mock_process_message):
        """Test the message endpoint."""
        # Mock process_message
        async def mock_process():
            yield {"event": "test_event", "data": json.dumps({"id": "123"})}
        
        mock_process_message.return_value = mock_process()
        
        # Test with valid message
        response = self.client.post(
            "/message",
            json={"role": "user", "content": "Hello", "id": "123"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("results", data["data"])
    
    def test_validation_error(self):
        """Test validation error handling."""
        # Send invalid message (missing required field)
        response = self.client.post(
            "/message",
            json={"role": "user"}  # Missing 'content' field
        )
        
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["code"], 422)
        self.assertEqual(data["message"], "Validation error")
        self.assertIn("errors", data["details"])

if __name__ == "__main__":
    unittest.main() 