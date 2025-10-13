#!/bin/bash

# Script to restart Celery worker
# Usage: ./restart_celery.sh

echo "🔄 Restarting Celery worker..."

# Kill existing Celery processes
echo "📝 Killing existing Celery processes..."
pkill -f "celery.*worker" 2>/dev/null || echo "No existing Celery processes found"

# Wait for processes to terminate
echo "⏳ Waiting for processes to terminate..."
sleep 3

# Change to backend directory
cd /Users/swastikpadhi/code/lab/product-market-research/backend

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source /Users/swastikpadhi/code/venv/bin/activate

# Start Celery worker
echo "🚀 Starting Celery worker..."
celery -A app.worker.celery_app worker --loglevel=info

echo "✅ Celery worker restarted successfully!"
