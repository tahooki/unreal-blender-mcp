"""
Tests for connection classes.

This module contains tests for the BlenderConnection and UnrealConnection classes,
which handle communication with Blender and Unreal Engine.
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp
from aiohttp import ClientResponseError

from src.unreal_blender_mcp.blender_connection import BlenderConnection
from src.unreal_blender_mcp.unreal_connection import UnrealConnection

class TestBlenderConnection(unittest.TestCase):
    """Test the BlenderConnection class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.connection = BlenderConnection(host="localhost", port=8400)
        
        # Patch ClientSession
        self.session_patcher = patch('src.unreal_blender_mcp.blender_connection.aiohttp.ClientSession')
        self.mock_session_class = self.session_patcher.start()
        self.mock_session = MagicMock()
        self.mock_session_class.return_value = self.mock_session
        
        # Set up ClientSession.__aenter__ to return self.mock_session
        self.mock_session.__aenter__ = AsyncMock(return_value=self.mock_session)
        self.mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Set up default response
        self.mock_response = MagicMock()
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={"status": "success", "result": "ok"})
        self.mock_session.post = AsyncMock(return_value=self.mock_response)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.session_patcher.stop()
    
    async def test_connect(self):
        """Test the connect method."""
        # Test successful connection
        self.mock_response.status = 200
        self.mock_response.json.return_value = {"status": "success"}
        
        result = await self.connection.connect()
        self.assertTrue(result)
        
        # Test failed connection
        self.mock_response.status = 404
        
        result = await self.connection.connect()
        self.assertFalse(result)
        
        # Test exception
        self.mock_session.post.side_effect = aiohttp.ClientError("Connection error")
        
        result = await self.connection.connect()
        self.assertFalse(result)
    
    async def test_close(self):
        """Test the close method."""
        # Test successful close
        await self.connection.close()
        self.mock_session.close.assert_called_once()
    
    async def test_get_scene_info(self):
        """Test the get_scene_info method."""
        self.mock_response.json.return_value = {
            "status": "success",
            "result": {"objects": [], "materials": []}
        }
        
        result = await self.connection.get_scene_info()
        self.assertEqual(result, {"objects": [], "materials": []})
        
        # Check correct arguments were passed
        self.mock_session.post.assert_called_with(
            "http://localhost:8400/execute",
            json={"type": "get_scene_info"}
        )
    
    async def test_get_object_info(self):
        """Test the get_object_info method."""
        self.mock_response.json.return_value = {
            "status": "success",
            "result": {"name": "Cube", "location": [0, 0, 0]}
        }
        
        result = await self.connection.get_object_info("Cube")
        self.assertEqual(result, {"name": "Cube", "location": [0, 0, 0]})
        
        # Check correct arguments were passed
        self.mock_session.post.assert_called_with(
            "http://localhost:8400/execute",
            json={"type": "get_object_info", "name": "Cube"}
        )
    
    async def test_execute_code(self):
        """Test the execute_code method."""
        self.mock_response.json.return_value = {
            "status": "success",
            "result": "Code executed successfully"
        }
        
        result = await self.connection.execute_code("print('Hello')")
        self.assertEqual(result, "Code executed successfully")
        
        # Check correct arguments were passed
        self.mock_session.post.assert_called_with(
            "http://localhost:8400/execute",
            json={"type": "execute_code", "code": "print('Hello')"}
        )
    
    async def test_error_response(self):
        """Test handling of error responses."""
        self.mock_response.json.return_value = {
            "status": "error",
            "message": "Error executing code"
        }
        
        result = await self.connection.execute_code("print('Hello')")
        self.assertEqual(result, {"status": "error", "message": "Error executing code"})

class TestUnrealConnection(unittest.TestCase):
    """Test the UnrealConnection class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.connection = UnrealConnection(host="localhost", port=8500)
        
        # Patch ClientSession
        self.session_patcher = patch('src.unreal_blender_mcp.unreal_connection.aiohttp.ClientSession')
        self.mock_session_class = self.session_patcher.start()
        self.mock_session = MagicMock()
        self.mock_session_class.return_value = self.mock_session
        
        # Set up ClientSession.__aenter__ to return self.mock_session
        self.mock_session.__aenter__ = AsyncMock(return_value=self.mock_session)
        self.mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Set up default response
        self.mock_response = MagicMock()
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={"result": "ok", "error": None})
        self.mock_session.post = AsyncMock(return_value=self.mock_response)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.session_patcher.stop()
    
    async def test_connect(self):
        """Test the connect method."""
        # Test successful connection
        self.mock_response.status = 200
        
        result = await self.connection.connect()
        self.assertTrue(result)
        
        # Test failed connection
        self.mock_response.status = 404
        
        result = await self.connection.connect()
        self.assertFalse(result)
        
        # Test exception
        self.mock_session.post.side_effect = aiohttp.ClientError("Connection error")
        
        result = await self.connection.connect()
        self.assertFalse(result)
    
    async def test_close(self):
        """Test the close method."""
        # Test successful close
        await self.connection.close()
        self.mock_session.close.assert_called_once()
    
    async def test_create_level(self):
        """Test the create_level method."""
        self.mock_response.json.return_value = {
            "result": "Level created successfully",
            "error": None
        }
        
        result = await self.connection.create_level("TestLevel")
        self.assertEqual(result, "Level created successfully")
        
        # Check correct arguments were passed
        self.mock_session.post.assert_called_with(
            "http://localhost:8500/execute",
            json={"code": "unreal.EditorLevelLibrary.new_level('TestLevel')"}
        )
    
    async def test_import_asset(self):
        """Test the import_asset method."""
        self.mock_response.json.return_value = {
            "result": "Asset imported successfully",
            "error": None
        }
        
        result = await self.connection.import_asset("/path/to/asset.fbx", "/Game/Assets")
        self.assertEqual(result, "Asset imported successfully")
        
        # Check correct arguments were passed
        self.mock_session.post.assert_called_with(
            "http://localhost:8500/execute",
            json={"code": "unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([unreal.AssetImportTask(filename='/path/to/asset.fbx', destination_path='/Game/Assets')])[0]"}
        )
    
    async def test_get_engine_version(self):
        """Test the get_engine_version method."""
        self.mock_response.json.return_value = {
            "result": "5.0.0",
            "error": None
        }
        
        result = await self.connection.get_engine_version()
        self.assertEqual(result, "5.0.0")
        
        # Check correct arguments were passed
        self.mock_session.post.assert_called_with(
            "http://localhost:8500/execute",
            json={"code": "str(unreal.SystemLibrary.get_engine_version())"}
        )
    
    async def test_execute_code(self):
        """Test the execute_code method."""
        self.mock_response.json.return_value = {
            "result": "Code executed successfully",
            "error": None
        }
        
        result = await self.connection.execute_code("print('Hello')")
        self.assertEqual(result, "Code executed successfully")
        
        # Check correct arguments were passed
        self.mock_session.post.assert_called_with(
            "http://localhost:8500/execute",
            json={"code": "print('Hello')"}
        )
    
    async def test_error_response(self):
        """Test handling of error responses."""
        self.mock_response.json.return_value = {
            "result": None,
            "error": "Error executing code"
        }
        
        result = await self.connection.execute_code("print('Hello')")
        self.assertEqual(result, {"status": "error", "message": "Error executing code"})

if __name__ == "__main__":
    unittest.main() 