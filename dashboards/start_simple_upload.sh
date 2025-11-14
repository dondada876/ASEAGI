#!/bin/bash
# Start Simple Document Upload Portal
# Access at: http://137.184.1.91:8505

echo "🚀 Starting Simple Document Upload Portal..."
echo ""

cd /home/user/ASEAGI/dashboards

# Kill any existing process on port 8505
lsof -ti:8505 | xargs kill -9 2>/dev/null || true

# Create upload directory
mkdir -p /home/user/ASEAGI/uploads/web_uploads

# Start Streamlit on port 8505
streamlit run simple_document_upload.py \
    --server.port 8505 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    > /tmp/simple_upload.log 2>&1 &

sleep 3

if lsof -i:8505 > /dev/null 2>&1; then
    echo "✅ Upload portal started successfully!"
    echo ""
    echo "📱 Access your upload portal:"
    echo "   http://137.184.1.91:8505"
    echo ""
    echo "💾 Files will be saved to:"
    echo "   /home/user/ASEAGI/uploads/web_uploads/"
    echo ""
    echo "📊 Check logs:"
    echo "   tail -f /tmp/simple_upload.log"
else
    echo "❌ Failed to start. Check logs:"
    echo "   cat /tmp/simple_upload.log"
    exit 1
fi
