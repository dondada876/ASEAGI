#!/bin/bash
# ============================================================================
# ASEAGI Digital Ocean Deployment Script
# Deploys FastAPI + Streamlit + Redis to Digital Ocean droplet
# ============================================================================

set -e  # Exit on error

echo "============================================================================"
echo "ASEAGI DIGITAL OCEAN DEPLOYMENT"
echo "============================================================================"
echo ""

# ============================================================================
# STEP 1: Environment Setup
# ============================================================================

echo "📋 Step 1: Checking environment variables..."

if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cat > .env << EOF
# Supabase
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=your-supabase-key-here

# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here

# Anthropic
ANTHROPIC_API_KEY=your-key-here

# Redis
REDIS_PASSWORD=$(openssl rand -base64 32)
EOF
    echo "✅ Created .env file. Please edit with your API keys:"
    echo "   nano .env"
    exit 1
fi

source .env

if [ -z "$SUPABASE_KEY" ] || [ "$SUPABASE_KEY" = "your-supabase-key-here" ]; then
    echo "❌ Please set SUPABASE_KEY in .env file"
    exit 1
fi

echo "✅ Environment variables loaded"
echo ""

# ============================================================================
# STEP 2: Install Docker (if not already installed)
# ============================================================================

echo "🐳 Step 2: Checking Docker installation..."

if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh

    # Add current user to docker group
    sudo usermod -aG docker $USER

    echo "✅ Docker installed"
    echo "⚠️  Please log out and log back in for Docker permissions to take effect"
    echo "   Then run this script again"
    exit 0
else
    echo "✅ Docker already installed"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

echo ""

# ============================================================================
# STEP 3: Build Docker Images
# ============================================================================

echo "🔨 Step 3: Building Docker images..."

docker-compose build

echo "✅ Docker images built"
echo ""

# ============================================================================
# STEP 4: Start Services
# ============================================================================

echo "🚀 Step 4: Starting services..."

# Stop existing containers (if any)
docker-compose down

# Start new containers
docker-compose up -d

echo "✅ Services started"
echo ""

# ============================================================================
# STEP 5: Wait for Services to be Ready
# ============================================================================

echo "⏳ Step 5: Waiting for services to be ready..."

# Wait for API
echo "   Waiting for API..."
until curl -f http://localhost:8000/health &> /dev/null; do
    sleep 2
done
echo "   ✅ API ready"

# Wait for Dashboard
echo "   Waiting for Dashboard..."
until curl -f http://localhost:80 &> /dev/null; do
    sleep 2
done
echo "   ✅ Dashboard ready"

echo ""

# ============================================================================
# STEP 6: Display Status
# ============================================================================

echo "============================================================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "============================================================================"
echo ""

# Get public IP
PUBLIC_IP=$(curl -s https://api.ipify.org)

echo "📊 Services Running:"
echo ""
echo "   🌐 Streamlit Dashboard:"
echo "      http://$PUBLIC_IP"
echo "      http://localhost"
echo ""
echo "   🔌 FastAPI Backend:"
echo "      http://$PUBLIC_IP:8000"
echo "      http://localhost:8000"
echo "      Docs: http://$PUBLIC_IP:8000/docs"
echo ""
echo "   📱 Mobile Access:"
echo "      Open on phone: http://$PUBLIC_IP"
echo ""

echo "📝 Container Status:"
docker-compose ps

echo ""
echo "📊 Resource Usage:"
docker stats --no-stream

echo ""
echo "============================================================================"
echo "NEXT STEPS"
echo "============================================================================"
echo ""
echo "1. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "2. Access dashboard:"
echo "   Open browser: http://$PUBLIC_IP"
echo ""
echo "3. Upload a document:"
echo "   curl -X POST http://localhost:8000/api/upload -F 'file=@test.pdf'"
echo ""
echo "4. View logs:"
echo "   docker-compose logs -f"
echo ""
echo "5. Stop services:"
echo "   docker-compose down"
echo ""
echo "6. Setup SSL (recommended for production):"
echo "   ./setup_ssl.sh yourdomain.com"
echo ""
echo "For Ashe. For Justice. For All Children. 🛡️"
echo ""
