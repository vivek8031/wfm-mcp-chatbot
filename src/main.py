#!/usr/bin/env python3
"""
FastAPI WFM Database Assistant
Clean architecture with proper MCP connection management
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import sys
import os
sys.path.append(os.path.dirname(__file__))

from chat_handler import WFMChatHandler
from collection_manager import WFMCollectionManager
from mcp_connection_manager import MCPConnectionManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection manager - proper lifespan management
mcp_manager: Optional[MCPConnectionManager] = None
chat_handler: Optional[WFMChatHandler] = None 
collection_manager: Optional[WFMCollectionManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan following MCP SDK documentation patterns"""
    global mcp_manager, chat_handler, collection_manager
    
    logger.info("🚀 Starting WFM Database Assistant...")
    
    try:
        # Initialize MCP connection manager using proper patterns
        mcp_manager = MCPConnectionManager()
        
        # Initialize MCP connection - this now uses proper async context management
        success = await mcp_manager.initialize()
        if not success:
            raise Exception("Failed to establish MCP connection")
        
        # Initialize chat handler and collection manager with the connected MCP manager
        chat_handler = WFMChatHandler(mcp_manager)
        collection_manager = WFMCollectionManager(mcp_manager)
        
        # These should be quick since MCP connection is already established
        await chat_handler.initialize()
        await collection_manager.initialize()
        
        logger.info("✅ WFM Database Assistant initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize WFM system: {e}")
        # Cleanup on error
        if mcp_manager:
            try:
                await mcp_manager.cleanup()
            except Exception as cleanup_error:
                logger.error(f"Cleanup error: {cleanup_error}")
        raise
    finally:
        # Cleanup on shutdown
        logger.info("🔄 Shutting down WFM Database Assistant...")
        if mcp_manager:
            await mcp_manager.cleanup()
        logger.info("✅ Cleanup complete")

# Create FastAPI app with lifespan management
app = FastAPI(
    title="WFM Database Assistant",
    description="Workforce Management Database Assistant with Claude AI",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: datetime

class EmployeeSearchRequest(BaseModel):
    name: Optional[str] = None
    badge_id: Optional[str] = None
    limit: int = 20

class PayrollAnalysisRequest(BaseModel):
    county: Optional[str] = None
    days_back: int = 30

class HolidayRequest(BaseModel):
    days_ahead: int = 90

# Root endpoint - serve HTML frontend
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML frontend"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WFM Database Assistant</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { background: linear-gradient(90deg, #1f4e79, #2e86c1); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .status { padding: 10px; border-radius: 4px; margin-bottom: 20px; }
            .status.connected { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .chat-container { display: flex; gap: 20px; }
            .chat-box { flex: 2; }
            .sidebar { flex: 1; background: #f8f9fa; padding: 15px; border-radius: 8px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
            .user-message { background: #e3f2fd; text-align: right; }
            .assistant-message { background: #f1f8e9; }
            .message h1, .message h2, .message h3 { margin-top: 0; color: #2e86c1; }
            .message ul, .message ol { margin: 10px 0; padding-left: 20px; }
            .message li { margin: 5px 0; }
            .message code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
            .message pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .message strong { color: #1f4e79; }
            .loading-message { background: #fff3cd; border-left: 4px solid #ffc107; }
            .loading-dots::after { content: '...'; animation: loading 1.5s infinite; }
            @keyframes loading { 0%, 20% { opacity: 0; } 50% { opacity: 1; } 100% { opacity: 0; } }
            .input-group { display: flex; gap: 10px; margin-top: 20px; }
            .input-group input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            .btn { padding: 10px 20px; background: #2e86c1; color: white; border: none; border-radius: 4px; cursor: pointer; }
            .btn:hover { background: #1f4e79; }
            .btn.secondary { background: #6c757d; }
            .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .metric-card { background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #2e86c1; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .quick-queries { margin-top: 20px; }
            .quick-queries button { margin: 5px; padding: 8px 12px; background: #e9ecef; border: 1px solid #ced4da; border-radius: 4px; cursor: pointer; }
            .loading { color: #666; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>👥 Workforce Management Database Assistant</h1>
                <p>Intelligent analysis of your WFM data with Claude AI • 9 Collections • FastAPI Backend</p>
            </div>
            
            <div id="status" class="status">🔄 Connecting to WFM Database...</div>
            
            <div class="chat-container">
                <div class="chat-box">
                    <h2>💬 Chat with your WFM Database</h2>
                    <div id="messages" style="height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; border-radius: 8px; background: #fafafa;">
                        <div class="message assistant-message">
                            <strong>Assistant:</strong> Hello! I'm your WFM Database Assistant. I can help you analyze employee data, payroll records, activities, and holidays. What would you like to know?
                        </div>
                    </div>
                    <div class="input-group">
                        <input type="text" id="messageInput" placeholder="Ask me anything about your WFM data..." onkeypress="handleKeyPress(event)">
                        <button class="btn" onclick="sendMessage()">Send</button>
                    </div>
                </div>
                
                <div class="sidebar">
                    <h3>📊 Database Overview</h3>
                    <div id="overview" class="loading">Loading...</div>
                    
                    <div class="quick-queries">
                        <h4>⚡ Quick Queries</h4>
                        <button onclick="quickQuery('Show all collections')">Show Collections</button>
                        <button onclick="quickQuery('Employee count by type')">Employee Types</button>
                        <button onclick="quickQuery('Top 5 counties by hours')">Top Counties</button>
                        <button onclick="quickQuery('Recent payroll entries')">Recent Payroll</button>
                        <button onclick="quickQuery('Upcoming holidays')">Upcoming Holidays</button>
                        
                        <h4>💡 Try asking:</h4>
                        <button onclick="quickQuery('Find employees from East Krista county')">East Krista Employees</button>
                        <button onclick="quickQuery('Show payroll trends by county')">Payroll Trends</button>
                        <button onclick="quickQuery('Generate workforce report')">Workforce Report</button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let conversationId = null;

            async function checkStatus() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    const statusEl = document.getElementById('status');
                    
                    if (data.status === 'healthy') {
                        statusEl.className = 'status connected';
                        statusEl.innerHTML = '✅ Connected to WFM Database';
                        loadOverview();
                    } else {
                        statusEl.className = 'status error';
                        statusEl.innerHTML = `❌ Connection Error: ${data.error || 'Unknown error'}`;
                    }
                } catch (error) {
                    document.getElementById('status').innerHTML = `❌ Cannot connect to API: ${error.message}`;
                    document.getElementById('status').className = 'status error';
                }
            }

            async function loadOverview() {
                try {
                    const response = await fetch('/collections');
                    const data = await response.json();
                    
                    if (data.success) {
                        const overviewEl = document.getElementById('overview');
                        overviewEl.innerHTML = `
                            <div class="metrics">
                                <div class="metric-card">
                                    <h4>Total Collections</h4>
                                    <h2>${data.summary.total_collections}</h2>
                                </div>
                                <div class="metric-card">
                                    <h4>Total Records</h4>
                                    <h2>${data.summary.total_documents}</h2>
                                </div>
                                <div class="metric-card">
                                    <h4>Master Data</h4>
                                    <h2>${data.summary.master_data.count}</h2>
                                </div>
                                <div class="metric-card">
                                    <h4>Transactional</h4>
                                    <h2>${data.summary.transactional_data.count}</h2>
                                </div>
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('overview').innerHTML = 'Failed to load overview';
                }
            }

            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;

                addMessage('user', message);
                input.value = '';

                // Show loading indicator
                const loadingId = addLoadingMessage();

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            message: message,
                            conversation_id: conversationId 
                        })
                    });

                    const data = await response.json();
                    conversationId = data.conversation_id;
                    
                    // Remove loading indicator and show response
                    removeLoadingMessage(loadingId);
                    addMessage('assistant', data.response);
                } catch (error) {
                    removeLoadingMessage(loadingId);
                    addMessage('assistant', `**Error:** ${error.message}`);
                }
            }

            function addMessage(role, content) {
                const messagesEl = document.getElementById('messages');
                const messageEl = document.createElement('div');
                messageEl.className = `message ${role}-message`;
                
                // Parse markdown for assistant messages, plain text for user messages
                const processedContent = role === 'assistant' ? marked.parse(content) : content;
                
                messageEl.innerHTML = `<strong>${role === 'user' ? 'You' : 'Assistant'}:</strong> ${processedContent}`;
                messagesEl.appendChild(messageEl);
                messagesEl.scrollTop = messagesEl.scrollHeight;
            }

            function addLoadingMessage() {
                const messagesEl = document.getElementById('messages');
                const messageEl = document.createElement('div');
                const loadingId = 'loading_' + Date.now();
                messageEl.id = loadingId;
                messageEl.className = 'message assistant-message loading-message';
                messageEl.innerHTML = '<strong>Assistant:</strong> <span class="loading-dots">Thinking</span>';
                messagesEl.appendChild(messageEl);
                messagesEl.scrollTop = messagesEl.scrollHeight;
                return loadingId;
            }

            function removeLoadingMessage(loadingId) {
                const loadingEl = document.getElementById(loadingId);
                if (loadingEl) {
                    loadingEl.remove();
                }
            }

            function quickQuery(query) {
                document.getElementById('messageInput').value = query;
                sendMessage();
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }

            // Initialize
            checkStatus();
            setInterval(checkStatus, 30000); // Check status every 30 seconds
        </script>
    </body>
    </html>
    """

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check system health and connection status - no recursive tool calls"""
    global mcp_manager, chat_handler, collection_manager
    
    try:
        if not mcp_manager or not mcp_manager.is_connected():
            return JSONResponse({
                "status": "unhealthy",
                "error": "MCP connection not available"
            })
        
        if not chat_handler or not collection_manager:
            return JSONResponse({
                "status": "unhealthy", 
                "error": "Components not initialized"
            })
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "mcp_connected": mcp_manager.is_connected(),
                "chat_handler": chat_handler is not None,
                "collection_manager": collection_manager is not None,
                "available_tools": len(mcp_manager.get_available_tools())
            }
        }
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "error": str(e)
        })

# Collections endpoint
@app.get("/collections")
async def get_collections():
    """Get all collections summary"""
    global collection_manager
    
    try:
        if not collection_manager:
            raise HTTPException(status_code=503, detail="Collection manager not available")
        
        summary = collection_manager.get_all_collections_summary()
        
        return {
            "success": True,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Collections endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint  
@app.post("/chat", response_model=ChatResponse)
async def chat_with_database(request: ChatRequest):
    """Process chat message with WFM database"""
    global chat_handler
    
    try:
        if not chat_handler:
            raise HTTPException(status_code=503, detail="Chat handler not available")
        
        response = await chat_handler.process_message(request.message)
        
        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id or "default",
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Employee search endpoint
@app.post("/employees/search")
async def search_employees(request: EmployeeSearchRequest):
    """Search employees by name or badge ID"""
    global collection_manager
    
    try:
        if not collection_manager:
            raise HTTPException(status_code=503, detail="Collection manager not available")
        
        result = await collection_manager.find_employees(
            name=request.name,
            badge_id=request.badge_id,
            limit=request.limit
        )
        
        if result.get("success"):
            return {
                "success": True,
                "employees": result.get("result", []),
                "count": result.get("count", 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Search failed"))
            
    except Exception as e:
        logger.error(f"Employee search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Payroll analysis endpoint
@app.post("/payroll/analyze")
async def analyze_payroll(request: PayrollAnalysisRequest):
    """Analyze payroll data by county and date range"""
    global collection_manager
    
    try:
        if not collection_manager:
            raise HTTPException(status_code=503, detail="Collection manager not available")
        
        result = await collection_manager.analyze_payroll(
            county=request.county,
            days_back=request.days_back
        )
        
        if result.get("success"):
            return {
                "success": True,
                "analysis": result.get("result", []),
                "period": result.get("analysis_period", ""),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
            
    except Exception as e:
        logger.error(f"Payroll analysis endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Holidays endpoint
@app.post("/holidays/upcoming")
async def get_upcoming_holidays(request: HolidayRequest):
    """Get upcoming holidays"""
    global collection_manager
    
    try:
        if not collection_manager:
            raise HTTPException(status_code=503, detail="Collection manager not available")
        
        result = await collection_manager.get_upcoming_holidays(
            days_ahead=request.days_ahead
        )
        
        if result.get("success"):
            return {
                "success": True,
                "holidays": result.get("result", []),
                "count": result.get("count", 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Holiday lookup failed"))
            
    except Exception as e:
        logger.error(f"Holidays endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Workforce report endpoint
@app.get("/reports/workforce")
async def get_workforce_report():
    """Generate comprehensive workforce report"""
    global collection_manager
    
    try:
        if not collection_manager:
            raise HTTPException(status_code=503, detail="Collection manager not available")
        
        result = await collection_manager.generate_workforce_report()
        
        if result.get("success"):
            return {
                "success": True,
                "report": result.get("result", {}),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Report generation failed"))
            
    except Exception as e:
        logger.error(f"Workforce report endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Database stats endpoint
@app.get("/stats")
async def get_database_stats():
    """Get database statistics and collection info"""
    global mcp_manager
    
    try:
        if not mcp_manager:
            raise HTTPException(status_code=503, detail="MCP manager not available")
        
        # Get databases
        db_result = await mcp_manager.list_databases()
        
        # Get collections for wfm_database
        coll_result = await mcp_manager.list_collections("wfm_database")
        
        return {
            "success": True,
            "databases": db_result.get("result", []) if db_result.get("success") else [],
            "collections": coll_result.get("result", []) if coll_result.get("success") else [],
            "mcp_tools": len(mcp_manager.get_available_tools()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database stats endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")