#!/bin/bash
# ASEAGI Digital Ocean Deployment Script
# Deploys all dashboards to droplet at 137.184.1.91

set -e  # Exit on error

DROPLET_IP="137.184.1.91"
DROPLET_USER="root"
PROJECT_DIR="/opt/ASEAGI"

echo "🚀 ASEAGI Digital Ocean Deployment"
echo "===================================="
echo "Target: $DROPLET_USER@$DROPLET_IP"
echo ""

# Test SSH connection
echo "📡 Testing SSH connection..."
ssh -o ConnectTimeout=10 $DROPLET_USER@$DROPLET_IP "echo '✅ SSH connection successful'" || {
    echo "❌ Cannot connect to droplet. Please check:"
    echo "   - Droplet is running"
    echo "   - SSH key is added to droplet"
    echo "   - IP address is correct: $DROPLET_IP"
    exit 1
}

echo ""
echo "📦 Installing Docker and dependencies..."
ssh $DROPLET_USER@$DROPLET_IP 'bash -s' << 'ENDSSH'
# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y apt-transport-https ca-certificates curl software-properties-common git ufw

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
systemctl start docker
systemctl enable docker

# Verify installation
docker --version
docker compose version

echo "✅ Docker installed successfully"
ENDSSH

echo ""
echo "🔐 Configuring firewall..."
ssh $DROPLET_USER@$DROPLET_IP 'bash -s' << 'ENDSSH'
# Configure UFW firewall
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# Allow SSH
ufw allow 22/tcp

# Allow HTTP & HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow dashboard ports (for testing without nginx)
ufw allow 8501:8505/tcp

# Enable firewall
ufw --force enable

ufw status

echo "✅ Firewall configured"
ENDSSH

echo ""
echo "📥 Cloning ASEAGI repository..."
ssh $DROPLET_USER@$DROPLET_IP "rm -rf $PROJECT_DIR && git clone https://github.com/dondada876/ASEAGI.git $PROJECT_DIR"

echo ""
echo "🔑 Creating environment file..."
ssh $DROPLET_USER@$DROPLET_IP "cat > $PROJECT_DIR/.env" << 'ENVFILE'
# Supabase Configuration
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c

# Dashboard Passwords
MASTER_PASSWORD=Ashe2024Bucknor!
LEGAL_PASSWORD=Justice2024Legal!
CEO_PASSWORD=Proj344CEO!
TIMELINE_PASSWORD=Timeline2024!
MONITOR_PASSWORD=Monitor2024!

# Case Information
CASE_ID=ashe-bucknor-j24-00478
DOCKET_NUMBER=J24-00478
ENVFILE

echo ""
echo "🐳 Building Docker images..."
ssh $DROPLET_USER@$DROPLET_IP "cd $PROJECT_DIR && docker compose build"

echo ""
echo "🚀 Starting all dashboards..."
ssh $DROPLET_USER@$DROPLET_IP "cd $PROJECT_DIR && docker compose up -d"

echo ""
echo "⏳ Waiting for containers to start..."
sleep 10

echo ""
echo "📊 Checking container status..."
ssh $DROPLET_USER@$DROPLET_IP "cd $PROJECT_DIR && docker compose ps"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your dashboards are now live:"
echo "   Master Dashboard:    http://$DROPLET_IP:8501"
echo "   Scanning Monitor:    http://$DROPLET_IP:8502"
echo "   Legal Intelligence:  http://$DROPLET_IP:8503"
echo "   CEO Dashboard:       http://$DROPLET_IP:8504"
echo "   Timeline Dashboard:  http://$DROPLET_IP:8505"
echo ""
echo "📋 Useful commands:"
echo "   View logs:    ssh $DROPLET_USER@$DROPLET_IP 'cd $PROJECT_DIR && docker compose logs -f'"
echo "   Restart:      ssh $DROPLET_USER@$DROPLET_IP 'cd $PROJECT_DIR && docker compose restart'"
echo "   Stop:         ssh $DROPLET_USER@$DROPLET_IP 'cd $PROJECT_DIR && docker compose down'"
echo ""
echo "For Ashe. For Justice. For All Children. 🛡️"
