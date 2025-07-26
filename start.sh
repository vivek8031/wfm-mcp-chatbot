#!/bin/bash

# start.sh - WFM Database Assistant Startup Script

echo "🚀 Starting WFM Database Assistant..."
echo "========================================"

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the wfm-mcp-chatbot directory"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 20.19.0+ first."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.9+ first."
    exit 1
fi

# Determine Python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check if MongoDB is running
echo "🔍 Checking MongoDB..."
if ! pgrep -f mongod > /dev/null; then
    echo "⚠️  MongoDB not running. Starting MongoDB..."
    brew services start mongodb/brew/mongodb-community
    sleep 3
fi

# Check if environment file exists
if [ ! -f "config/.env" ]; then
    echo "⚠️  Environment file not found. Creating from template..."
    cp config/.env config/.env.backup 2>/dev/null || true
    cat > config/.env << EOF
# Anthropic Configuration (Primary LLM)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# MongoDB Configuration  
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/wfm_database

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:3001
MCP_TIMEOUT=10000

# Application Configuration
LOG_LEVEL=INFO
WFM_DATABASE_NAME=wfm_database
EOF
    echo "📝 Please edit config/.env with your API keys before continuing."
    echo "   Required: ANTHROPIC_API_KEY"
    echo "   Default MongoDB connection should work if you have the wfm_database loaded."
    read -p "Press Enter after updating config/.env..."
fi

# Check if dependencies are installed
echo "📦 Checking Python dependencies..."
$PYTHON_CMD -c "import streamlit, anthropic, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing Python dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt
fi

# Check if MongoDB MCP server is available
echo "🔍 Checking MongoDB MCP Server..."
if ! command -v mongodb-mcp-server &> /dev/null; then
    echo "⚠️  Installing MongoDB MCP Server..."
    npm install -g mongodb-mcp-server
fi

# Start MongoDB MCP Server in background
echo "🔌 Starting MongoDB MCP Server..."
pkill -f "mongodb-mcp-server" 2>/dev/null || true
sleep 2

npx -y mongodb-mcp-server \
    --connectionString="mongodb://localhost:27017/wfm_database" \
    --readOnly \
    --transport http \
    --httpPort 3001 \
    --loggers disk,stderr &

MCP_PID=$!
echo "📡 MCP Server started (PID: $MCP_PID) on http://localhost:3001"

# Wait for MCP server to start
echo "⏳ Waiting for MCP server to initialize..."
sleep 5

# Test MCP server
for i in {1..10}; do
    if curl -s http://localhost:3001 >/dev/null 2>&1; then
        echo "✅ MCP Server is responding"
        break
    fi
    echo "   Attempt $i/10..."
    sleep 2
done

# Run tests (optional)
echo ""
read -p "🧪 Run integration tests first? (y/N): " run_tests
if [[ $run_tests =~ ^[Yy]$ ]]; then
    echo "🧪 Running integration tests..."
    cd tests && $PYTHON_CMD run_tests.py
    if [ $? -ne 0 ]; then
        echo "❌ Tests failed. Check the output above."
        echo "You can still continue, but some features might not work properly."
        read -p "Continue anyway? (y/N): " continue_anyway
        if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
            echo "Stopping MCP server..."
            kill $MCP_PID 2>/dev/null
            exit 1
        fi
    fi
    cd ..
fi

# Start Streamlit app
echo ""
echo "🎉 Starting WFM Database Assistant..."
echo "📊 Streamlit app will open at: http://localhost:8501"
echo "🔌 MCP Server running at: http://localhost:3001"
echo ""
echo "💡 Tips:"
echo "   - Try asking: 'Show me all collections'"
echo "   - Search employees: 'Find employee with badge 2114'"
echo "   - Analyze payroll: 'Top 5 counties by hours worked'"
echo "   - Check holidays: 'What holidays are coming up?'"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $MCP_PID 2>/dev/null
    echo "✅ Cleanup complete"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Start Streamlit
cd src && $PYTHON_CMD -m streamlit run app.py --server.port=8501

# If we get here, streamlit exited normally
cleanup