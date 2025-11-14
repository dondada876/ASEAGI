#!/bin/bash
# ASEAGI Droplet Deployment Script
# Deploys entire stack to DigitalOcean droplet

set -e

echo "🚀 ASEAGI Droplet Deployment"
echo "=============================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Copy .env.example to .env and fill in your credentials"
    exit 1
fi

# Load environment
source .env

# Check required variables
REQUIRED_VARS=("SUPABASE_URL" "SUPABASE_KEY" "ANTHROPIC_API_KEY" "TELEGRAM_BOT_TOKEN")

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required variable: $var"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Install Docker (if not installed)
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose (if not installed)
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# Install Vast.ai CLI
if ! command -v vastai &> /dev/null; then
    echo "📦 Installing Vast.ai CLI..."
    pip3 install vastai
    echo "✅ Vast.ai CLI installed"
else
    echo "✅ Vast.ai CLI already installed"
fi

# Configure Vast.ai API key
if [ -n "$VASTAI_API_KEY" ]; then
    vastai set api-key $VASTAI_API_KEY
    echo "✅ Vast.ai API key configured"
fi

# Create necessary directories
mkdir -p nginx/ssl
mkdir -p data/redis
mkdir -p data/certbot

echo "✅ Directories created"

# Build and start services
echo "🐳 Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
else
    echo "❌ Some services failed to start"
    docker-compose logs
    exit 1
fi

# Display service URLs
echo ""
echo "✅ Deployment Complete!"
echo "======================="
echo ""
echo "📊 Dashboard:    http://$(hostname -I | awk '{print $1}'):8501"
echo "🤖 API:          http://$(hostname -I | awk '{print $1}'):5000"
echo "📡 Nginx:        http://$(hostname -I | awk '{print $1}')"
echo ""
echo "🔧 Useful commands:"
echo "  docker-compose logs -f          # View logs"
echo "  docker-compose ps               # Check status"
echo "  docker-compose restart          # Restart services"
echo "  docker-compose down             # Stop all services"
echo ""
echo "📱 Set Telegram webhook:"
echo "  curl -X POST \"https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook?url=http://$(hostname -I | awk '{print $1}')/telegram/webhook\""
echo ""
echo "🚀 Ready to process documents!"
