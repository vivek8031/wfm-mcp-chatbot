# chat_handler.py - WFM Database Assistant with Anthropic Claude
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from anthropic import Anthropic
from mcp_connection_manager import MCPConnectionManager
import os
from datetime import datetime

class WFMChatHandler:
    """Workforce Management Database Chat Handler using Anthropic Claude"""
    
    def __init__(self, mcp_manager: MCPConnectionManager = None, model: str = "claude-3-5-sonnet-20241022"):
        self.model = model
        
        # Initialize Anthropic client
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Use provided MCP manager or create singleton
        self.mcp_client = mcp_manager or MCPConnectionManager()
        
        self.conversation_history: List[Dict[str, str]] = []
        self.logger = logging.getLogger(__name__)
        self.mcp_connected = False
        
        # WFM specific collections
        self.wfm_collections = {
            "master_data": [
                "employees", "activities", "activityTypes", 
                "paycodes", "itms_wfm_roles", "ITMS_HOLIDAYS_LIST"
            ],
            "transactional_data": [
                "dailyActivities", "itms_wfm_payroll", "itms_wfm_user_roles"
            ]
        }
        
    async def initialize(self):
        """Initialize the chat handler - MCP connection should already be established"""
        self.mcp_connected = self.mcp_client.is_connected()
        if self.mcp_connected:
            self.logger.info("✅ Chat handler initialized with MCP connection")
        else:
            self.logger.error("❌ Chat handler initialization failed - no MCP connection")
        return self.mcp_connected
    
    def _build_wfm_system_prompt(self) -> str:
        """Build WFM-specific system prompt with database context"""
        tools_info = ""
        if self.mcp_connected:
            tools = self.mcp_client.get_available_tools()
            tools_info = f"Available MongoDB tools: {[tool['name'] for tool in tools]}"
        
        return f"""You are a Workforce Management Database Assistant with expertise in HR analytics and workforce data. You have access to a MongoDB database called 'wfm_database' containing 9 collections of workforce data.

DATABASE STRUCTURE:
MASTER DATA (6 collections):
• employees: Employee records with badges, names, contact info, employment history, addresses
• activities: Work activity definitions and descriptions  
• activityTypes: Categories and types of work activities
• paycodes: Payroll codes and compensation rules
• itms_wfm_roles: User roles and permissions in the WFM system
• ITMS_HOLIDAYS_LIST: Holiday schedules with HOL_DATE (Date field), HOL_DESC (description), and NAME fields

TRANSACTIONAL DATA (3 collections):
• dailyActivities: Daily work activity tracking, time logs, and employee assignments
• itms_wfm_payroll: Payroll records with hours worked, dates, counties, and employee details
• itms_wfm_user_roles: User role assignments and access permissions

{tools_info}

EXPERTISE AREAS:
- Workforce analytics and reporting
- Payroll analysis and time tracking
- Employee management and HR insights
- Activity scheduling and productivity analysis
- Holiday planning and workforce coverage
- Role-based access and permissions

QUERY GUIDELINES:
1. Always use the appropriate MongoDB tools to fetch real data from the wfm_database
2. For holidays: Use collection "ITMS_HOLIDAYS_LIST" with field "HOL_DATE" for date queries
3. When analyzing payroll data, focus on hours, counties, dates, and trends
4. For employee queries, consider badge IDs, names, employment types, and locations
5. Use "query" parameter (not "filter") for MongoDB find operations
6. For date comparisons, use MongoDB Extended JSON format: {{"$date": "2025-07-26T00:00:00Z"}}
7. Format results clearly for HR and management stakeholders
8. Provide actionable insights and summaries when appropriate
9. Handle dates and time ranges intelligently
10. Suggest follow-up questions or related analyses

Current time: {datetime.now().isoformat()}
Database: wfm_database (9 collections: 6 master, 3 transactional)
"""
    
    async def _call_claude_with_tools(self, messages: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, Any]]]:
        """Call Anthropic Claude with tool calling capability"""
        
        if not self.mcp_connected:
            return "Sorry, I'm not connected to the WFM database right now. Please try again later.", []
        
        tools = self.mcp_client.get_available_tools()
        
        # Convert tools to Anthropic format
        formatted_tools = []
        for tool in tools:
            formatted_tools.append({
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["parameters"]
            })
        
        try:
            response = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=self._build_wfm_system_prompt(),
                messages=messages,
                tools=formatted_tools,
                tool_choice={"type": "auto"}
            )
            
            # Extract content and tool calls from Anthropic response
            content = ""
            tool_calls = []
            
            for content_block in response.content:
                if content_block.type == "text":
                    content += content_block.text
                elif content_block.type == "tool_use":
                    tool_calls.append({
                        "id": content_block.id,
                        "name": content_block.name,
                        "input": content_block.input
                    })
            
            return content, tool_calls
        
        except Exception as e:
            self.logger.error(f"Claude API call failed: {e}")
            return f"Sorry, I encountered an error connecting to Claude: {str(e)}", []
    
    async def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute the tool calls and return results"""
        results = []
        
        for tool_call in tool_calls:
            try:
                # Anthropic format
                tool_name = tool_call.get('name')
                arguments = tool_call.get('input', {})
                call_id = tool_call.get('id', f"call_{len(results)}")
                
                self.logger.info(f"Executing tool: {tool_name} with args: {arguments}")
                
                # Execute the tool via MCP
                result = await self.mcp_client.execute_tool(tool_name, arguments)
                
                results.append({
                    "tool_call_id": call_id,
                    "tool_name": tool_name,
                    "result": result
                })
                
            except Exception as e:
                self.logger.error(f"Tool execution failed for {tool_name}: {e}")
                results.append({
                    "tool_call_id": call_id,
                    "tool_name": tool_name,
                    "error": str(e)
                })
        
        return results
    
    async def process_message(self, user_message: str) -> str:
        """Process user message and return response with WFM context"""
        max_turns = 10  # Limit conversation turns to prevent infinite loops
        current_turn = 0
        
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            
            messages = self.conversation_history.copy()
            
            while current_turn < max_turns:
                current_turn += 1
                self.logger.info(f"Conversation turn {current_turn}/{max_turns}")
                
                # Get Claude response with potential tool calls
                claude_response, tool_calls = await self._call_claude_with_tools(messages)
                
                if not tool_calls:
                    # No tool calls, return final response
                    self.logger.info(f"Final response after {current_turn} turns")
                    response = claude_response
                    break
                
                # Execute tool calls
                self.logger.info(f"Executing {len(tool_calls)} tool calls in turn {current_turn}")
                tool_results = await self._execute_tool_calls(tool_calls)
                
                # Prepare tool result content
                tool_result_content = []
                for result in tool_results:
                    if "error" in result:
                        tool_result_content.append({
                            "type": "tool_result",
                            "tool_use_id": result["tool_call_id"],
                            "content": f"Error: {result['error']}"
                        })
                    else:
                        content_str = self._extract_text_from_mcp_result(result["result"])
                        tool_result_content.append({
                            "type": "tool_result", 
                            "tool_use_id": result["tool_call_id"],
                            "content": content_str
                        })
                
                # Add assistant message with tool calls to conversation
                assistant_content = []
                if claude_response:
                    assistant_content.append({"type": "text", "text": claude_response})
                for tool_call in tool_calls:
                    assistant_content.append({
                        "type": "tool_use",
                        "id": tool_call["id"],
                        "name": tool_call["name"],
                        "input": tool_call["input"]
                    })
                
                messages.append({
                    "role": "assistant",
                    "content": assistant_content
                })
                
                # Add user message with tool results
                messages.append({
                    "role": "user",
                    "content": tool_result_content
                })
                
            else:
                # Reached max turns limit
                self.logger.warning(f"Reached maximum conversation turns ({max_turns})")
                response = claude_response + f"\n\n[Note: Reached maximum interaction limit of {max_turns} turns. Response may be incomplete.]"
            
            # Add final assistant response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Keep conversation history manageable (last 10 exchanges)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return response
            
        except Exception as e:
            self.logger.error(f"Message processing failed: {e}")
            return f"I encountered an error while processing your WFM query: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
    
    def _extract_text_from_mcp_result(self, result) -> str:
        """Extract text content from MCP result for Claude"""
        if isinstance(result, list):
            text_parts = []
            for item in result:
                if hasattr(item, 'type') and hasattr(item, 'text'):
                    # This is a TextContent object
                    text_parts.append(item.text)
                elif hasattr(item, '__dict__'):
                    # Convert object to string representation
                    text_parts.append(json.dumps(vars(item), indent=2))
                else:
                    # Primitive type
                    text_parts.append(str(item))
            return "\n".join(text_parts)
        elif hasattr(result, 'type') and hasattr(result, 'text'):
            # Single TextContent object
            return result.text
        elif hasattr(result, '__dict__'):
            # Convert object to JSON string
            return json.dumps(vars(result), indent=2)
        else:
            # Convert to string
            return str(result)
    
    def _serialize_mcp_result(self, result) -> Any:
        """Convert MCP result objects to JSON-serializable format"""
        if isinstance(result, list):
            serialized_items = []
            for item in result:
                if hasattr(item, 'type') and hasattr(item, 'text'):
                    # This is a TextContent object
                    serialized_items.append({
                        "type": item.type,
                        "text": item.text
                    })
                elif hasattr(item, '__dict__'):
                    # Convert object to dict
                    serialized_items.append(vars(item))
                else:
                    # Primitive type
                    serialized_items.append(item)
            return serialized_items
        elif hasattr(result, 'type') and hasattr(result, 'text'):
            # Single TextContent object
            return {
                "type": result.type,
                "text": result.text
            }
        elif hasattr(result, '__dict__'):
            # Convert object to dict
            return vars(result)
        else:
            # Already serializable
            return result
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the database connection and return status"""
        if not self.mcp_client.is_connected():
            return {"status": "disconnected", "error": "MCP client not connected"}
        
        try:
            result = await self.mcp_client.list_databases()
            return {
                "status": "connected",
                "databases": result.get("result", []),
                "tools_available": len(self.mcp_client.get_available_tools())
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Example usage
async def test_wfm_chat_handler():
    """Test the WFM chat handler"""
    handler = WFMChatHandler()
    
    if await handler.initialize():
        print("✅ WFM Chat handler initialized")
        
        # Test connection
        status = await handler.test_connection()
        print(f"📊 Connection status: {status}")
        
        # Test WFM-specific queries
        test_queries = [
            "What collections do we have in the WFM database?",
            "Show me a sample employee record",
            "How many payroll records do we have?"
        ]
        
        for query in test_queries:
            print(f"\n🤔 Query: {query}")
            response = await handler.process_message(query)
            print(f"🤖 Response: {response}")
    
    else:
        print("❌ Failed to initialize WFM chat handler")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run test
    asyncio.run(test_wfm_chat_handler())