# DigitalOcean Deployment Guide - ASEAGI Telegram Bot + Full Stack

**Complete deployment guide for ASEAGI multi-channel system on DigitalOcean**

---

## 🎯 What You're Deploying

Your complete ASEAGI case management system with:

```
┌─────────────────────────────────────────────────────────────┐
│                 DigitalOcean Droplet                        │
├─────────────────────────────────────────────────────────────┤
│  ✅ FastAPI (Telegram endpoints + shared service layer)     │
│  ✅ Telegram Bot (polling mode, always running)             │
│  ✅ Streamlit Dashboards (analytics, timeline, violations)  │
│  ✅ n8n (automation: daily reports, deadline alerts)        │
│  ✅ Qdrant (vector database for semantic search)            │
│  ✅ Neo4j (graph database for relationships)                │
│  ✅ Redis (caching and queues)                              │
│  ✅ Nginx (reverse proxy with SSL)                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ┌──────────────┐
                    │   Supabase   │
                    │   (Database) │
                    └──────────────┘
```

---

## 💰 Cost Analysis

### **Recommended Droplet Sizes**

#### **Option 1: Starter (MVP Testing)**
- **Plan:** Basic Droplet
- **RAM:** 8GB
- **CPU:** 4 vCPUs
- **Storage:** 160GB SSD
- **Bandwidth:** 5TB
- **Cost:** $48/month
- **Best for:** Testing, low usage (< 100 Telegram queries/day)

#### **Option 2: Production (Recommended)** ✅
- **Plan:** Basic Droplet
- **RAM:** 16GB
- **CPU:** 8 vCPUs
- **Storage:** 320GB SSD
- **Bandwidth:** 6TB
- **Cost:** $96/month
- **Best for:** Production use, moderate traffic (500+ Telegram queries/day)

#### **Option 3: High Performance**
- **Plan:** CPU-Optimized Droplet
- **RAM:** 32GB
- **CPU:** 16 vCPUs
- **Storage:** 640GB SSD
- **Bandwidth:** 7TB
- **Cost:** $192/month
- **Best for:** Heavy usage, multiple users, large document sets

### **Total Monthly Costs**

| Component | Cost |
|-----------|------|
| DigitalOcean Droplet (16GB) | $96/month |
| Supabase (Free tier) | $0/month |
| Telegram Bot API | $0/month |
| Domain name (optional) | $12/year |
| **Total** | **~$96-100/month** |

### **Why DigitalOcean?**

✅ **Simple:** One droplet, one monthly bill
✅ **Reliable:** 99.99% uptime SLA
✅ **Fast:** All services on same machine = low latency
✅ **Portable:** Can migrate to any host later
✅ **Cost-effective:** $96/month vs $300+ on AWS/GCP

---

## 🚀 Deployment Steps (45 minutes)

### **Prerequisites**

- [ ] DigitalOcean account (use this link for $200 credit: https://m.do.co/c/your-referral-code)
- [ ] Telegram bot token from @BotFather
- [ ] Supabase credentials
- [ ] Domain name (optional, for SSL)

---

### **Step 1: Create DigitalOcean Droplet (5 minutes)**

1. **Go to DigitalOcean Dashboard:**
   - https://cloud.digitalocean.com/

2. **Create Droplet:**
   - Click "Create" → "Droplets"

3. **Choose Configuration:**

   **Region:** Choose closest to you
   - San Francisco (USA West)
   - New York (USA East)
   - London (Europe)
   - Singapore (Asia)

   **Image:** Ubuntu 22.04 LTS x64

   **Droplet Type:** Basic

   **CPU Options:** Regular Intel
   - Select: **16GB / 8 CPUs / 320GB SSD / 6TB transfer** ($96/month)

   **Authentication:**
   - ✅ SSH Key (recommended - [setup guide](https://docs.digitalocean.com/products/droplets/how-to/add-ssh-keys/))
   - OR Password (less secure)

   **Hostname:** `aseagi-production`

4. **Click "Create Droplet"**

5. **Wait 60 seconds** for droplet to provision

6. **Copy IP Address** (e.g., `165.232.XXX.XXX`)

---

### **Step 2: Initial Server Setup (10 minutes)**

**Connect to your droplet:**

```bash
ssh root@YOUR_DROPLET_IP
```

**Update system:**

```bash
apt-get update && apt-get upgrade -y
```

**Install Docker:**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt-get install -y docker-compose

# Verify installation
docker --version
docker-compose --version
```

**Setup firewall:**

```bash
# Allow SSH (IMPORTANT - don't lock yourself out!)
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow API (for testing)
ufw allow 8000/tcp

# Allow n8n
ufw allow 5678/tcp

# Allow Qdrant (optional, for external access)
ufw allow 6333/tcp

# Allow Neo4j Browser (optional)
ufw allow 7474/tcp

# Enable firewall
ufw --force enable

# Check status
ufw status
```

**Create swap space (prevents out-of-memory):**

```bash
# Create 4GB swap
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab

# Verify
free -h
```

---

### **Step 3: Clone Repository and Configure (5 minutes)**

**Clone your ASEAGI repository:**

```bash
cd /root
git clone https://github.com/dondada876/ASEAGI.git
cd ASEAGI

# Or if you prefer a different location:
cd /opt
git clone https://github.com/dondada876/ASEAGI.git
cd ASEAGI
```

**Create environment configuration:**

```bash
nano .env
```

**Paste this configuration** (update with your real values):

```bash
# Supabase (REQUIRED)
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=your-actual-supabase-anon-key-here

# Telegram Bot (REQUIRED)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# API Keys (OPTIONAL - for AI features)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Redis (set strong password)
REDIS_PASSWORD=$(openssl rand -base64 32)

# Neo4j (set strong password)
NEO4J_PASSWORD=$(openssl rand -base64 32)

# n8n (set credentials)
N8N_USER=admin
N8N_PASSWORD=$(openssl rand -base64 32)

# Domain (optional - use your IP if no domain)
DOMAIN=YOUR_DROPLET_IP

# Timezone
TIMEZONE=America/Los_Angeles
```

**Generate secure passwords:**

```bash
# This will show random passwords - copy them to .env
echo "REDIS_PASSWORD=$(openssl rand -base64 32)"
echo "NEO4J_PASSWORD=$(openssl rand -base64 32)"
echo "N8N_PASSWORD=$(openssl rand -base64 32)"
```

**Save the file:**
- Press `Ctrl+X`
- Press `Y`
- Press `Enter`

---

### **Step 4: Deploy with Docker Compose (10 minutes)**

**Start all services:**

```bash
cd /root/ASEAGI  # or /opt/ASEAGI

# Start in detached mode
docker-compose -f docker-compose.full.yml up -d

# This will:
# 1. Pull Docker images (may take 5-10 minutes first time)
# 2. Build custom images (API, Telegram bot)
# 3. Start all 8 containers
# 4. Setup networking
```

**Watch the logs (in another terminal):**

```bash
# Follow all logs
docker-compose -f docker-compose.full.yml logs -f

# Or specific service
docker logs -f aseagi-telegram
docker logs -f aseagi-api
```

**Check container status:**

```bash
docker-compose -f docker-compose.full.yml ps
```

Expected output:
```
NAME                STATUS              PORTS
aseagi-api          Up (healthy)        0.0.0.0:8000->8000/tcp
aseagi-telegram     Up
aseagi-dashboard    Up (healthy)        0.0.0.0:80->8501/tcp
aseagi-n8n          Up (healthy)        0.0.0.0:5678->5678/tcp
aseagi-qdrant       Up (healthy)        0.0.0.0:6333->6333/tcp
aseagi-neo4j        Up (healthy)        0.0.0.0:7474->7474/tcp, 7687/tcp
aseagi-redis        Up (healthy)        0.0.0.0:6379->6379/tcp
aseagi-nginx        Up (healthy)        0.0.0.0:443->443/tcp
```

---

### **Step 5: Verify Deployment (5 minutes)**

**Test API:**

```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "healthy",
  "service": "ASEAGI API",
  "environment": {
    "supabase_configured": true,
    "telegram_configured": true
  }
}
```

**Test from your computer:**

```bash
curl http://YOUR_DROPLET_IP:8000/health
```

**Test Telegram Bot:**

1. Open Telegram on your phone
2. Search for your bot (the name you gave @BotFather)
3. Send `/start` command
4. You should receive welcome message

**Test Streamlit Dashboard:**

Open browser: `http://YOUR_DROPLET_IP`

**Test n8n:**

Open browser: `http://YOUR_DROPLET_IP:5678`
- Username: admin (or what you set in .env)
- Password: (check your .env file)

**Test Neo4j Browser:**

Open browser: `http://YOUR_DROPLET_IP:7474`
- Username: neo4j
- Password: (check your .env NEO4J_PASSWORD)

**Test Qdrant:**

```bash
curl http://YOUR_DROPLET_IP:6333/collections
```

---

### **Step 6: Setup Domain and SSL (Optional, 10 minutes)**

**If you have a domain name:**

1. **Point domain to droplet:**
   - Go to your domain registrar (Namecheap, GoDaddy, etc.)
   - Add A record: `aseagi.yourdomain.com` → `YOUR_DROPLET_IP`
   - Wait 5-10 minutes for DNS propagation

2. **Install Certbot (Let's Encrypt SSL):**

```bash
apt-get install -y certbot python3-certbot-nginx
```

3. **Get SSL certificate:**

```bash
certbot --nginx -d aseagi.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose: Redirect HTTP to HTTPS (option 2)
```

4. **Update .env with your domain:**

```bash
nano .env
# Change: DOMAIN=aseagi.yourdomain.com
```

5. **Restart services:**

```bash
docker-compose -f docker-compose.full.yml restart
```

**Now access via HTTPS:**
- API: `https://aseagi.yourdomain.com:8000`
- Dashboard: `https://aseagi.yourdomain.com`
- n8n: `https://aseagi.yourdomain.com:5678`

---

## 📱 Using Your Deployed System

### **Telegram Bot Commands**

From anywhere in the world, send commands to your bot:

```
/search Cal OES 2-925        → Search communications
/timeline 60                 → Show last 60 days
/actions                     → Show pending tasks
/violations                  → Show legal violations
/deadline                    → Show upcoming deadlines
/report                      → Daily summary
/hearing                     → Show hearings
/motion reconsideration "issue" → Generate motion
```

### **Streamlit Dashboard**

Access from any device: `http://YOUR_DROPLET_IP` or `https://aseagi.yourdomain.com`

Available dashboards:
- CEO Global Dashboard
- Court Events Timeline
- Truth Score Dashboard
- Legal Intelligence
- Queue Monitor
- Violations Tracker

### **n8n Automation**

Access: `http://YOUR_DROPLET_IP:5678`

**Example workflows to create:**

1. **Daily Report (every morning at 8 AM):**
   ```
   Schedule Trigger → HTTP Request (GET /telegram/report) → Telegram Send Message
   ```

2. **Deadline Alert (every day at 9 AM):**
   ```
   Schedule Trigger → HTTP Request (GET /telegram/deadline) →
   Filter (if deadlines < 3 days) → Telegram Send Alert
   ```

3. **New Violation Alert (real-time):**
   ```
   Webhook Trigger → HTTP Request (GET /telegram/violations?severity=critical) →
   Telegram Send Message
   ```

### **API Access**

For custom integrations:

```bash
# Base URL
API_URL="http://YOUR_DROPLET_IP:8000"

# Search communications
curl "$API_URL/telegram/search" -X POST -H "Content-Type: application/json" \
  -d '{"query": "visitation denial", "limit": 10}'

# Get timeline
curl "$API_URL/telegram/timeline?days=30"

# Get action items
curl "$API_URL/telegram/actions?priority=urgent"
```

**API Docs:**
- Swagger UI: `http://YOUR_DROPLET_IP:8000/docs`
- ReDoc: `http://YOUR_DROPLET_IP:8000/redoc`

---

## 🔧 Management & Maintenance

### **View Logs**

```bash
# All services
docker-compose -f docker-compose.full.yml logs -f

# Specific service
docker logs -f aseagi-telegram
docker logs -f aseagi-api

# Last 100 lines
docker logs --tail 100 aseagi-telegram
```

### **Restart Services**

```bash
# Restart all
docker-compose -f docker-compose.full.yml restart

# Restart specific service
docker-compose -f docker-compose.full.yml restart telegram
docker-compose -f docker-compose.full.yml restart api
```

### **Stop Services**

```bash
# Stop all
docker-compose -f docker-compose.full.yml stop

# Stop specific service
docker-compose -f docker-compose.full.yml stop telegram
```

### **Update Code**

```bash
cd /root/ASEAGI  # or /opt/ASEAGI

# Pull latest code
git pull origin claude/create-truth-score-charts-011CUqV28kW1jcpJE1z2B5rM

# Rebuild and restart
docker-compose -f docker-compose.full.yml up -d --build
```

### **Check Resource Usage**

```bash
# Docker stats
docker stats

# System resources
htop

# Disk space
df -h

# Memory
free -h
```

### **Backup Data**

```bash
# Backup Docker volumes
docker run --rm -v aseagi_neo4j-data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data

# Backup Redis
docker exec aseagi-redis redis-cli -a $REDIS_PASSWORD SAVE

# Backup n8n workflows
docker exec aseagi-n8n cp -r /home/node/.n8n /backup/n8n-$(date +%Y%m%d)

# Backup .env (contains passwords!)
cp .env .env.backup-$(date +%Y%m%d)
```

**Supabase backup:**
- Go to Supabase dashboard
- Database → Backups
- Daily automatic backups included

---

## 🚨 Troubleshooting

### **Problem: Telegram bot not responding**

**Check bot is running:**
```bash
docker ps | grep telegram
```

**Check bot logs:**
```bash
docker logs aseagi-telegram
```

**Common issues:**
- Wrong bot token → Check .env TELEGRAM_BOT_TOKEN
- API not accessible → Check `docker logs aseagi-api`
- Network issue → Check `docker network ls`

**Fix:**
```bash
# Restart bot
docker-compose -f docker-compose.full.yml restart telegram

# Or rebuild
docker-compose -f docker-compose.full.yml up -d --build telegram
```

### **Problem: API returns 500 errors**

**Check API logs:**
```bash
docker logs aseagi-api | tail -50
```

**Common issues:**
- Supabase connection failed → Check SUPABASE_URL and SUPABASE_KEY
- Missing environment variable → Check .env file
- Database schema not deployed → Deploy schemas (see below)

**Fix:**
```bash
# Restart API
docker-compose -f docker-compose.full.yml restart api

# Check Supabase connection
curl -H "apikey: YOUR_SUPABASE_KEY" \
  https://jvjlhxodmbkodzmggwpu.supabase.co/rest/v1/
```

### **Problem: Out of memory**

**Check memory usage:**
```bash
free -h
docker stats
```

**Common issues:**
- Neo4j using too much RAM
- Too many concurrent requests

**Fix:**
```bash
# Option 1: Add more swap
fallocate -l 8G /swapfile2
chmod 600 /swapfile2
mkswap /swapfile2
swapon /swapfile2

# Option 2: Reduce Neo4j memory
nano docker-compose.full.yml
# Find neo4j section, reduce heap_max_size to 1G

# Option 3: Upgrade droplet
# Go to DigitalOcean dashboard → Resize → Select 32GB
```

### **Problem: Can't connect to services from internet**

**Check firewall:**
```bash
ufw status
```

**Check containers are running:**
```bash
docker-compose -f docker-compose.full.yml ps
```

**Check port bindings:**
```bash
netstat -tulpn | grep LISTEN
```

**Fix:**
```bash
# Open required ports
ufw allow 8000/tcp  # API
ufw allow 80/tcp    # Dashboard
ufw allow 5678/tcp  # n8n

# Reload firewall
ufw reload
```

### **Problem: Docker containers keep restarting**

**Check logs:**
```bash
docker-compose -f docker-compose.full.yml logs --tail 100
```

**Common issues:**
- Missing environment variables
- Port conflicts
- Insufficient memory

**Fix:**
```bash
# Stop everything
docker-compose -f docker-compose.full.yml down

# Start one by one to identify issue
docker-compose -f docker-compose.full.yml up redis
docker-compose -f docker-compose.full.yml up qdrant
docker-compose -f docker-compose.full.yml up neo4j
docker-compose -f docker-compose.full.yml up api
docker-compose -f docker-compose.full.yml up telegram
```

---

## 📊 Monitoring & Alerts

### **Setup Monitoring (recommended)**

**1. DigitalOcean Monitoring (built-in, free):**
- Go to droplet page
- Click "Monitoring"
- Enable alerts for:
  - CPU > 80%
  - Memory > 90%
  - Disk > 90%

**2. Uptime Monitoring:**

Use a service like UptimeRobot (free):
- Monitor: `http://YOUR_DROPLET_IP:8000/health`
- Alert via email/Telegram if down

**3. Log Management:**

Send logs to external service:
```bash
# Install Logrotate
apt-get install logrotate

# Configure rotation
cat > /etc/logrotate.d/docker-logs <<EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    missingok
    delaycompress
    copytruncate
}
EOF
```

---

## 🔐 Security Hardening

### **1. SSH Security**

```bash
# Disable root login (after creating sudo user)
nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
# Set: PasswordAuthentication no

# Restart SSH
systemctl restart ssh
```

### **2. Install Fail2Ban**

```bash
apt-get install -y fail2ban

# Configure
cat > /etc/fail2ban/jail.local <<EOF
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600
EOF

systemctl restart fail2ban
```

### **3. Secure Telegram Bot**

Add admin-only access in `/root/ASEAGI/api-service/telegram_bot.py`:

```python
# Get your Telegram user ID from @userinfobot
ALLOWED_USER_IDS = [123456789]  # Your user ID

async def is_admin(update: Update) -> bool:
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return False
    return True

# Add to each command handler:
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    # ... rest of handler
```

Rebuild:
```bash
docker-compose -f docker-compose.full.yml up -d --build telegram
```

### **4. API Authentication (Optional)**

For production, add API key authentication to protect endpoints.

---

## 📈 Performance Optimization

### **1. Enable Redis Caching**

Uncomment caching in `services.py`:
```python
# Cache timeline queries for 5 minutes
@cache.memoize(timeout=300)
def get_timeline(...):
    ...
```

### **2. Database Indexes**

Ensure indexes exist on Supabase:
```sql
-- Run in Supabase SQL Editor
CREATE INDEX IF NOT EXISTS idx_communications_sender ON communications(sender);
CREATE INDEX IF NOT EXISTS idx_communications_sent_date ON communications(sent_date);
CREATE INDEX IF NOT EXISTS idx_events_event_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_action_items_due_date ON action_items(due_date);
CREATE INDEX IF NOT EXISTS idx_violations_severity ON violations(severity);
```

### **3. Nginx Caching**

Configure nginx to cache static responses (if using nginx container).

---

## 💡 Pro Tips

### **Save Money:**

1. **Use snapshots for backups** ($0.05/GB vs $2.40/month for automatic backups)
2. **Don't need Neo4j yet?** Comment it out in docker-compose to save RAM
3. **Use Supabase free tier** (sufficient for most use cases)
4. **Setup auto-scaling alerts** to catch resource issues early

### **Improve Performance:**

1. **Use SSD volumes** for Neo4j and Qdrant (already included)
2. **Enable HTTP/2** in nginx for faster API responses
3. **Add CDN** (Cloudflare free tier) for dashboard assets

### **Development Workflow:**

1. **Test locally first** before deploying
2. **Use separate branch** for production
3. **Setup staging environment** (smaller droplet) for testing

---

## 📋 Deployment Checklist

### **Pre-Launch:**
- [ ] Droplet created (16GB recommended)
- [ ] Firewall configured
- [ ] Swap space added
- [ ] Repository cloned
- [ ] .env file configured with all credentials
- [ ] Docker and Docker Compose installed

### **Launch:**
- [ ] `docker-compose up -d` successful
- [ ] All containers healthy (check `docker ps`)
- [ ] API health check passes
- [ ] Telegram bot responds to `/start`
- [ ] Dashboard accessible
- [ ] n8n accessible

### **Post-Launch:**
- [ ] SSL certificate installed (if using domain)
- [ ] Monitoring enabled (DigitalOcean + UptimeRobot)
- [ ] Backups scheduled
- [ ] Admin-only access configured for Telegram bot
- [ ] Database schemas deployed (motion engine, queue, tiered analysis)
- [ ] Test all Telegram commands
- [ ] Create first n8n workflow (daily report)

### **Security:**
- [ ] SSH key authentication enabled
- [ ] Root login disabled
- [ ] Fail2Ban installed
- [ ] Strong passwords for Redis, Neo4j, n8n
- [ ] .env file secured (chmod 600)
- [ ] Firewall rules reviewed

---

## 🎯 Next Steps After Deployment

### **1. Deploy Database Schemas**

Your new system needs these schemas in Supabase:

```bash
# Connect to your droplet
ssh root@YOUR_DROPLET_IP
cd /root/ASEAGI

# Deploy queue system
./deploy_queue_schema.sh

# Or manually in Supabase SQL Editor:
# Copy and run: document_journal_queue_schema.sql
# Copy and run: tiered_analysis_schema.sql
# Copy and run: motion_engine_schema.sql
```

### **2. Create n8n Workflows**

Access n8n: `http://YOUR_DROPLET_IP:5678`

**Workflow 1: Daily Report**
- Trigger: Schedule (8:00 AM daily)
- HTTP Request: `GET http://api:8000/telegram/report`
- Telegram: Send message to your user ID

**Workflow 2: Deadline Alerts**
- Trigger: Schedule (9:00 AM daily)
- HTTP Request: `GET http://api:8000/telegram/deadline`
- Filter: Only if deadlines exist
- Telegram: Send alert

### **3. Add Initial Data**

Upload your case documents to start populating the system:
- Use mobile scanner
- Use desktop upload
- Bulk import from Google Drive

### **4. Test Motion Generation**

```
/motion reconsideration "Cal OES 2-925 verification failure"
```

---

## 📞 Support

### **DigitalOcean Support:**
- Docs: https://docs.digitalocean.com
- Community: https://www.digitalocean.com/community
- Support tickets (for paid customers)

### **ASEAGI System:**
- Documentation: All .md files in repository
- API Docs: `http://YOUR_DROPLET_IP:8000/docs`
- Logs: `docker logs aseagi-telegram`

---

## 🎬 Ready to Deploy!

**Quick Command Reference:**

```bash
# Deploy everything
ssh root@YOUR_DROPLET_IP
cd /root/ASEAGI
docker-compose -f docker-compose.full.yml up -d

# Check status
docker-compose -f docker-compose.full.yml ps

# View logs
docker-compose -f docker-compose.full.yml logs -f

# Test
curl http://YOUR_DROPLET_IP:8000/health
```

**Your system will be live at:**
- API: `http://YOUR_DROPLET_IP:8000`
- Dashboard: `http://YOUR_DROPLET_IP`
- n8n: `http://YOUR_DROPLET_IP:5678`
- Telegram: Message your bot from Telegram app

**For Ashe. For Justice. For All Children.** 🛡️

---

**Last Updated:** 2025-11-06
**Version:** 1.0.0
**Status:** Production Ready
