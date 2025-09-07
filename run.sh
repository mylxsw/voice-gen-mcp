#!/bin/bash

# MCP Voice Generation Server - HTTP Server Startup Script
# Start HTTP mode MCP server

set -e

echo "🚀 MCP Voice Generation Server - HTTP Mode"
echo "=========================================="

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "📦 Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Virtual environment found"
    source venv/bin/activate
fi

# Check configuration file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "Creating .env from env.example..."
    cp env.example .env
    echo "📝 Please edit .env file with your API credentials and S3 settings"
    echo "   Required: MINIMAX_API_KEY, MINIMAX_GROUP_ID, S3_BUCKET_NAME, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY"
    read -p "Press Enter after configuring .env file..."
fi

# Set HTTP mode environment variables
export MCP_TRANSPORT=http
export MCP_SERVER_HOST=0.0.0.0
export MCP_SERVER_PORT=8000

echo "🌐 Starting MCP server in HTTP mode..."
echo "   Host: $MCP_SERVER_HOST"
echo "   Port: $MCP_SERVER_PORT"
echo "   Endpoint: http://$MCP_SERVER_HOST:$MCP_SERVER_PORT/mcp"
echo ""
echo "📋 Connection Information:"
echo "   - Health Check: Removed as requested"
echo "   - MCP Endpoint: http://$MCP_SERVER_HOST:$MCP_SERVER_PORT/mcp"
echo ""
echo "🔗 For Claude Desktop, use this configuration:"
echo "   {"
echo "     \"mcpServers\": {"
echo "       \"voice-gen-http\": {"
echo "         \"url\": \"http://$MCP_SERVER_HOST:$MCP_SERVER_PORT/mcp\""
echo "       }"
echo "     }"
echo "   }"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python server.py