#!/bin/bash

# Message RAG System Stopper
# Stop web interface

echo "🛑 Stopping Message RAG System..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PORT=8501
STOPPED=0

# Stop by PID file
if [ -f ".streamlit.pid" ]; then
    PID=$(cat .streamlit.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "Killing process $PID..."
        kill -9 $PID 2>/dev/null
        STOPPED=1
    fi
    rm -f .streamlit.pid
fi

# Stop by port
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PID=$(lsof -Pi :$PORT -sTCP:LISTEN -t)
    echo "Killing process on port $PORT (PID: $PID)..."
    kill -9 $PID 2>/dev/null
    STOPPED=1
fi

# Stop all streamlit processes
STREAMLIT_PIDS=$(pgrep -f "streamlit run")
if [ -n "$STREAMLIT_PIDS" ]; then
    echo "Killing all Streamlit processes..."
    echo "$STREAMLIT_PIDS" | xargs kill -9 2>/dev/null
    STOPPED=1
fi

if [ $STOPPED -eq 1 ]; then
    echo -e "${GREEN}✓ Server stopped${NC}"
else
    echo -e "${YELLOW}ℹ️  Server was not running${NC}"
fi
