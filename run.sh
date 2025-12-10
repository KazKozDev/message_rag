#!/bin/bash

# Message RAG System Launcher
# Automatic web interface startup

set -e

echo "🚀 Message RAG System Launcher"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo -e "${RED}❌ IMPORTANT: Add your ANTHROPIC_API_KEY to .env file${NC}"
    echo "After adding the key, run the script again."
    open .env
    exit 1
fi

# Check if API key is configured
if ! grep -q "sk-ant-" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠️  API key not configured${NC}"
    echo -e "${RED}Open .env file and add your ANTHROPIC_API_KEY${NC}"
    open .env
    exit 1
fi

# Port for Streamlit
PORT=8501

# Check if port is in use
echo -e "${BLUE}🔍 Checking port $PORT...${NC}"
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port $PORT is in use${NC}"
    PID=$(lsof -Pi :$PORT -sTCP:LISTEN -t)
    echo "Killing process $PID..."
    kill -9 $PID 2>/dev/null || true
    sleep 2
    echo -e "${GREEN}✓ Port freed${NC}"
else
    echo -e "${GREEN}✓ Port $PORT is available${NC}"
fi

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found${NC}"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Check dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"
if ! python -c "import streamlit" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dependencies not installed${NC}"
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p data/cache data/outputs data/embeddings
echo -e "${GREEN}✓ Directories ready${NC}"

# Start Streamlit in background
echo -e "${BLUE}🚀 Starting web interface...${NC}"
echo ""

# Start with output redirection
nohup streamlit run src/web_app.py \
    --server.port=$PORT \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.fileWatcherType=none \
    > data/outputs/streamlit.log 2>&1 &

STREAMLIT_PID=$!
echo $STREAMLIT_PID > .streamlit.pid

# Wait for server to start
echo "Waiting for server to start..."
for i in {1..30}; do
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${GREEN}✓ Server started (PID: $STREAMLIT_PID)${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

echo ""

# Check if server actually started
if ! lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}❌ Failed to start server${NC}"
    echo "Check logs: cat data/outputs/streamlit.log"
    exit 1
fi

# Display information
echo ""
echo "================================"
echo -e "${GREEN}✨ Message RAG System Ready!${NC}"
echo "================================"
echo ""
echo "📍 URL: http://localhost:$PORT"
echo "🔑 PID: $STREAMLIT_PID"
echo "📄 Logs: data/outputs/streamlit.log"
echo ""
echo "Commands:"
echo "  • Stop: ./stop.sh"
echo "  • Logs: tail -f data/outputs/streamlit.log"
echo ""

# Wait before opening browser
sleep 2

# Open in browser
echo -e "${BLUE}🌐 Opening browser...${NC}"
open "http://localhost:$PORT"

echo ""
echo -e "${GREEN}✓ Done! Browser opened.${NC}"
echo ""
echo "Instructions:"
echo "1. Upload examples/sample_messages.json in the sidebar"
echo "2. Click 'Ingest Messages'"
echo "3. Ask questions in the chat"
echo ""
