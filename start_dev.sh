#!/bin/bash

echo "🚀 Starting NeoMentor development servers..."

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $port is already in use"
        return 1
    else
        echo "Port $port is free"
        return 0
    fi
}

# Check if required ports are available
echo "📡 Checking port availability..."
check_port 8000 || exit 1
check_port 3000 || exit 1

echo "🔧 Installing dependencies..."

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
if [ ! -d "env" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv env
fi

source env/bin/activate
pip install -r requirements.txt

echo "🔥 Starting backend server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd ../frontend
npm install

echo "🌐 Starting frontend server..."
npm start &
FRONTEND_PID=$!

echo "✅ Development servers started!"
echo "🔗 Backend API: http://localhost:8000"
echo "🔗 Frontend App: http://localhost:3000"
echo "🔗 API Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup when script exits
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Wait for background processes
wait
