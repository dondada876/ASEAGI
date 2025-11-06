# 🚀 Deploy to Digital Ocean - Complete Guide
**Self-Hosted Deployment for PROJ344 Dashboards**

---

## ✅ Why Digital Ocean?

**Advantages Over Streamlit Cloud:**
- ✅ Deploy **all 5 dashboards** as private
- ✅ **No sleep mode** - always on
- ✅ **Custom domains** with SSL
- ✅ Full **SSH access** and control
- ✅ **Docker containerization**
- 💰 **$12/month** vs $250/month Streamlit Teams

---

## 📋 Prerequisites

### 1. Digital Ocean Account
- Sign up at https://www.digitalocean.com
- Add payment method
- Get $200 free credit (60 days)

### 2. SSH Keys (Required)
```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519_digitalocean

# Display public key (copy this)
cat ~/.ssh/id_ed25519_digitalocean.pub
```

### 3. Local Tools
```bash
# Install doctl (Digital Ocean CLI)
brew install doctl

# Install docker (if not already)
brew install docker

# Verify installations
doctl version
docker --version
```

---

## 🖥️ Step 1: Create a Droplet

### Option A: Via Web Console (Easiest)

1. Go to https://cloud.digitalocean.com
2. Click **"Create"** → **"Droplets"**
3. **Choose Image:** Ubuntu 24.04 (LTS) x64
4. **Choose Plan:**
   - **Basic** (recommended for start)
   - **Regular** (not Premium)
   - **$12/month:** 2GB RAM / 1 CPU / 50GB SSD / 2TB transfer
5. **Choose Region:** San Francisco 3 (or closest to you)
6. **Authentication:** Select your SSH key
   - Click "New SSH Key"
   - Paste public key from `~/.ssh/id_ed25519_digitalocean.pub`
   - Name it: "proj344-macbook"
7. **Hostname:** `proj344-dashboards`
8. **Tags:** `proj344`, `legal`, `dashboards`
9. Click **"Create Droplet"** 🚀

### Option B: Via CLI

```bash
# Authenticate doctl
doctl auth init

# Add SSH key to Digital Ocean
doctl compute ssh-key import proj344-macbook --public-key-file ~/.ssh/id_ed25519_digitalocean.pub

# Create droplet
doctl compute droplet create proj344-dashboards \
  --image ubuntu-24-04-x64 \
  --size s-2vcpu-2gb \
  --region sfo3 \
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header) \
  --tag-names proj344,legal,dashboards \
  --wait
```

**Wait 60 seconds** for droplet to fully boot.

---

## 🔌 Step 2: Connect to Your Droplet

```bash
# Get droplet IP address
doctl compute droplet list --format Name,PublicIPv4

# Connect via SSH (replace with your IP)
ssh -i ~/.ssh/id_ed25519_digitalocean root@YOUR_DROPLET_IP

# Example:
# ssh -i ~/.ssh/id_ed25519_digitalocean root@147.182.XXX.XXX
```

You should see:
```
Welcome to Ubuntu 24.04 LTS (GNU/Linux 5.15.0-76-generic x86_64)
```

---

## 🐳 Step 3: Install Docker on Droplet

Run these commands on your droplet:

```bash
# Update system packages
apt update && apt upgrade -y

# Install required packages
apt install -y apt-transport-https ca-certificates curl software-properties-common

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
```

---

## 📦 Step 4: Deploy Your Dashboards

### 4.1: Clone Repository on Droplet

```bash
# Install git
apt install -y git

# Clone your repository
cd /opt
git clone https://github.com/dondada876/proj344-dashboards.git
cd proj344-dashboards

# Verify files
ls -la
```

### 4.2: Create Environment File

```bash
# Create .env file with secrets
nano .env
```

Paste this configuration:
```env
# Supabase Configuration
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c

# Dashboard Passwords (Change these!)
MASTER_PASSWORD=Ashe2024Bucknor!
LEGAL_PASSWORD=Justice2024Legal!
CEO_PASSWORD=Proj344CEO!
TIMELINE_PASSWORD=Timeline2024!
MONITOR_PASSWORD=Monitor2024!

# Case Information
CASE_ID=ashe-bucknor-j24-00478
DOCKET_NUMBER=J24-00478
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### 4.3: Update docker-compose.yml

```bash
nano docker-compose.yml
```

Replace with this production configuration:

```yaml
version: '3.8'

services:
  # Master Dashboard (Most Sensitive)
  proj344-master:
    build: .
    container_name: proj344-master
    restart: unless-stopped
    ports:
      - "8501:8501"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - DASHBOARD_PASSWORD=${MASTER_PASSWORD}
    command: streamlit run dashboards/proj344_master_dashboard.py --server.port=8501 --server.headless=true
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Scanning Monitor
  scanning-monitor:
    build: .
    container_name: scanning-monitor
    restart: unless-stopped
    ports:
      - "8502:8502"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - DASHBOARD_PASSWORD=${MONITOR_PASSWORD}
    command: streamlit run dashboards/enhanced_scanning_monitor.py --server.port=8502 --server.headless=true
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8502"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Legal Intelligence Dashboard
  legal-intel:
    build: .
    container_name: legal-intel
    restart: unless-stopped
    ports:
      - "8503:8503"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - DASHBOARD_PASSWORD=${LEGAL_PASSWORD}
    command: streamlit run dashboards/legal_intelligence_dashboard.py --server.port=8503 --server.headless=true
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8503"]
      interval: 30s
      timeout: 10s
      retries: 3

  # CEO Dashboard
  ceo-dashboard:
    build: .
    container_name: ceo-dashboard
    restart: unless-stopped
    ports:
      - "8504:8504"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - DASHBOARD_PASSWORD=${CEO_PASSWORD}
    command: streamlit run dashboards/ceo_dashboard.py --server.port=8504 --server.headless=true
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8504"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Timeline & Violations Dashboard
  timeline-dashboard:
    build: .
    container_name: timeline-dashboard
    restart: unless-stopped
    ports:
      - "8505:8505"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - DASHBOARD_PASSWORD=${TIMELINE_PASSWORD}
    command: streamlit run dashboards/timeline_violations_dashboard.py --server.port=8505 --server.headless=true
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8505"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  logs:
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### 4.4: Build and Start Containers

```bash
# Build Docker images
docker compose build

# Start all dashboards
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

---

## 🌐 Step 5: Configure Firewall

```bash
# Install UFW firewall
apt install -y ufw

# Allow SSH
ufw allow 22/tcp

# Allow HTTP & HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow dashboard ports (for testing)
ufw allow 8501:8505/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

---

## 🔒 Step 6: Set Up Nginx Reverse Proxy (Optional but Recommended)

### 6.1: Install Nginx

```bash
apt install -y nginx

# Start nginx
systemctl start nginx
systemctl enable nginx
```

### 6.2: Configure Nginx

```bash
# Create nginx config
nano /etc/nginx/sites-available/proj344
```

Paste this configuration:

```nginx
# Master Dashboard
server {
    listen 80;
    server_name master.proj344.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Scanning Monitor
server {
    listen 80;
    server_name monitor.proj344.com;

    location / {
        proxy_pass http://localhost:8502;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Legal Intelligence
server {
    listen 80;
    server_name legal.proj344.com;

    location / {
        proxy_pass http://localhost:8503;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}

# CEO Dashboard
server {
    listen 80;
    server_name ceo.proj344.com;

    location / {
        proxy_pass http://localhost:8504;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}

# Timeline Dashboard
server {
    listen 80;
    server_name timeline.proj344.com;

    location / {
        proxy_pass http://localhost:8505;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Save and enable:

```bash
# Enable config
ln -s /etc/nginx/sites-available/proj344 /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Restart nginx
systemctl restart nginx
```

---

## 🔐 Step 7: Install SSL Certificates (HTTPS)

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get SSL certificates (replace with your domains)
certbot --nginx -d master.proj344.com -d monitor.proj344.com -d legal.proj344.com -d ceo.proj344.com -d timeline.proj344.com

# Follow prompts:
# - Enter email: your_email@example.com
# - Agree to terms: Y
# - Share email: N (optional)
# - Redirect HTTP to HTTPS: 2 (Yes)

# Verify auto-renewal
certbot renew --dry-run
```

---

## 🌍 Step 8: Configure DNS (Domain Setup)

### If You Have a Domain:

1. Go to your domain registrar (Namecheap, GoDaddy, etc.)
2. Add these A records:

```
master.proj344.com    → YOUR_DROPLET_IP
monitor.proj344.com   → YOUR_DROPLET_IP
legal.proj344.com     → YOUR_DROPLET_IP
ceo.proj344.com       → YOUR_DROPLET_IP
timeline.proj344.com  → YOUR_DROPLET_IP
```

### Without a Domain (Use IP):

Access dashboards directly:
```
http://YOUR_DROPLET_IP:8501  (Master)
http://YOUR_DROPLET_IP:8502  (Monitor)
http://YOUR_DROPLET_IP:8503  (Legal)
http://YOUR_DROPLET_IP:8504  (CEO)
http://YOUR_DROPLET_IP:8505  (Timeline)
```

---

## ✅ Step 9: Verify Deployment

```bash
# Check all containers are running
docker compose ps

# Should show 5 containers as "Up"

# Check logs for errors
docker compose logs proj344-master
docker compose logs scanning-monitor
docker compose logs legal-intel
docker compose logs ceo-dashboard
docker compose logs timeline-dashboard

# Test each dashboard
curl http://localhost:8501
curl http://localhost:8502
curl http://localhost:8503
curl http://localhost:8504
curl http://localhost:8505
```

---

## 🔄 Automated Deployment Script

Create a deployment script for easy updates:

```bash
nano /opt/proj344-dashboards/deploy.sh
```

```bash
#!/bin/bash
# PROJ344 Dashboard Deployment Script

echo "🚀 PROJ344 Dashboard Deployment"
echo "================================"

# Navigate to project directory
cd /opt/proj344-dashboards

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Rebuild containers
echo "🐳 Rebuilding Docker images..."
docker compose build

# Restart containers
echo "♻️  Restarting containers..."
docker compose down
docker compose up -d

# Check status
echo "✅ Checking container status..."
docker compose ps

# View logs
echo "📊 Viewing logs (Ctrl+C to exit)..."
docker compose logs -f
```

Make executable:
```bash
chmod +x /opt/proj344-dashboards/deploy.sh
```

Deploy updates anytime:
```bash
/opt/proj344-dashboards/deploy.sh
```

---

## 🛡️ Security Best Practices

### 1. Disable Root Login

```bash
# Create a new user
adduser proj344admin
usermod -aG sudo proj344admin
usermod -aG docker proj344admin

# Copy SSH keys
rsync --archive --chown=proj344admin:proj344admin ~/.ssh /home/proj344admin

# Test SSH with new user
# ssh proj344admin@YOUR_DROPLET_IP

# Disable root SSH login
nano /etc/ssh/sshd_config
# Change: PermitRootLogin no
systemctl restart sshd
```

### 2. Install Fail2Ban

```bash
apt install -y fail2ban

# Configure fail2ban
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
systemctl enable fail2ban
systemctl start fail2ban
```

### 3. Set Up Automatic Updates

```bash
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

### 4. Configure Backups

```bash
# Install Digital Ocean backup agent
snap install doctl
doctl compute droplet-action snapshot YOUR_DROPLET_ID --snapshot-name "proj344-backup-$(date +%Y%m%d)"
```

---

## 📊 Monitoring & Maintenance

### View Container Logs

```bash
# All containers
docker compose logs -f

# Specific container
docker compose logs -f proj344-master

# Last 100 lines
docker compose logs --tail=100 scanning-monitor
```

### Restart Containers

```bash
# Restart all
docker compose restart

# Restart specific
docker compose restart proj344-master
```

### Update Dashboards

```bash
cd /opt/proj344-dashboards
git pull
docker compose build
docker compose up -d
```

### Check Resource Usage

```bash
# Container stats
docker stats

# System resources
htop  # (install: apt install htop)

# Disk usage
df -h
docker system df
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs container-name

# Rebuild image
docker compose build container-name --no-cache
docker compose up -d container-name
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8501

# Kill process
kill -9 PID
```

### Out of Disk Space

```bash
# Clean Docker
docker system prune -a

# Clean logs
truncate -s 0 /var/log/*.log
```

### Can't Connect to Droplet

```bash
# Check firewall
ufw status

# Check SSH service
systemctl status sshd

# Use Digital Ocean console
# https://cloud.digitalocean.com/droplets → Click droplet → "Console"
```

---

## 💰 Cost Optimization

### Monitor Usage

```bash
# Check bandwidth usage
vnstat -h  # (install: apt install vnstat)

# Check droplet metrics
doctl compute droplet get YOUR_DROPLET_ID --format Name,Memory,Disk,Bandwidth
```

### Resize Droplet

If you need more power:
```bash
doctl compute droplet-action resize YOUR_DROPLET_ID --size s-4vcpu-8gb
```

---

## ✅ Deployment Checklist

- [ ] Digital Ocean account created
- [ ] SSH keys generated and added
- [ ] Droplet created (Ubuntu 24.04)
- [ ] Docker installed on droplet
- [ ] Repository cloned to /opt
- [ ] .env file created with secrets
- [ ] docker-compose.yml updated
- [ ] Containers built and started
- [ ] Firewall configured (UFW)
- [ ] Nginx installed (optional)
- [ ] SSL certificates installed (optional)
- [ ] DNS records configured (optional)
- [ ] All 5 dashboards accessible
- [ ] Security hardening complete
- [ ] Backup strategy implemented

---

## 🎉 Success!

Your dashboards are now live on Digital Ocean!

**Access URLs (with domain):**
- https://master.proj344.com
- https://monitor.proj344.com
- https://legal.proj344.com
- https://ceo.proj344.com
- https://timeline.proj344.com

**Or (with IP only):**
- http://YOUR_IP:8501 (Master)
- http://YOUR_IP:8502 (Monitor)
- http://YOUR_IP:8503 (Legal)
- http://YOUR_IP:8504 (CEO)
- http://YOUR_IP:8505 (Timeline)

---

## 📞 Support Resources

- **Digital Ocean Docs:** https://docs.digitalocean.com
- **Docker Documentation:** https://docs.docker.com
- **Nginx Documentation:** https://nginx.org/en/docs/
- **Certbot Documentation:** https://certbot.eff.org
- **PROJ344 Repository:** https://github.com/dondada876/proj344-dashboards

---

**For Ashe. For Justice. For All Children.** 🛡️
