# PROJ344 Dashboard Deployment Guide

## 🌐 Deployment Options

### Option 1: Streamlit Community Cloud (Recommended - Free)

**Best for:** Quick deployment, free hosting, easy updates

#### Steps:

1. **Push to GitHub**
```bash
cd proj344-dashboards
git init
git add .
git commit -m "Initial commit: PROJ344 dashboards"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/proj344-dashboards.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Click "New app"
- Connect your GitHub account
- Select repository: `proj344-dashboards`
- Select branch: `main`
- Select main file: `dashboards/proj344_master_dashboard.py`
- Click "Deploy"

3. **Add Secrets**
In Streamlit Cloud dashboard:
- Click "Settings" → "Secrets"
- Add:
```toml
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
ANTHROPIC_API_KEY = "your-anthropic-api-key"
```

4. **Deploy Other Dashboards**
Repeat for:
- `dashboards/legal_intelligence_dashboard.py`
- `dashboards/ceo_dashboard.py`

**URLs will be:**
- `https://YOUR_USERNAME-proj344-dashboards-proj344-master-dashboard.streamlit.app`
- `https://YOUR_USERNAME-proj344-dashboards-legal-intelligence-dashboard.streamlit.app`
- `https://YOUR_USERNAME-proj344-dashboards-ceo-dashboard.streamlit.app`

---

### Option 2: Heroku

**Best for:** Production deployments, custom domains

#### Steps:

1. **Install Heroku CLI**
```bash
brew install heroku/brew/heroku  # macOS
# or download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login and Create App**
```bash
heroku login
heroku create proj344-dashboard
```

3. **Set Environment Variables**
```bash
heroku config:set SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
heroku config:set SUPABASE_KEY=your-supabase-anon-key
heroku config:set ANTHROPIC_API_KEY=your-anthropic-api-key
```

4. **Deploy**
```bash
git push heroku main
```

5. **Open**
```bash
heroku open
```

**Cost:** Free tier available, $7/month for hobby tier

---

### Option 3: Docker + Any Cloud Provider

**Best for:** Full control, multiple cloud providers

#### Local Testing:

```bash
# Build image
docker build -t proj344-dashboards .

# Run single dashboard
docker run -p 8501:8501 \
  -e SUPABASE_URL=your-url \
  -e SUPABASE_KEY=your-key \
  proj344-dashboards

# Run all dashboards with docker-compose
docker-compose up -d
```

#### Deploy to Cloud:

**AWS ECS:**
```bash
# Push to ECR
aws ecr create-repository --repository-name proj344-dashboards
docker tag proj344-dashboards:latest YOUR_ECR_URL/proj344-dashboards:latest
docker push YOUR_ECR_URL/proj344-dashboards:latest

# Create ECS task and service (via AWS Console or CLI)
```

**Google Cloud Run:**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT/proj344-dashboards
gcloud run deploy proj344-dashboards \
  --image gcr.io/YOUR_PROJECT/proj344-dashboards \
  --platform managed \
  --set-env-vars SUPABASE_URL=your-url,SUPABASE_KEY=your-key
```

**DigitalOcean App Platform:**
- Connect GitHub repository
- Select Docker as runtime
- Set environment variables in UI
- Deploy

---

### Option 4: Railway.app

**Best for:** Easy deployment, generous free tier

#### Steps:

1. **Go to [railway.app](https://railway.app)**
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Select `proj344-dashboards`
5. Add environment variables in Settings
6. Deploy!

**Cost:** Free tier includes $5 credit/month

---

### Option 5: Render

**Best for:** Free tier, easy setup

#### Steps:

1. **Go to [render.com](https://render.com)**
2. Click "New" → "Web Service"
3. Connect GitHub repository
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run dashboards/proj344_master_dashboard.py --server.port=$PORT --server.address=0.0.0.0`
5. Add environment variables
6. Deploy

**Cost:** Free tier available

---

## 🔐 Security Best Practices

### Environment Variables

**NEVER commit:**
- Actual API keys
- Database credentials
- `.env` files with real values

**ALWAYS:**
- Use `.env.example` as template
- Set secrets in deployment platform UI
- Use environment variables in code

### Database Security

1. **Enable Row Level Security (RLS) in Supabase**
```sql
ALTER TABLE legal_documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow authenticated access" ON legal_documents
FOR ALL USING (auth.role() = 'authenticated');
```

2. **Use Anon Key (Public)**
- Safe to use in client-side apps
- Respects RLS policies

3. **Service Role Key (Private)**
- Only use server-side
- Never expose in client code

### Rate Limiting

For public deployments, add rate limiting:

```python
import streamlit as st
from functools import wraps
import time

def rate_limit(max_calls=10, time_window=60):
    calls = []
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - time_window]
            if len(calls) >= max_calls:
                st.error("Too many requests. Please wait.")
                return None
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## 🚀 CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run tests
        run: |
          python -m pytest tests/

      - name: Deploy to Streamlit
        # Streamlit Cloud auto-deploys on push to main
        run: echo "Deployed to Streamlit Cloud"
```

---

## 📊 Monitoring

### Streamlit Cloud
- Built-in logs and metrics
- View at: App → "Manage app" → "Logs"

### Heroku
```bash
heroku logs --tail -a proj344-dashboard
```

### Docker
```bash
docker logs -f container_name
```

### Custom Monitoring

Add to dashboard code:

```python
import streamlit as st
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log page views
logger.info(f"Page view: {st.session_state.get('page', 'home')}")

# Log errors
try:
    # Your code
except Exception as e:
    logger.error(f"Error: {e}")
    st.error("Something went wrong. Please try again.")
```

---

## 🔧 Troubleshooting

### Deployment Fails

**Issue:** Build fails on deployment

**Solutions:**
1. Check requirements.txt for incompatible versions
2. Verify Python version compatibility
3. Check logs for specific errors

### Environment Variables Not Loading

**Issue:** Dashboard can't connect to Supabase

**Solutions:**
1. Verify variables are set in platform UI
2. Check variable names match exactly
3. Restart deployment after setting variables

### Port Issues

**Issue:** Port already in use

**Solutions:**
```bash
# Find process using port
lsof -ti :8501 | xargs kill -9

# Or use different port
streamlit run dashboard.py --server.port 8504
```

### Memory Issues

**Issue:** Dashboard crashes due to memory

**Solutions:**
1. Increase instance size (if on paid tier)
2. Optimize queries (use LIMIT)
3. Cache data with TTL
4. Paginate large results

---

## 📈 Scaling

### Horizontal Scaling

**Load Balancer + Multiple Instances:**
```
                    ┌─ Instance 1 (8501)
Load Balancer  ─────┼─ Instance 2 (8501)
                    └─ Instance 3 (8501)
```

### Vertical Scaling

**Increase Resources:**
- RAM: 512MB → 2GB → 4GB
- CPU: 1 core → 2 cores → 4 cores

### Database Optimization

**Supabase Performance:**
1. Add indexes to frequently queried columns
2. Use materialized views for complex queries
3. Enable query caching
4. Upgrade to paid tier for better performance

---

## 🌍 Custom Domain

### Streamlit Cloud (Pro)
- Upgrade to Pro plan
- Add custom domain in settings

### Heroku
```bash
heroku domains:add www.proj344.com -a proj344-dashboard
# Follow DNS setup instructions
```

### Cloudflare (Recommended)
1. Add site to Cloudflare
2. Point CNAME to deployment URL
3. Enable SSL/TLS
4. Set up caching rules

---

## ✅ Post-Deployment Checklist

- [ ] Environment variables set correctly
- [ ] Database connections working
- [ ] All dashboards accessible
- [ ] SSL/HTTPS enabled
- [ ] Monitoring configured
- [ ] Backups enabled (Supabase)
- [ ] Error tracking set up
- [ ] Documentation updated with URLs
- [ ] Team has access credentials
- [ ] Rate limiting configured (if public)

---

**For questions or issues, see main README.md or open an issue on GitHub.**
