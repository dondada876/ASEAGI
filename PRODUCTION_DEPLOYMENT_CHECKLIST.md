# Production Deployment Checklist

## Current Status: Development Sandbox Only

This environment is a **Claude Code sandbox** (ephemeral container), NOT a production server.

## Steps to Deploy to Real Digital Ocean Droplet

### Step 1: Create Droplet (5-10 minutes)

```bash
# Option A: Via Digital Ocean Web UI
1. Go to cloud.digitalocean.com/droplets/new
2. Choose:
   - Region: San Francisco (SFO3)
   - Image: Ubuntu 24.04 LTS
   - Size: Basic, 2-4 GB RAM ($18-24/mo)
   - Authentication: SSH key
   - Hostname: aseagi-production
3. Click "Create Droplet"
4. Note IP address

# Option B: Via doctl CLI
doctl compute droplet create aseagi-production \
  --region sfo3 \
  --image ubuntu-24-04-x64 \
  --size s-2vcpu-2gb \
  --ssh-keys YOUR_SSH_KEY_ID
```

### Step 2: Connect to Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

### Step 3: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Install Python & Node
apt install python3 python3-pip nodejs npm git -y

# Verify installations
docker --version
docker-compose --version
python3 --version
node --version
```

### Step 4: Clone Repositories

```bash
cd /opt
git clone https://github.com/dondada876/ASEAGI.git
git clone https://github.com/dondada876/don1_automation.git

cd ASEAGI
git checkout merge-telegram-bot  # Has telegram bot
```

### Step 5: Configure Environment Variables

```bash
# Create .env file
cat > /opt/ASEAGI/.env << 'EOF'
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_token_from_botfather

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Claude AI
ANTHROPIC_API_KEY=your_anthropic_key

# Case Info
CASE_ID=ashe-bucknor-j24-00478
CASE_NUMBER=J24-00478

# Vtiger (optional)
VTIGER_ENABLED=false
VTIGER_URL=https://your-crm.od2.vtiger.com
VTIGER_USERNAME=admin
VTIGER_ACCESS_KEY=your_access_key
EOF

# Secure it
chmod 600 /opt/ASEAGI/.env
```

### Step 6: Install Python Packages

```bash
cd /opt/ASEAGI
pip3 install -r requirements.txt

# Install additional packages
pip3 install \
  python-telegram-bot==20.7 \
  streamlit \
  fastapi \
  uvicorn \
  anthropic \
  supabase \
  python-dotenv
```

### Step 7: Test Telegram Bot

```bash
cd /opt/ASEAGI
git checkout merge-telegram-bot

# Run in background
nohup python3 telegram_document_bot.py > bot.log 2>&1 &

# Check if running
ps aux | grep telegram

# View logs
tail -f bot.log
```

### Step 8: Deploy Dashboards with Docker Compose

```bash
# Create docker-compose.yml
cat > /opt/ASEAGI/docker-compose.yml << 'EOF'
version: '3.8'

services:
  proj344-master:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - ./:/app
    ports:
      - "8501:8501"
    command: >
      bash -c "pip install -r requirements.txt &&
               streamlit run dashboards/proj344_master_dashboard.py --server.port 8501"
    env_file: .env
    restart: unless-stopped

  legal-intel:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - ./:/app
    ports:
      - "8502:8502"
    command: >
      bash -c "pip install -r requirements.txt &&
               streamlit run dashboards/legal_intelligence_dashboard.py --server.port 8502"
    env_file: .env
    restart: unless-stopped

  ceo-dashboard:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - ./:/app
    ports:
      - "8503:8503"
    command: >
      bash -c "pip install -r requirements.txt &&
               streamlit run dashboards/ceo_dashboard.py --server.port 8503"
    env_file: .env
    restart: unless-stopped

  telegram-bot:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - ./:/app
    command: >
      bash -c "pip install -r requirements.txt &&
               python3 telegram_document_bot.py"
    env_file: .env
    restart: unless-stopped

  fastapi-backend:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - ./api:/app
    ports:
      - "8000:8000"
    command: >
      bash -c "pip install fastapi uvicorn supabase &&
               uvicorn main:app --host 0.0.0.0 --port 8000"
    env_file: .env
    restart: unless-stopped
EOF

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 9: Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS, and dashboard ports
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8501/tcp  # Dashboard 1
ufw allow 8502/tcp  # Dashboard 2
ufw allow 8503/tcp  # Dashboard 3
ufw allow 8000/tcp  # API

ufw enable
ufw status
```

### Step 10: Setup Nginx Reverse Proxy (Optional)

```bash
# Install nginx
apt install nginx -y

# Configure reverse proxy
cat > /etc/nginx/sites-available/aseagi << 'EOF'
server {
    listen 80;
    server_name aseagi.yourdomain.com;

    location /dashboard1 {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /dashboard2 {
        proxy_pass http://localhost:8502;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/aseagi /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 11: Setup SSL with Let's Encrypt (Optional)

```bash
# Install certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot --nginx -d aseagi.yourdomain.com

# Auto-renewal is configured automatically
```

### Step 12: Monitor Services

```bash
# Check Docker containers
docker-compose ps

# View logs
docker-compose logs -f telegram-bot
docker-compose logs -f proj344-master

# Check resource usage
docker stats

# Check system resources
htop
```

---

## Monitoring & Maintenance

### Daily Checks

```bash
# Service status
docker-compose ps

# Disk space
df -h

# Memory usage
free -h

# Bot logs
tail -f bot.log
```

### Weekly Tasks

- Review bot logs for errors
- Check Supabase storage usage
- Monitor API costs (Claude)
- Backup database

### Monthly Tasks

- Update system packages: `apt update && apt upgrade`
- Update Docker images: `docker-compose pull`
- Review security logs
- Optimize database

---

## Troubleshooting

### Bot Not Responding

```bash
# Check if running
ps aux | grep telegram

# Restart bot
docker-compose restart telegram-bot

# View logs
docker-compose logs telegram-bot
```

### Dashboards Not Loading

```bash
# Check container status
docker-compose ps

# Restart dashboard
docker-compose restart proj344-master

# Check firewall
ufw status
```

### Out of Memory

```bash
# Check memory
free -h

# Restart services
docker-compose restart

# Upgrade droplet size if needed
```

---

## Cost Estimate

### Monthly Costs

- **Droplet (2GB RAM):** $18/month
- **Droplet (4GB RAM):** $24/month ⭐ Recommended
- **Supabase:** $0 (free tier)
- **Claude API:** ~$0.015/document
- **Domain:** ~$12/year = $1/month (optional)
- **SSL Certificate:** $0 (Let's Encrypt free)

**Total:** ~$19-25/month

### One-Time Costs

- **Setup time:** 2-3 hours
- **Domain registration:** $12/year (optional)

---

## Current Status

- ✅ Code ready in git
- ✅ Documentation complete
- ❌ Not deployed (sandbox environment only)
- ⏳ Need to follow steps above to deploy

---

## Quick Deploy Commands (After Droplet Created)

```bash
# On fresh Digital Ocean droplet:
curl -fsSL https://github.com/dondada876/ASEAGI/raw/main/scripts/deploy.sh | bash

# Or manual:
cd /opt
git clone https://github.com/dondada876/ASEAGI.git
cd ASEAGI
./scripts/setup.sh
```

---

**Next Action:** Create Digital Ocean droplet to deploy ASEAGI in production.
