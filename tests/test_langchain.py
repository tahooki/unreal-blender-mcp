"""
Tests for Langchain integration.

This module contains tests for the Langchain integration functionality,
including document processing, memory management, and prompt generation.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from src.unreal_blender_mcp.langchain_integration import LangchainManager

class TestLangchainManager(unittest.TestCase):
    """Test the LangchainManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize with a mock embeddings key
        with patch('os.environ.get', return_value=None):
            with patch('src.unreal_blender_mcp.langchain_integration.OpenAIEmbeddings') as mock_embeddings:
                mock_embeddings.return_value = MagicMock()
                self.manager = LangchainManager(embeddings_key="fake_key")
    
    def test_memory_management(self):
        """Test basic memory management functionality."""
        # Test storing and retrieving values
        self.manager.store_memory("test_key", "test_value")
        self.assertEqual(self.manager.retrieve_memory("test_key"), "test_value")
        
        # Test retrieving non-existent key
        self.assertIsNone(self.manager.retrieve_memory("non_existent_key"))
        
        # Test get_all_memory
        self.assertEqual(self.manager.get_all_memory(), {"test_key": "test_value"})
        
        # Test clear_memory
        self.manager.clear_memory()
        self.assertEqual(self.manager.get_all_memory(), {})
    
    def test_prompt_templates(self):
        """Test prompt template registration and generation."""
        # Test registering a new template
        self.manager.register_prompt_template("test_template", "Hello, {name}!")
        
        # Test generating from registered template
        result = self.manager.generate_prompt(template_id="test_template", name="World")
        self.assertEqual(result, "Hello, World!")
        
        # Test generating from raw template
        result = self.manager.generate_prompt(template="Goodbye, {name}!", name="World")
        self.assertEqual(result, "Goodbye, World!")
        
        # Test with non-existent template ID
        result = self.manager.generate_prompt(template_id="non_existent")
        self.assertEqual(result, "")
    
    @patch('src.unreal_blender_mcp.langchain_integration.RecursiveCharacterTextSplitter')
    def test_document_processing(self, mock_splitter):
        """Test document processing functionality."""
        # Mock the text splitter
        mock_splitter_instance = MagicMock()
        mock_splitter.return_value = mock_splitter_instance
        mock_splitter_instance.split_text.return_value = ["chunk1", "chunk2"]
        
        # Test processing a document
        result = self.manager.process_document("test_doc", "Test document content")
        
        # Assert the document was split
        mock_splitter_instance.split_text.assert_called_once_with("Test document content")
        
        # Assert the chunks were stored
        self.assertEqual(len(result), 2)
        self.assertEqual(len(self.manager.document_store["test_doc"]), 2)
        self.assertEqual(self.manager.document_store["test_doc"][0].page_content, "chunk1")
        self.assertEqual(self.manager.document_store["test_doc"][1].page_content, "chunk2")
    
    @patch('src.unreal_blender_mcp.langchain_integration.FAISS')
    def test_vector_store(self, mock_faiss):
        """Test vector store creation and querying."""
        # Setup document store with mock documents
        self.manager.document_store = {
            "doc1": [MagicMock(), MagicMock()],
            "doc2": [MagicMock(), MagicMock()]
        }
        
        # Mock FAISS.from_documents
        mock_vs = MagicMock()
        mock_faiss.from_documents.return_value = mock_vs
        
        # Test creating a vector store
        result = self.manager.create_vector_store(["doc1", "doc2"], "test_store")
        
        # Assert FAISS was called correctly
        mock_faiss.from_documents.assert_called_once()
        self.assertEqual(result, mock_vs)
        
        # Test querying the vector store
        mock_results = [MagicMock(), MagicMock()]
        mock_vs.similarity_search.return_value = mock_results
        
        # Store the vector store in memory
        self.manager.store_memory("vector_store_test_store", mock_vs)
        
        # Query the vector store
        results = self.manager.query_documents("test query", "test_store")
        
        # Assert the query was performed correctly
        mock_vs.similarity_search.assert_called_once_with("test query", k=5)
        self.assertEqual(results, mock_results)
    
    def test_conversation_management(self):
        """Test conversation management functionality."""
        # Test adding different message types
        self.manager.add_message_to_conversation("user", "Hello")
        self.manager.add_message_to_conversation("assistant", "Hi there")
        self.manager.add_message_to_conversation("system", "System message")
        
        # Check system message is stored separately
        self.assertEqual(self.manager.retrieve_memory("system_message"), "System message")
        
        # Test conversation history
        history = self.manager.get_conversation_history()
        self.assertIn("Hello", history)
        self.assertIn("Hi there", history)
    
    def test_tool_description_formatting(self):
        """Test tool description formatting for AI prompts."""
        tools = [
            {
                "name": "tool1",
                "category": "blender",
                "description": "A Blender tool",
                "parameters": "param1, param2",
                "example": "tool1(param1=1, param2=2)"
            },
            {
                "name": "tool2",
                "category": "unreal",
                "description": "An Unreal tool",
                "parameters": "param1",
                "example": "tool2(param1=1)"
            }
        ]
        
        result = self.manager.format_tool_descriptions(tools)
        
        self.assertIn("blender_tools", result)
        self.assertIn("unreal_tools", result)
        self.assertIn("tool1", result["blender_tools"])
        self.assertIn("tool2", result["unreal_tools"])

if __name__ == "__main__":
    unittest.main() 