# 👥 WFM Database Assistant

A sophisticated Workforce Management Database Assistant powered by **Anthropic Claude** and **MongoDB MCP Server**. Chat naturally with your WFM data using AI.

## 🎯 Features

- **🤖 AI-Powered Chat**: Natural language queries with Claude 3.5 Sonnet
- **📊 9 WFM Collections**: Complete workforce data coverage
- **⚡ Real-time Analysis**: Instant payroll, employee, and activity insights
- **📈 Visual Analytics**: Charts and dashboards for workforce metrics
- **🔍 Smart Search**: Find employees, analyze payroll, track activities
- **🎉 Holiday Management**: Comprehensive holiday schedule tracking

## 🗂️ Database Structure

### Master Data Collections (6)
- **employees**: Employee records with badges, contacts, employment history
- **activities**: Work activity definitions and descriptions
- **activityTypes**: Categories and types of work activities
- **paycodes**: Payroll codes and compensation rules
- **itms_wfm_roles**: User roles and permissions
- **ITMS_HOLIDAYS_LIST**: Holiday schedules by location

### Transactional Data Collections (3)
- **dailyActivities**: Daily work activity tracking and time logs
- **itms_wfm_payroll**: Payroll records with hours, dates, counties
- **itms_wfm_user_roles**: User role assignments and access

## 🚀 Quick Start

### Prerequisites

1. **Node.js** (20.19.0+) for MongoDB MCP Server
2. **Python** (3.9+) for the application
3. **MongoDB** running locally with your WFM data
4. **Anthropic API Key** for Claude integration

### Installation

1. **Clone and Setup**:
```bash
cd /Users/vivekchithari/Desktop/Bhumika/wfm-mcp-chatbot
pip install -r requirements.txt
npm install -g mongodb-mcp-server
```

2. **Configure Environment**:
```bash
cp config/.env.example config/.env
# Edit config/.env with your credentials:
# ANTHROPIC_API_KEY=your_claude_api_key
# MONGODB_CONNECTION_STRING=mongodb://localhost:27017/wfm_database
```

3. **Start MongoDB MCP Server**:
```bash
npx -y mongodb-mcp-server --connectionString="mongodb://localhost:27017/wfm_database" --readOnly --transport http --httpPort 3001
```

4. **Run the Application**:
```bash
cd src
streamlit run app.py
```

5. **Open Browser**: Visit `http://localhost:8501`

## 🧪 Testing

Run comprehensive tests to verify your setup:

```bash
cd tests
python run_tests.py
```

Tests include:
- ✅ MCP server connectivity
- ✅ All 9 collections accessibility
- ✅ Data integrity checks
- ✅ Query functionality
- ✅ Chat handler integration
- ✅ Performance metrics

## 💬 Example Queries

Try these natural language queries:

### Employee Management
- *"Find employee with badge ID 2114"*
- *"Show me all Full-Time employees"*
- *"How many employees do we have by type?"*

### Payroll Analysis
- *"Show payroll summary for East Krista county"*
- *"Which employees worked overtime last month?"*
- *"What are the top 5 counties by total hours?"*

### Activity Tracking
- *"Show daily activities for December 15th"*
- *"What's the activity completion rate?"*
- *"List all activities for employee John Smith"*

### Holiday Management
- *"What holidays are coming up?"*
- *"Show holidays for next quarter"*
- *"Holiday schedule for workforce planning"*

### Advanced Analytics
- *"Generate a comprehensive workforce report"*
- *"Analyze payroll trends by county"*
- *"Show employee productivity metrics"*

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Anthropic      │    │   MCP Client    │
│   Frontend      │◄──►│   Claude AI      │◄──►│   (Python)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │  MongoDB MCP    │
                                               │    Server       │
                                               │   (Node.js)     │
                                               └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   MongoDB       │
                                               │ wfm_database    │
                                               │ (9 Collections) │
                                               └─────────────────┘
```

## 📁 Project Structure

```
wfm-mcp-chatbot/
├── src/
│   ├── app.py                 # Main Streamlit application
│   ├── chat_handler.py        # Claude AI integration
│   ├── mcp_client.py          # MCP client implementation
│   ├── collection_manager.py  # WFM collection management
│   └── wfm_queries.py         # Query templates & builders
├── config/
│   ├── .env                   # Environment variables
│   └── mcp_config.json        # MCP server configuration
├── tests/
│   ├── test_wfm_integration.py # Comprehensive tests
│   └── run_tests.py           # Test runner
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_claude_api_key_here
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/wfm_database

# Optional
MCP_SERVER_URL=http://localhost:3001
LOG_LEVEL=INFO
```

### MCP Server Options

```bash
# Basic setup (read-only)
npx mongodb-mcp-server --connectionString="mongodb://localhost:27017/wfm_database" --readOnly

# HTTP transport (recommended for development)
npx mongodb-mcp-server --connectionString="mongodb://localhost:27017/wfm_database" --readOnly --transport http --httpPort 3001

# With logging
npx mongodb-mcp-server --connectionString="mongodb://localhost:27017/wfm_database" --readOnly --loggers disk,stderr
```

## 🎨 UI Features

### Chat Interface
- Natural language queries
- Real-time responses
- Query history
- Suggested questions

### Analytics Dashboard
- **Overview**: Workforce summary with key metrics
- **Employees**: Search and analyze employee data
- **Payroll**: County-wise payroll analysis with charts
- **Activities**: Holiday management and activity tracking

### Sidebar
- Collection overview (9 collections)
- Quick query buttons
- Database statistics
- Connection status

## 🔧 Troubleshooting

### Common Issues

1. **MCP Server Not Responding**:
   ```bash
   # Check if MongoDB is running
   brew services list | grep mongodb
   
   # Restart MCP server
   pkill -f mongodb-mcp-server
   npx mongodb-mcp-server --connectionString="mongodb://localhost:27017/wfm_database" --readOnly --transport http --httpPort 3001
   ```

2. **Import Errors**:
   ```bash
   # Ensure you're in the src directory
   cd src
   streamlit run app.py
   ```

3. **API Key Issues**:
   ```bash
   # Verify environment variables
   echo $ANTHROPIC_API_KEY
   
   # Check .env file
   cat config/.env
   ```

4. **Database Connection**:
   ```bash
   # Test MongoDB connection
   mongosh "mongodb://localhost:27017/wfm_database"
   
   # List collections
   show collections
   ```

### Testing Connection

```bash
# Test MCP server
curl http://localhost:3001

# Run integration tests
cd tests && python run_tests.py
```

## 📊 Performance

- **Query Response**: < 2 seconds for most queries
- **Data Loading**: 450+ documents across 9 collections
- **Concurrent Users**: Designed for multiple simultaneous users
- **Memory Usage**: ~100MB typical usage

## 🛡️ Security

- **Read-Only Mode**: MCP server runs in read-only mode by default
- **API Key Security**: Environment variables for sensitive data
- **Input Validation**: Query validation and sanitization
- **Error Handling**: Comprehensive error handling and logging

## 🚀 Deployment

### Local Development
- Use the quick start guide above
- MongoDB MCP server on port 3001
- Streamlit app on port 8501

### Production
- Use environment variables for configuration
- Consider Docker deployment
- Implement authentication if needed
- Monitor logs and performance

## 🤝 Contributing

This is a complete, production-ready WFM Database Assistant. The architecture is modular and extensible for future enhancements.

## 📜 License

Internal use for Workforce Management Database analysis.

---

**🎉 Ready to chat with your WFM data? Start the application and ask anything!**