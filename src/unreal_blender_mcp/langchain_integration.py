"""
Langchain integration for unreal-blender-mcp.

This module provides integration with Langchain for state management,
memory, and document processing capabilities.
"""

import logging
import os
from typing import Dict, List, Any, Optional, Union

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

logger = logging.getLogger(__name__)

# Default prompt templates
DEFAULT_SYSTEM_TEMPLATE = """
You are an AI assistant that can control both Blender and Unreal Engine through an MCP server.
You have access to the following tools:

BLENDER TOOLS:
{blender_tools}

UNREAL TOOLS:
{unreal_tools}

Use these tools to help the user accomplish their tasks with 3D content creation.
Always respond in a helpful and informative manner.
"""

DEFAULT_TOOL_DESCRIPTION_TEMPLATE = """
{tool_name}:
Description: {description}
Parameters: {parameters}
Example: {example}
"""

class LangchainManager:
    """
    Class for managing Langchain functionality.
    
    Provides document processing, memory management, and prompt generation.
    """
    
    def __init__(self, embeddings_key: Optional[str] = None):
        """
        Initialize the Langchain manager.
        
        Args:
            embeddings_key: Optional OpenAI API key for embeddings. If not provided,
                            will try to use OPENAI_API_KEY from environment variables.
        """
        self.memory = {}
        self.document_store = {}
        self.prompt_templates = {}
        self.conversation_memory = ConversationBufferMemory()
        
        # Initialize embeddings if key is provided or in env vars
        self.embeddings = None
        if embeddings_key or os.environ.get("OPENAI_API_KEY"):
            try:
                if embeddings_key:
                    os.environ["OPENAI_API_KEY"] = embeddings_key
                self.embeddings = OpenAIEmbeddings()
                logger.info("OpenAI embeddings initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI embeddings: {e}")
        
        # Initialize default prompt templates
        self.register_prompt_template("system", DEFAULT_SYSTEM_TEMPLATE)
        self.register_prompt_template("tool_description", DEFAULT_TOOL_DESCRIPTION_TEMPLATE)
        
        logger.info("Initialized Langchain manager with document processing capabilities")
    
    def store_memory(self, key: str, value: Any) -> None:
        """
        Store a value in memory.
        
        Args:
            key: The key to store the value under
            value: The value to store
        """
        self.memory[key] = value
        logger.info(f"Stored value for key: {key}")
    
    def retrieve_memory(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from memory.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value associated with the key, or None if not found
        """
        value = self.memory.get(key)
        if value is None:
            logger.info(f"No value found for key: {key}")
        else:
            logger.info(f"Retrieved value for key: {key}")
        return value
    
    def get_all_memory(self) -> Dict[str, Any]:
        """
        Get all stored memory.
        
        Returns:
            Dict containing all memory key-value pairs
        """
        return self.memory.copy()
    
    def clear_memory(self) -> None:
        """Clear all stored memory."""
        self.memory.clear()
        logger.info("Cleared all memory")
    
    def process_document(self, document_id: str, text: str, chunk_size: int = 1000, 
                        chunk_overlap: int = 200) -> List[Document]:
        """
        Process a document for later retrieval.
        
        Args:
            document_id: Unique identifier for the document
            text: The document text to process
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of processed document chunks
        """
        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        
        # Create Document objects
        docs = [Document(page_content=chunk, metadata={"source": document_id}) for chunk in chunks]
        
        # Store document chunks
        self.document_store[document_id] = docs
        logger.info(f"Processed document {document_id} into {len(docs)} chunks")
        
        return docs
    
    def create_vector_store(self, document_ids: List[str], store_id: str) -> Optional[FAISS]:
        """
        Create a vector store from processed documents.
        
        Args:
            document_ids: List of document IDs to include in the vector store
            store_id: Unique identifier for the vector store
            
        Returns:
            FAISS vector store or None if embeddings are not available
        """
        if not self.embeddings:
            logger.warning("Cannot create vector store: embeddings not initialized")
            return None
        
        # Collect all documents
        all_docs = []
        for doc_id in document_ids:
            if doc_id in self.document_store:
                all_docs.extend(self.document_store[doc_id])
        
        if not all_docs:
            logger.warning(f"No documents found for IDs: {document_ids}")
            return None
        
        # Create vector store
        vector_store = FAISS.from_documents(all_docs, self.embeddings)
        
        # Store for later use
        self.store_memory(f"vector_store_{store_id}", vector_store)
        logger.info(f"Created vector store {store_id} with {len(all_docs)} document chunks")
        
        return vector_store
    
    def query_documents(self, query: str, store_id: str, k: int = 5) -> List[Document]:
        """
        Query the vector store for relevant documents.
        
        Args:
            query: The search query
            store_id: ID of the vector store to search
            k: Number of results to return
            
        Returns:
            List of relevant document chunks
        """
        vector_store = self.retrieve_memory(f"vector_store_{store_id}")
        if not vector_store:
            logger.warning(f"Vector store {store_id} not found")
            return []
        
        results = vector_store.similarity_search(query, k=k)
        logger.info(f"Query returned {len(results)} results from vector store {store_id}")
        
        return results
    
    def register_prompt_template(self, template_id: str, template_text: str) -> None:
        """
        Register a prompt template for later use.
        
        Args:
            template_id: Unique identifier for the template
            template_text: The template text with placeholders
        """
        try:
            prompt_template = PromptTemplate.from_template(template_text)
            self.prompt_templates[template_id] = prompt_template
            logger.info(f"Registered prompt template: {template_id}")
        except Exception as e:
            logger.error(f"Failed to register prompt template {template_id}: {e}")
    
    def generate_prompt(self, template_id: str = None, template: str = None, **kwargs) -> str:
        """
        Generate a prompt from a template.
        
        Args:
            template_id: ID of a registered template to use
            template: Raw template string (used if template_id is None)
            **kwargs: Values to substitute in the template
            
        Returns:
            The formatted prompt
        """
        if template_id and template_id in self.prompt_templates:
            return self.prompt_templates[template_id].format(**kwargs)
        elif template:
            return template.format(**kwargs)
        else:
            logger.warning(f"Template ID {template_id} not found and no raw template provided")
            return ""
    
    def format_tool_descriptions(self, tools: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Format tool descriptions for AI agent prompts.
        
        Args:
            tools: List of tool definitions
            
        Returns:
            Dictionary with formatted tool descriptions grouped by category
        """
        result = {"blender_tools": "", "unreal_tools": ""}
        
        for tool in tools:
            category = "blender_tools" if tool.get("category") == "blender" else "unreal_tools"
            description = self.generate_prompt(
                template_id="tool_description",
                tool_name=tool.get("name", ""),
                description=tool.get("description", ""),
                parameters=tool.get("parameters", ""),
                example=tool.get("example", "")
            )
            result[category] += description + "\n"
        
        return result
    
    def add_message_to_conversation(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: The role of the message sender (user, assistant, system)
            content: The message content
        """
        if role == "user":
            self.conversation_memory.chat_memory.add_user_message(content)
        elif role == "assistant":
            self.conversation_memory.chat_memory.add_ai_message(content)
        elif role == "system":
            # Store system message separately as it's handled differently
            self.store_memory("system_message", content)
        
        logger.info(f"Added {role} message to conversation history")
    
    def get_conversation_history(self) -> str:
        """
        Get the conversation history as a formatted string.
        
        Returns:
            Conversation history string
        """
        return self.conversation_memory.buffer 