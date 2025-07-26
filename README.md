# 👥 WFM Database Assistant

A sophisticated **FastAPI-powered** Workforce Management Database Assistant with **Anthropic Claude AI** and **MongoDB MCP Server**. Chat naturally with your WFM data using intelligent multi-turn conversations.

## ✨ Key Features

- **🤖 Multi-Turn AI Chat**: Advanced conversation flow with Claude 3.5 Sonnet
- **📊 9 WFM Collections**: Complete workforce data coverage (450+ documents)
- **⚡ Real-time Analysis**: Instant payroll, employee, and activity insights
- **🔄 Smart Retry Logic**: 10-turn conversation limit with self-correction
- **📝 Markdown Rendering**: Beautiful formatted responses in web interface
- **⏱️ Loading Indicators**: Real-time feedback during query processing
- **🔍 Cross-Collection Analytics**: Complex queries spanning multiple data sources
- **🎉 Holiday Management**: Comprehensive holiday schedule tracking

## 🗂️ Database Structure

### Master Data Collections (6)
- **employees**: Employee records with badges, contacts, employment history
- **activities**: Work activity definitions and descriptions
- **activityTypes**: Categories and types of work activities
- **paycodes**: Payroll codes and compensation rules
- **itms_wfm_roles**: User roles and permissions in the WFM system
- **ITMS_HOLIDAYS_LIST**: Holiday schedules with dates and descriptions

### Transactional Data Collections (3)
- **dailyActivities**: Daily work activity tracking and time logs
- **itms_wfm_payroll**: Payroll records with hours, dates, counties, and employee details
- **itms_wfm_user_roles**: User role assignments and access permissions

## 🚀 Quick Start

### Prerequisites

1. **Node.js** (20.19.0+) for MongoDB MCP Server
2. **Python** (3.9+) for the FastAPI application
3. **MongoDB** running locally with your WFM data loaded
4. **Anthropic API Key** for Claude integration

### Installation

1. **Clone and Setup**:
```bash
git clone <your-repo-url>
cd wfm-mcp-chatbot
pip install -r requirements.txt
npm install -g mongodb-mcp-server
```

2. **Configure Environment**:
```bash
cp config/.env.example config/.env
# Edit config/.env with your credentials:
# ANTHROPIC_API_KEY=your_claude_api_key_here
# MONGODB_CONNECTION_STRING=mongodb://localhost:27017/wfm_database
```

3. **Start MongoDB MCP Server**:
```bash
npx -y mongodb-mcp-server \
  --connectionString="mongodb://localhost:27017/wfm_database" \
  --readOnly \
  --transport http \
  --httpPort 3001 \
  --loggers disk,stderr
```

4. **Run the FastAPI Application**:
```bash
python3 src/main.py
```

5. **Open Browser**: Visit `http://localhost:8000`

## 💬 Example Queries

Try these natural language queries in the chat interface:

### Employee Management
- *"Find employees from East Krista county"*
- *"Show me employee with badge ID 2114"*
- *"How many employees do we have by employment type?"*

### Payroll Analysis
- *"Show payroll trends by county"*
- *"Which counties have the highest total hours worked?"*
- *"Analyze payroll data for the last 30 days"*

### Activity Tracking
- *"Show recent daily activities"*
- *"What's the activity completion rate?"*
- *"Find activities for specific employees"*

### Holiday Management
- *"What holidays are coming up?"*
- *"Show upcoming holidays for workforce planning"*
- *"Holiday schedule for the next 90 days"*

### Advanced Analytics
- *"Generate a comprehensive workforce report"*
- *"Show employee distribution across counties"*
- *"Create workforce analytics dashboard"*

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Anthropic      │    │   MCP Client    │
│   + HTML UI     │◄──►│   Claude AI      │◄──►│   (AsyncExit)   │
│   (Port 8000)   │    │   Multi-turn     │    │   Stack Mgmt    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                         │
         ▼                       ▼                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Markdown      │    │  Conversation    │    │  MongoDB MCP    │
│   Rendering     │    │   Context        │    │    Server       │
│   + Loading     │    │   History        │    │   (Node.js)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   MongoDB       │
                                               │ wfm_database    │
                                               │ (9 Collections) │
                                               │  450+ docs      │
                                               └─────────────────┘
```

## 📁 Project Structure

```
wfm-mcp-chatbot/
├── src/
│   ├── main.py                   # FastAPI application with HTML UI
│   ├── chat_handler.py           # Multi-turn Claude AI integration  
│   ├── mcp_connection_manager.py # Proper MCP SDK implementation
│   ├── collection_manager.py     # WFM collection management
│   └── wfm_queries.py           # Query templates & builders
├── config/
│   ├── .env.example             # Environment template
│   ├── .env                     # Your environment (git-ignored)
│   └── mcp_config.json          # MCP server configuration
├── .gitignore                   # Comprehensive exclusions
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_claude_api_key_here
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/wfm_database

# Optional (with defaults)
MCP_SERVER_URL=http://localhost:3001
MCP_TIMEOUT=10000
LOG_LEVEL=INFO
WFM_DATABASE_NAME=wfm_database
DEBUG_MODE=false
```

### MCP Server Configuration

The `config/mcp_config.json` contains the MCP server setup:

```json
{
  "mcpServers": {
    "MongoDB-WFM": {
      "command": "npx",
      "args": ["-y", "mongodb-mcp-server", "--connectionString", "mongodb://localhost:27017/wfm_database", "--readOnly"],
      "env": {
        "MDB_MCP_READ_ONLY": "true"
      }
    }
  }
}
```

## 🎨 Web Interface Features

### Chat Interface
- **Natural Language Queries**: Ask questions in plain English
- **Multi-turn Conversations**: AI remembers context and can self-correct
- **Markdown Rendering**: Beautiful formatted responses with headers, lists, code blocks
- **Loading Indicators**: Real-time "Thinking..." feedback during processing
- **Query History**: Conversation context preserved across messages

### Database Overview Sidebar
- **Collection Statistics**: Real-time document counts for all 9 collections
- **Quick Query Buttons**: One-click access to common queries
- **Connection Status**: Live health monitoring
- **Metrics Dashboard**: Total collections, records, and data breakdown

### Advanced Features
- **Tool Call Retry Logic**: Up to 10 API calls with intelligent error recovery
- **Timeout Protection**: 20-second safeguards prevent hanging queries
- **Error Handling**: Graceful fallbacks for invalid queries
- **Cross-Collection Joins**: Complex analytics spanning multiple data sources

## 🔧 Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**:
   ```bash
   # Check if MongoDB is running
   mongosh "mongodb://localhost:27017/wfm_database"
   
   # Restart MCP server
   pkill -f mongodb-mcp-server
   npx -y mongodb-mcp-server --connectionString="mongodb://localhost:27017/wfm_database" --readOnly --transport http --httpPort 3001
   ```

2. **FastAPI Import Errors**:
   ```bash
   # Run from project root (not src/)
   python3 src/main.py
   ```

3. **Chat Not Working**:
   ```bash
   # Verify API key is set
   grep ANTHROPIC_API_KEY config/.env
   
   # Check application logs
   python3 src/main.py
   ```

4. **Database Connection Issues**:
   ```bash
   # Test MongoDB connection
   mongosh "mongodb://localhost:27017/wfm_database"
   
   # Verify collections exist
   show collections
   ```

### Health Check Endpoints

```bash
# Check application health
curl http://localhost:8000/health

# Get database statistics  
curl http://localhost:8000/stats

# View collection overview
curl http://localhost:8000/collections
```

## 📊 Performance & Scale

- **Query Response**: 2-15 seconds for complex multi-turn conversations
- **Data Processing**: 450+ documents across 9 collections
- **Concurrent Users**: FastAPI async architecture supports multiple users
- **Memory Usage**: ~150MB typical usage with MCP connection pooling
- **Conversation Turns**: Up to 10 API calls per query with intelligent retry logic

## 🛡️ Security Features

- **Read-Only Database Access**: MCP server runs in strict read-only mode
- **API Key Protection**: Environment variables with comprehensive .gitignore
- **Input Validation**: Query sanitization and error handling
- **Request Timeouts**: Prevents resource exhaustion from long-running queries
- **Conversation Limits**: 10-turn maximum prevents infinite API loops

## 🚀 API Endpoints

### Core Endpoints
- `GET /` - Web interface with chat functionality
- `POST /chat` - Process natural language queries
- `GET /health` - Application health check
- `GET /collections` - Database collection overview

### Specialized Endpoints
- `POST /employees/search` - Employee search functionality
- `POST /payroll/analyze` - Payroll data analysis
- `POST /holidays/upcoming` - Holiday schedule queries
- `GET /reports/workforce` - Comprehensive workforce reports

## 🎯 Advanced Use Cases

### Complex Analytics Queries
- **Multi-collection joins**: "Show employees from East Krista county and their recent payroll records"
- **Temporal analysis**: "Analyze workforce trends over the last quarter"
- **Anomaly detection**: "Find unusual payroll patterns or outliers"
- **Predictive insights**: "Which counties need more workforce coverage?"

### Conversation Examples
```
You: "Find employees from East Krista county"
Assistant: "I found 1 employee who worked in East Krista county..."

You: "What's their recent activity?"
Assistant: [Remembers context] "For Jamie Lowe (badge 2114)..."

You: "Show me the payroll trends for that county"
Assistant: [Continues conversation] "Based on East Krista county data..."
```

## 🤝 Contributing

This project uses a clean, modular architecture:

- **`main.py`**: FastAPI application with lifespan management
- **`chat_handler.py`**: Multi-turn conversation logic with Claude
- **`mcp_connection_manager.py`**: Proper MCP SDK implementation with AsyncExitStack
- **`collection_manager.py`**: WFM-specific database operations
- **`wfm_queries.py`**: Query templates and builders

## 📜 License

Internal use for Workforce Management Database analysis and insights.

---

**🎉 Ready to analyze your WFM data with AI? Start the application and ask anything!**

```bash
python3 src/main.py
# Open http://localhost:8000
# Ask: "What can you tell me about our workforce data?"
```