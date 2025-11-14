#!/bin/bash
# Quick Start: Document Upload Dashboard
# Use this instead of the broken Telegram bot

echo "🚀 Starting Document Upload Dashboard..."
echo ""
echo "This dashboard replaces the Telegram bot for uploading documents."
echo "It provides:"
echo "  ✅ Drag & drop file upload"
echo "  ✅ Instant confirmation"
echo "  ✅ Claude AI analysis"
echo "  ✅ Secure storage"
echo ""

cd /home/user/ASEAGI/dashboards

# Check if running
if lsof -Pi :8503 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Dashboard already running at http://localhost:8503"
else
    echo "Starting dashboard on port 8503..."
    streamlit run document_upload_analyzer.py --server.port 8503 &
    sleep 3
    echo "✅ Dashboard started!"
fi

echo ""
echo "📱 Access the dashboard:"
echo "   Local: http://localhost:8503"
echo "   Remote: http://137.184.1.91:8503"
echo ""
echo "💡 Upload your images here instead of Telegram bot"
