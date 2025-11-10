#!/bin/bash
# Launch Document Upload & Analyzer Dashboard

echo "🚀 Launching Document Upload & Analyzer Dashboard..."
echo ""

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not installed!"
    echo "Install: pip3 install streamlit"
    exit 1
fi

# Check environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set - analysis will be disabled"
fi

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "⚠️  Warning: Supabase credentials not set"
    echo "   Set SUPABASE_URL and SUPABASE_KEY environment variables"
fi

# Create upload directories if they don't exist
mkdir -p /home/user/ASEAGI/uploads/{processed,pending,chat_history}

# Launch dashboard
cd "$(dirname "$0")"
streamlit run document_upload_analyzer.py --server.port 8503

