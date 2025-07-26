# mcp_client.py
import asyncio
import json
import subprocess
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any]

class MongoMCPClient:
    def __init__(self, connection_string: str = None, atlas_client_id: str = None, atlas_client_secret: str = None):
        self.connection_string = connection_string
        self.atlas_client_id = atlas_client_id
        self.atlas_client_secret = atlas_client_secret
        self.session: Optional[ClientSession] = None
        self.available_tools: List[MCPTool] = []
        self.logger = logging.getLogger(__name__)
        
    async def connect(self):
        """Initialize connection to MongoDB MCP Server"""
        try:
            # Build server arguments
            server_args = [
                "npx", "-y", "mongodb-mcp-server"
            ]
            
            if self.connection_string:
                server_args.extend(["--connectionString", self.connection_string])
            
            if self.atlas_client_id and self.atlas_client_secret:
                server_args.extend([
                    "--apiClientId", self.atlas_client_id,
                    "--apiClientSecret", self.atlas_client_secret
                ])
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=server_args[0],
                args=server_args[1:],
                env=os.environ.copy()
            )
            
            # Connect to MCP server
            async with stdio_client(server_params) as (read, write):
                self.session = ClientSession(read, write)
                
                # Initialize the session
                await self.session.initialize()
                
                # Get available tools
                await self._load_tools()
                
                self.logger.info(f"Connected to MongoDB MCP Server with {len(self.available_tools)} tools")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server: {e}")
            return False
    
    async def _load_tools(self):
        """Load available tools from the MCP server"""
        try:
            # List available tools
            tools_response = await self.session.list_tools()
            
            self.available_tools = [
                MCPTool(
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.inputSchema
                )
                for tool in tools_response.tools
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to load tools: {e}")
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific MCP tool"""
        try:
            if not self.session:
                raise Exception("MCP session not initialized")
            
            # Call the tool
            result = await self.session.call_tool(tool_name, arguments)
            
            return {
                "success": True,
                "result": result.content,
                "tool_name": tool_name
            }
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
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
    
    async def insert_document(self, collection: str, document: Dict[str, Any], database: str = None) -> Dict[str, Any]:
        """Convenience method for inserting documents"""
        arguments = {
            "collection": collection,
            "document": document
        }
        if database:
            arguments["database"] = database
            
        return await self.execute_tool("insert-one", arguments)
    
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

# Example usage and testing
async def test_mcp_client():
    """Test the MCP client functionality"""
    # Initialize client
    client = MongoMCPClient(
        connection_string=os.getenv("MONGODB_CONNECTION_STRING"),
        atlas_client_id=os.getenv("ATLAS_CLIENT_ID"),
        atlas_client_secret=os.getenv("ATLAS_CLIENT_SECRET")
    )
    
    # Connect
    if await client.connect():
        print("✅ Connected to MongoDB MCP Server")
        
        # List available tools
        tools = client.get_available_tools()
        print(f"📋 Available tools: {[tool['name'] for tool in tools]}")
        
        # Test database listing
        databases = await client.list_databases()
        print(f"🗄️ Databases: {databases}")
        
    else:
        print("❌ Failed to connect to MCP server")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run test
    asyncio.run(test_mcp_client())