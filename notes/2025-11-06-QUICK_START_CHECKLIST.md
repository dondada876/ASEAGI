# QUICK START IMPLEMENTATION CHECKLIST

## 🚀 Day 1: Fix Telegram Bot (2-4 hours)

### Step 1: Create FastAPI Backend
```bash
cd /home/user/ASEAGI
mkdir -p api
cd api

# Create main.py (copy from ASEAGI_COMPLETE_SOLUTION.md)
nano main.py

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
supabase==2.0.3
anthropic==0.7.8
python-multipart==0.0.6
EOF
```

### Step 2: Update Docker Compose
```bash
cd /home/user/ASEAGI

# Create docker-compose.yml (copy from solution doc)
nano docker-compose.yml
```

### Step 3: Configure Environment
```bash
# Create .env file
cat > .env << 'EOF'
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=<YOUR_KEY_HERE>
ANTHROPIC_API_KEY=<YOUR_KEY_HERE>
TELEGRAM_BOT_TOKEN=<YOUR_KEY_HERE>
EOF

# IMPORTANT: Replace <YOUR_KEY_HERE> with actual keys!
```

### Step 4: Deploy
```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Test health endpoint
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"ASEAGI API"}
```

### Step 5: Test Telegram Bot
```
Open Telegram → Find your bot → Send:
/start
/timeline
/violations

Expected: Real responses (not connection errors!)
```

---

## 📊 Day 2: Fix CEO Dashboard (1-2 hours)

```bash
# Set environment variables permanently
cat >> ~/.bashrc << 'EOF'
export SUPABASE_URL='https://jvjlhxodmbkodzmggwpu.supabase.co'
export SUPABASE_KEY='<YOUR_KEY_HERE>'
EOF

source ~/.bashrc

# Navigate to dashboard
cd ~/Downloads/Resources/CH16_Technology/Dashboards/

# Kill any existing dashboard processes
pkill -f streamlit

# Start CEO dashboard
streamlit run 2025-11-05-CH16-ceo-global-dashboard.py \
  --server.port=8503 \
  --server.address=0.0.0.0 &

# Verify
curl http://localhost:8503
# Should return HTML (not error)

# Access in browser
open http://localhost:8503
```

---

## 🗄️ Day 3: Update Database Schema (1 hour)

```bash
# Connect to Supabase
psql "postgresql://postgres:[password]@db.jvjlhxodmbkodzmggwpu.supabase.co:5432/postgres"

# Or use Supabase SQL Editor (recommended)
# https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/editor

# Run this SQL:
```

```sql
-- Add bulk processing columns
ALTER TABLE documents ADD COLUMN IF NOT EXISTS batch_id VARCHAR(50);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS tier0_recommended_tier VARCHAR(20);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS tier0_reasoning TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS processing_worker VARCHAR(50);

-- Create routing accuracy tracking
CREATE TABLE IF NOT EXISTS routing_accuracy (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(50),
    predicted_tier VARCHAR(20),
    actual_tier VARCHAR(20),
    was_correct BOOLEAN,
    cost_if_correct DECIMAL(10, 4),
    cost_actual DECIMAL(10, 4),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create batch tracking
CREATE TABLE IF NOT EXISTS processing_batches (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) UNIQUE,
    source VARCHAR(50),
    total_documents INT,
    documents_processed INT DEFAULT 0,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(20),
    total_cost_usd DECIMAL(10, 2)
);

-- Verify
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_name IN ('documents', 'routing_accuracy', 'processing_batches')
ORDER BY table_name, ordinal_position;
```

---

## 🧪 Day 4-5: Testing (2 days)

### Test 1: Telegram Bot Commands
```
Send each command and verify response:

✅ /start → Welcome message
✅ /timeline → Shows events
✅ /violations → Shows violations (or "none detected")
✅ /actions → Shows pending actions
✅ /deadline → Shows upcoming deadlines
✅ /report → Daily summary
✅ /hearing → Hearing info
✅ /motion reconsideration "test" → Motion draft
```

### Test 2: Dashboard Access
```bash
# PROJ344 Dashboard
open http://localhost:8501
# Should show: Legal case tracking interface

# CEO Dashboard
open http://localhost:8503
# Should show: PARA distribution, file stats
```

### Test 3: API Endpoints
```bash
# Test each endpoint
curl http://localhost:8000/health
curl http://localhost:8000/telegram/timeline?days=7
curl http://localhost:8000/telegram/violations
curl http://localhost:8000/telegram/actions
curl http://localhost:8000/telegram/deadline

# All should return JSON (not errors)
```

### Test 4: Database Queries
```sql
-- Check document count
SELECT COUNT(*) FROM documents;

-- Check table structure
\d documents
\d routing_accuracy
\d processing_batches

-- All should return results (not errors)
```

---

## 🎯 Week 2: Bulk Processing Setup

### Day 8: Install Vast.AI CLI
```bash
pip install vastai

# Login
vastai set api-key <YOUR_VASTAI_KEY>

# Test
vastai search offers 'gpu_name=RTX_4090' --limit 5
```

### Day 9: Create Coordinator
```bash
mkdir -p /home/user/ASEAGI/bulk-processor
cd /home/user/ASEAGI/bulk-processor

# Download coordinator.py from solution doc
# Download worker.py from solution doc
# Create Docker files
```

### Day 10: Test with 100 Documents
```bash
# Small test run
python3 coordinator.py --test-mode --documents=100 --hours=1

# Monitor
watch -n 5 'psql -c "SELECT processing_status, COUNT(*) FROM documents WHERE batch_id LIKE '\''TEST%'\'' GROUP BY processing_status"'
```

### Day 11-12: Review and Adjust
```bash
# Check costs
psql -c "SELECT 
    batch_id,
    SUM(processing_cost_usd) as total_cost,
    COUNT(*) as doc_count,
    AVG(processing_cost_usd) as avg_cost_per_doc
FROM documents 
WHERE batch_id LIKE 'TEST%'
GROUP BY batch_id"

# Check routing accuracy
psql -c "SELECT 
    predicted_tier,
    actual_tier,
    COUNT(*),
    AVG(CASE WHEN was_correct THEN 1.0 ELSE 0.0 END) as accuracy_rate
FROM routing_accuracy
GROUP BY predicted_tier, actual_tier"

# Adjust thresholds if needed
```

### Day 13-14: Full 7TB Run
```bash
# THE BIG ONE
python3 coordinator.py --documents=700000 --hours=4

# Expected:
# - 30 Vast.AI instances spinning up
# - ~2,900 docs/minute processing
# - Real-time updates to database
# - ~4.5 hours total time
# - ~$59k total cost
```

---

## ✅ Verification Checklist

After each phase, verify:

### Phase 1 Complete (Week 1)
- [ ] Telegram bot responds to all commands
- [ ] CEO dashboard loads without errors
- [ ] Database has all required tables
- [ ] API health check returns 200 OK
- [ ] Can query documents from database
- [ ] No Docker container errors

### Phase 2 Complete (Week 2)
- [ ] Vast.AI coordinator runs without errors
- [ ] Test batch processed successfully
- [ ] Costs match projections
- [ ] Routing accuracy >80%
- [ ] Files renamed correctly
- [ ] Database updated with results

### Phase 3 Complete (Full Run)
- [ ] All 700k documents processed
- [ ] Files organized into tier folders
- [ ] Complete metadata in database
- [ ] Total cost within budget
- [ ] Naming compliance >90%
- [ ] Search functionality works

---

## 🚨 Troubleshooting

### Issue: Telegram bot still shows connection errors
```bash
# Check if API is running
docker-compose ps

# Check API logs
docker-compose logs api

# Restart services
docker-compose restart

# Test endpoint directly
curl http://localhost:8000/telegram/timeline?days=1
```

### Issue: Dashboard won't start
```bash
# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_KEY

# If empty, source bashrc
source ~/.bashrc

# Check for port conflicts
lsof -i :8503

# Kill conflicting process
kill -9 <PID>

# Restart dashboard
streamlit run dashboard.py --server.port=8503
```

### Issue: Database connection fails
```bash
# Test connection
psql "postgresql://postgres:[password]@db.jvjlhxodmbkodzmggwpu.supabase.co:5432/postgres" -c "SELECT 1"

# Check .env file
cat /home/user/ASEAGI/.env

# Verify credentials in Supabase dashboard
```

### Issue: Vast.AI instances not starting
```bash
# Check vastai CLI
vastai list instances

# Check account balance
vastai show user

# Check available offers
vastai search offers 'gpu_name=RTX_4090 reliability>0.95'

# If no offers, try different GPU
vastai search offers 'gpu_name=RTX_4090 reliability>0.90'
```

---

## 📞 Support Resources

- **Supabase Docs:** https://supabase.com/docs
- **Anthropic API:** https://docs.anthropic.com
- **Vast.AI Docs:** https://vast.ai/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Streamlit Docs:** https://docs.streamlit.io

---

## 💰 Cost Tracking

Keep track of actual costs:

```bash
# Check Anthropic usage
# https://console.anthropic.com/settings/usage

# Check Vast.AI spending
vastai show user

# Check Supabase usage
# https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/settings/billing

# Query processing costs
psql -c "SELECT 
    DATE(processing_completed) as date,
    COUNT(*) as documents,
    SUM(processing_cost_usd) as total_cost
FROM documents 
WHERE processing_completed IS NOT NULL
GROUP BY DATE(processing_completed)
ORDER BY date DESC"
```

---

**Ready to start? Begin with Day 1!** 🚀
