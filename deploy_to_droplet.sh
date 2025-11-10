#!/bin/bash
# PROJ344 Droplet Deployment Script
# Fixes all 5 ports: 8501-8505

set -e  # Exit on error

echo "🚀 PROJ344 Dashboard Deployment to Digital Ocean"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
DROPLET_IP="137.184.1.91"
DROPLET_USER="root"
PROJECT_PATH="/opt/ASEAGI"
BRANCH="claude/api-vs-web-clarification-011CUuqk9SwXoeKNSzwfQq68"

echo -e "${YELLOW}Step 1: Connecting to droplet...${NC}"
ssh ${DROPLET_USER}@${DROPLET_IP} << 'ENDSSH'
    set -e

    echo "✓ Connected to droplet"

    # Navigate to project
    cd /opt/ASEAGI || { echo "❌ Project directory not found"; exit 1; }
    echo "✓ Found project directory"

    # Show current branch
    echo "Current branch: $(git branch --show-current)"

    # Pull latest changes
    echo "📥 Pulling latest changes..."
    git fetch origin
    git checkout claude/api-vs-web-clarification-011CUuqk9SwXoeKNSzwfQq68
    git pull origin claude/api-vs-web-clarification-011CUuqk9SwXoeKNSzwfQq68
    echo "✓ Code updated"

    # Stop existing containers
    echo "🛑 Stopping existing containers..."
    docker compose down
    echo "✓ Containers stopped"

    # Clean up old images
    echo "🧹 Cleaning up old images..."
    docker system prune -f
    echo "✓ Cleanup complete"

    # Build fresh images
    echo "🐳 Building fresh Docker images..."
    docker compose build --no-cache
    echo "✓ Images built"

    # Start all containers
    echo "🚀 Starting all 5 dashboards..."
    docker compose up -d
    echo "✓ Containers started"

    # Wait for containers to initialize
    echo "⏳ Waiting 10 seconds for containers to initialize..."
    sleep 10

    # Check status
    echo ""
    echo "📊 Container Status:"
    docker compose ps

    # Check health
    echo ""
    echo "🏥 Health Checks:"
    for port in 8501 8502 8503 8504 8505; do
        if curl -sf http://localhost:${port}/_stcore/health > /dev/null 2>&1; then
            echo "  ✓ Port ${port}: HEALTHY"
        else
            echo "  ⚠️  Port ${port}: INITIALIZING (check logs if this persists)"
        fi
    done

    # Show logs for any unhealthy containers
    echo ""
    echo "📝 Recent logs (last 20 lines per container):"
    docker compose logs --tail=20

    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "Access your dashboards at:"
    echo "  • Master Dashboard:     http://137.184.1.91:8501"
    echo "  • Legal Intelligence:   http://137.184.1.91:8502"
    echo "  • CEO Dashboard:        http://137.184.1.91:8503"
    echo "  • Scanning Monitor:     http://137.184.1.91:8504"
    echo "  • Timeline & Violations: http://137.184.1.91:8505"
    echo ""
ENDSSH

echo ""
echo -e "${GREEN}✅ Deployment script completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Test all dashboards in your browser"
echo "2. Check for any errors: ssh root@137.184.1.91 'cd /opt/ASEAGI && docker compose logs -f'"
echo "3. If any port fails, check specific logs: docker compose logs container-name"
