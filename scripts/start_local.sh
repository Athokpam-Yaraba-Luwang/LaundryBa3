#!/bin/bash
echo "Starting LaundryBa Local Environment..."

# Kill existing processes
echo "Stopping any running instances..."
pkill -f "business_app/app.py" 2>/dev/null
pkill -f "customer_app/app.py" 2>/dev/null

# Start Business App
echo "Starting Business App on port 5000..."
.venv/bin/python business_app/app.py &

# Start Customer App  
echo "Starting Customer App on port 5001..."
.venv/bin/python customer_app/app.py &

echo ""
echo "✅ Apps started successfully!"
echo "   Business App: http://localhost:5000"
echo "   Customer App: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both apps"
wait
