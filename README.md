# 🚀 WFM Database Assistant

**FastAPI-powered Workforce Management Database Assistant** with Anthropic Claude AI and MongoDB MCP Server integration. Experience intelligent multi-turn conversations with your workforce data.

## ✨ Features

- **🤖 Advanced AI Chat**: Multi-turn conversations with Claude 3.5 Sonnet
- **📊 Complete WFM Coverage**: 9 MongoDB collections, 450+ documents
- **⚡ Real-time Analytics**: Instant employee, payroll, and activity insights
- **🔄 Smart Conversations**: 10-turn retry logic with self-correction
- **📝 Beautiful UI**: Markdown rendering with loading indicators
- **🎯 Cross-Collection Queries**: Complex analytics across multiple data sources

## 🏗️ Architecture

```
FastAPI Server (Port 8000) → Claude AI → MCP Client → MongoDB MCP Server → MongoDB
```

## 📁 Project Structure

```
wfm-mcp-chatbot/
├── src/
│   ├── main.py                   # FastAPI application + HTML interface
│   ├── chat_handler.py           # Multi-turn Claude AI conversations  
│   ├── mcp_connection_manager.py # MCP SDK implementation
│   ├── collection_manager.py     # WFM database operations
│   └── wfm_queries.py           # Query templates
├── config/
│   ├── .env.example             # Environment template
│   └── mcp_config.json          # MCP server configuration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Prerequisites
- **Node.js** 20.19.0+ (for MongoDB MCP Server)
- **Python** 3.9+ (for FastAPI application)
- **MongoDB** with `wfm_database` loaded
- **Anthropic API Key**

### 2. Installation
```bash
git clone <your-repo>
cd wfm-mcp-chatbot
pip install -r requirements.txt
npm install -g mongodb-mcp-server
```

### 3. Configuration
```bash
cp config/.env.example config/.env
# Edit config/.env:
# ANTHROPIC_API_KEY=your_key_here
# MONGODB_CONNECTION_STRING=mongodb://localhost:27017/wfm_database
```

### 4. Start MCP Server
```bash
npx -y mongodb-mcp-server \
  --connectionString="mongodb://localhost:27017/wfm_database" \
  --readOnly \
  --transport http \
  --httpPort 3001
```

### 5. Run Application
```bash
python3 src/main.py
```

### 6. Open Browser
Visit: **http://localhost:8000**

## 💾 Database Collections

### Master Data (6 collections)
- `employees` - Employee records with badges and details
- `activities` - Work activity definitions  
- `activityTypes` - Activity categories
- `paycodes` - Payroll codes and rules
- `itms_wfm_roles` - System user roles
- `ITMS_HOLIDAYS_LIST` - Holiday schedules

### Transactional Data (3 collections)  
- `dailyActivities` - Daily work tracking
- `itms_wfm_payroll` - Payroll records by county
- `itms_wfm_user_roles` - User role assignments

## 💬 Example Queries

### Employee Management
- "Find employees from East Krista county"
- "Show me employee with badge ID 2114"
- "How many employees by type?"

### Payroll Analysis
- "Show payroll trends by county"
- "Which counties have highest hours?"
- "Analyze last 30 days payroll data"

### Holiday Planning  
- "What holidays are coming up?"
- "Show next 90 days holiday schedule"

### Advanced Analytics
- "Generate comprehensive workforce report"
- "Cross-reference employees and payroll data"
- "Find unusual patterns in work hours"

## 🎨 Web Interface

### Chat Features
- **Natural Language**: Ask questions in plain English
- **Multi-turn Context**: AI remembers conversation history
- **Markdown Rendering**: Beautiful formatted responses
- **Loading Indicators**: Real-time "Thinking..." feedback
- **Error Recovery**: Intelligent retry on failed queries

### Dashboard
- **Live Statistics**: Real-time collection counts
- **Quick Queries**: One-click common questions
- **Health Monitoring**: Connection status display

## 🔧 API Endpoints

### Core
- `GET /` - Web interface
- `POST /chat` - Process chat messages
- `GET /health` - System health check
- `GET /collections` - Database overview

### Specialized
- `POST /employees/search` - Employee search
- `POST /payroll/analyze` - Payroll analytics
- `POST /holidays/upcoming` - Holiday queries
- `GET /reports/workforce` - Workforce reports

## ⚙️ Configuration

### Environment Variables
```bash
# Required
ANTHROPIC_API_KEY=your_claude_api_key
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/wfm_database

# Optional
MCP_SERVER_URL=http://localhost:3001
LOG_LEVEL=INFO
```

## 🔍 Troubleshooting

### MCP Connection Issues
```bash
# Check MongoDB
mongosh "mongodb://localhost:27017/wfm_database"

# Restart MCP Server
pkill -f mongodb-mcp-server
npx -y mongodb-mcp-server --connectionString="mongodb://localhost:27017/wfm_database" --readOnly --transport http --httpPort 3001
```

### Application Issues  
```bash
# Check health
curl http://localhost:8000/health

# Verify API key
grep ANTHROPIC_API_KEY config/.env

# Check logs
python3 src/main.py
```

## 📊 Performance

- **Response Time**: 2-15 seconds for complex conversations
- **Data Scale**: 450+ documents across 9 collections  
- **Conversation Depth**: Up to 10 API calls per query
- **Memory Usage**: ~150MB typical
- **Concurrent Users**: FastAPI async architecture

## 🛡️ Security

- **Read-Only Database**: MCP server in strict read-only mode
- **API Key Protection**: Environment variables with .gitignore
- **Input Validation**: Query sanitization and error handling
- **Timeout Protection**: Request limits prevent resource exhaustion

## 🎯 Advanced Features

### Multi-turn Conversations
```
You: "Find employees from East Krista county"
AI: "I found 1 employee: Jamie Lowe (badge 2114)..."

You: "What's their recent activity?"  
AI: [Remembers context] "For Jamie Lowe, here are recent activities..."

You: "Show payroll for that county"
AI: [Continues conversation] "Based on East Krista data..."
```

### Error Recovery
- Automatic retry on failed queries
- Intelligent error correction  
- Graceful fallbacks for invalid requests
- 10-turn conversation limits

### Cross-Collection Analytics
- Employee + Payroll correlations
- Activity + Holiday planning
- County-wise workforce distribution
- Temporal trend analysis

## 🚀 Production Ready

This is a complete, production-ready workforce management assistant with:

- ✅ Robust error handling
- ✅ Comprehensive logging
- ✅ Security best practices  
- ✅ Scalable FastAPI architecture
- ✅ Clean, modular codebase
- ✅ Full documentation

## 📄 License

Internal use for Workforce Management Database analysis.

---

**Ready to analyze your workforce data with AI?**

```bash
python3 src/main.py
# Open: http://localhost:8000
# Ask: "What can you tell me about our workforce?"
```

🎉 **Start chatting with your WFM data now!**