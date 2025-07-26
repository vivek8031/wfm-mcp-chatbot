#!/usr/bin/env python3
"""
Proper MCP Connection Manager following SDK documentation patterns
Uses FastAPI lifespan for connection management
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any]

class MCPConnectionManager:
    """
    Proper MCP Connection Manager using FastAPI lifespan patterns
    Following MCP Python SDK documentation best practices
    """
    
    def __init__(self):
        self.connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/wfm_database")
        self.session: Optional[ClientSession] = None
        self.available_tools: List[MCPTool] = []
        self.logger = logging.getLogger(__name__)
        self._exit_stack = AsyncExitStack()
        self._connected = False
        
    async def initialize(self) -> bool:
        """
        Initialize MCP connection using proper async context patterns
        Following the documentation: async with stdio_client() as (read, write):
        """
        try:
            self.logger.info("🔌 Initializing MCP connection...")
            
            # Create server parameters following documentation pattern
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "mongodb-mcp-server", "--connectionString", self.connection_string],
                env=os.environ.copy()
            )
            
            # Use proper async context manager pattern from documentation
            # This will be kept alive by the exit stack
            stdio_transport = await self._exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read_stream, write_stream = stdio_transport
            
            # Create session using proper context pattern
            self.session = await self._exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            # Initialize the session
            await self.session.initialize()
            
            # Load available tools
            await self._load_tools()
            
            self._connected = True
            self.logger.info(f"✅ MCP connection established with {len(self.available_tools)} tools")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize MCP connection: {e}")
            await self._cleanup()
            return False
    
    async def _load_tools(self):
        """Load available tools from the MCP server"""
        try:
            if not self.session:
                raise Exception("MCP session not available")
            
            tools_response = await self.session.list_tools()
            
            self.available_tools = [
                MCPTool(
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.inputSchema
                )
                for tool in tools_response.tools
            ]
            
            self.logger.info(f"📋 Loaded {len(self.available_tools)} MCP tools")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load tools: {e}")
            raise
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool with proper error handling"""
        if not self._connected or not self.session:
            return {
                "success": False,
                "error": "MCP connection not available",
                "tool_name": tool_name
            }
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            
            return {
                "success": True,
                "result": result.content,
                "tool_name": tool_name
            }
            
        except Exception as e:
            self.logger.error(f"❌ Tool execution failed for {tool_name}: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools for LLM function calling"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema
            }
            for tool in self.available_tools
        ]
    
    def is_connected(self) -> bool:
        """Simple connection state check - no recursive tool calls"""
        return self._connected and self.session is not None
    
    async def cleanup(self):
        """Cleanup connections and resources"""
        self.logger.info("🔄 Cleaning up MCP connection...")
        self._connected = False
        
        try:
            # Use exit stack to properly cleanup all resources
            await self._exit_stack.aclose()
        except Exception as e:
            self.logger.warning(f"⚠️ Cleanup warning: {e}")
        
        self.session = None
        self.available_tools = []
        
        self.logger.info("✅ MCP cleanup complete")
    
    async def _cleanup(self):
        """Internal cleanup method"""
        await self.cleanup()
    
    # Convenience methods for common operations
    async def find_documents(self, collection: str, query: Dict[str, Any], database: str = None) -> Dict[str, Any]:
        """Convenience method for finding documents"""
        arguments = {
            "collection": collection,
            "query": query
        }
        if database:
            arguments["database"] = database
            
        return await self.execute_tool("find", arguments)
    
    async def aggregate_documents(self, collection: str, pipeline: List[Dict[str, Any]], database: str = None) -> Dict[str, Any]:
        """Convenience method for aggregation"""
        arguments = {
            "collection": collection,
            "pipeline": pipeline
        }
        if database:
            arguments["database"] = database
            
        return await self.execute_tool("aggregate", arguments)
    
    async def list_databases(self) -> Dict[str, Any]:
        """List all databases"""
        return await self.execute_tool("list-databases", {})
    
    async def list_collections(self, database: str) -> Dict[str, Any]:
        """List collections in a database"""
        return await self.execute_tool("list-collections", {"database": database})
    
    async def get_collection_schema(self, collection: str, database: str = None) -> Dict[str, Any]:
        """Get schema for a collection"""
        arguments = {"collection": collection}
        if database:
            arguments["database"] = database
        return await self.execute_tool("collection-schema", arguments)