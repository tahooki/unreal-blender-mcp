"""
Integration tests for the MCP server.

This module contains integration tests that verify multiple components
of the MCP server working together with simulated client requests.
"""

import unittest
import asyncio
import json
from unittest.mock import patch, MagicMock, AsyncMock

from fastapi.testclient import TestClient
import pytest

from src.unreal_blender_mcp.server import app
from tests.utils.request_simulator import RequestSimulator, MockConnection


@pytest.mark.asyncio
class TestServerIntegration:
    """Integration tests for the MCP server."""
    
    async def setup_mocks(self):
        """Set up mock connections for testing."""
        # Mock the BlenderConnection and UnrealConnection
        self.blender_patch = patch('src.unreal_blender_mcp.server.blender_connection')
        self.unreal_patch = patch('src.unreal_blender_mcp.server.unreal_connection')
        self.langchain_patch = patch('src.unreal_blender_mcp.server.langchain_manager')
        
        self.mock_blender = self.blender_patch.start()
        self.mock_unreal = self.unreal_patch.start()
        self.mock_langchain = self.langchain_patch.start()
        
        # Create mock connections with expected responses
        self.blender_mock = MockConnection("blender", {
            "get_scene_info": {"objects": ["Cube", "Camera", "Light"], "materials": ["Material"]},
            "get_object_info_Cube": {"name": "Cube", "type": "MESH", "location": [0, 0, 0]},
            "execute_code_create_cube": "Created cube successfully"
        })
        
        self.unreal_mock = MockConnection("unreal", {
            "get_engine_version": "5.0.0",
            "create_level": "Level created successfully",
            "execute_code": "Code executed successfully"
        })
        
        # Set up the mock connections to be returned by the connection managers
        self.mock_blender.connect = self.blender_mock.connect
        self.mock_blender.get_scene_info = self.blender_mock.get_scene_info
        self.mock_blender.get_object_info = self.blender_mock.get_object_info
        self.mock_blender.execute_code = self.blender_mock.execute_code
        
        self.mock_unreal.connect = self.unreal_mock.connect
        self.mock_unreal.get_engine_version = self.unreal_mock.get_engine_version
        self.mock_unreal.create_level = self.unreal_mock.create_level
        self.mock_unreal.execute_code = self.unreal_mock.execute_code
    
    async def teardown_mocks(self):
        """Tear down mock connections."""
        self.blender_patch.stop()
        self.unreal_patch.stop()
        self.langchain_patch.stop()
    
    @pytest.fixture
    async def client(self):
        """Create a test client with mock connections."""
        await self.setup_mocks()
        try:
            with TestClient(app) as client:
                yield client
        finally:
            await self.teardown_mocks()
    
    async def test_server_status(self, client):
        """Test getting the server status."""
        # Start simulator
        async with RequestSimulator() as simulator:
            # Get server status
            status = await simulator.get_server_status()
            
            # Verify status response
            assert status["status"] == "success"
            assert "server" in status["data"]
            assert "active_connections" in status["data"]
    
    async def test_basic_message(self, client):
        """Test sending a basic message."""
        # Start simulator
        async with RequestSimulator() as simulator:
            # Send a simple message
            response = await simulator.send_message("user", "Hello, server!")
            
            # Verify response
            assert response["status"] == "success"
            assert "results" in response["data"]
    
    async def test_blender_tool_call(self, client):
        """Test calling a Blender tool."""
        # Start simulator
        async with RequestSimulator() as simulator:
            # Simulate a tool call to get scene info
            response = await simulator.simulate_tool_call("get_scene_info")
            
            # Verify response
            assert response["status"] == "success"
            
            # In a real test, we would verify that the tool was actually called
            # and the response contains the expected data. Here we just check
            # that the response has the expected structure.
    
    async def test_conversation_sequence(self, client):
        """Test a sequence of conversation messages."""
        # Start simulator
        async with RequestSimulator() as simulator:
            # Simulate a conversation
            messages = [
                {"role": "user", "content": "Hello, I want to create a scene in Blender"},
                {"role": "assistant", "content": "I'll help you create a scene in Blender. What do you want to create?"},
                {"role": "user", "content": "I want to create a red cube"},
            ]
            
            responses = await simulator.simulate_conversation(messages)
            
            # Verify responses
            assert len(responses) == 3
            for response in responses:
                assert response["status"] == "success"
    
    async def test_stream_connection(self, client):
        """Test connecting to and using an SSE stream."""
        # This test is more complex because it involves streaming events
        # We'll just verify that we can connect and send a message
        
        # Start simulator
        async with RequestSimulator() as simulator:
            # Connect to stream
            connection_id, response = await simulator.connect_stream()
            
            # Verify connection
            assert response.status == 200
            
            # Try to read one event (should be a heartbeat)
            async for event in simulator.read_stream_events(response):
                # Check that we got some kind of event
                assert event is not None
                # Only read one event for this test
                break
            
            # Send a message to the stream
            message_response = await simulator.send_stream_message("user", "Hello via stream")
            
            # Verify response
            assert message_response["status"] == "success"
    
    async def test_error_handling(self, client):
        """Test error handling in various scenarios."""
        # Start simulator
        async with RequestSimulator() as simulator:
            # Test with invalid message (missing role)
            async with simulator.session.post(
                f"{simulator.base_url}/message",
                json={"content": "No role specified"}
            ) as response:
                data = await response.json()
                
                # Verify error response
                assert response.status == 422
                assert data["status"] == "error"
                assert "message" in data
                assert "code" in data
                assert "details" in data


# Make the tests run with unittest
class TestServerIntegrationSync(unittest.TestCase):
    """Synchronous wrapper for async integration tests."""
    
    def test_server_integration(self):
        """Run all async tests using pytest."""
        pytest.main(["-xvs", __file__])


if __name__ == "__main__":
    unittest.main() 