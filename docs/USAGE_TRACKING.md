# Claude API Usage & Cost Tracking

## 💰 Pricing (Web & Terminal - Same Rates)

| Model | Input | Output | Best For |
|-------|-------|--------|----------|
| **Sonnet 4.5** | $3/1M tokens | $15/1M tokens | General use (recommended) |
| **Opus 4** | $15/1M tokens | $75/1M tokens | Complex analysis |
| **Haiku 3.5** | $0.25/1M tokens | $1.25/1M tokens | Simple tasks |

**Important:** Both Claude Code Web and Terminal use the same API and cost the same.

---

## 📊 This Session's Cost

**Current conversation:**
- **Tokens used:** ~98,000 input tokens
- **Estimated cost:** ~$0.29
- **Model:** Claude Sonnet 4.5

---

## 🎯 How to Track Your Usage

### **Method 1: Official Dashboard (Most Accurate)**

```bash
# Open Anthropic Console
open https://console.anthropic.com/settings/usage
```

**Features:**
- ✅ Real-time usage tracking
- ✅ Breakdown by API key
- ✅ Daily/monthly totals
- ✅ Export to CSV
- ✅ Set budget alerts

### **Method 2: Local Tracking Scripts**

We've created two tools for you:

#### **A. Quick Cost Estimator**
```bash
python3 scripts/track_api_usage.py
```

Shows example costs for common operations.

#### **B. Usage Dashboard**
```bash
python3 scripts/usage_dashboard.py
```

Logs and tracks your local usage over time.

**Log location:** `~/.claude_usage_log.jsonl`

---

## 💡 Example Costs

### **Typical ASEAGI Operations**

| Task | Input | Output | Cost |
|------|-------|--------|------|
| Scan 1 legal document | 2,000 | 500 | $0.014 |
| Bug tracker error log | 1,000 | 200 | $0.006 |
| Telegram bot response | 500 | 200 | $0.005 |
| Dashboard query | 1,500 | 300 | $0.009 |
| Claude Code session (1 hour) | 50,000 | 5,000 | $0.23 |

### **Daily Usage Estimates**

| Activity | Daily Cost |
|----------|------------|
| Light usage (5 docs/day) | $0.07 |
| Medium usage (20 docs/day) | $0.28 |
| Heavy usage (100 docs/day) | $1.40 |
| Claude Code (4 hours/day) | $0.92 |

### **Monthly Estimates**

| Scenario | Monthly Cost |
|----------|--------------|
| Personal use | $10-30 |
| Professional (ASEAGI daily) | $50-100 |
| Heavy development | $100-300 |

---

## 🚨 Budget Protection

### **Set Up Alerts**

1. Visit [Anthropic Console](https://console.anthropic.com/settings/usage)
2. Click "Set Budget Alert"
3. Configure thresholds:
   - 50% warning
   - 80% alert
   - 90% critical
4. Add email notification

### **Hard Limits**

You can set hard limits in the Anthropic Console:
- Daily limit
- Monthly limit
- Per API key limit

**When limit is reached:** API requests will fail with error.

---

## 📈 Cost Optimization Tips

### **1. Use the Right Model**

```python
# Simple tasks - use Haiku (cheapest)
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model="claude-3-5-haiku-20241022",  # $0.25/1M input
    ...
)

# Complex analysis - use Sonnet (balanced)
response = client.messages.create(
    model="claude-sonnet-4-20250514",  # $3/1M input
    ...
)

# Only use Opus for very complex tasks
response = client.messages.create(
    model="claude-opus-4-20250514",  # $15/1M input
    ...
)
```

### **2. Optimize Prompts**

- ✅ Be concise
- ✅ Use system prompts efficiently
- ✅ Cache frequently used context (if available)
- ❌ Avoid repeating large context

### **3. Batch Processing**

Process multiple documents in one request when possible:

```python
# Instead of 10 separate requests
for doc in docs:
    analyze(doc)  # 10 × cost

# Do one batch request
analyze_batch(docs)  # 1 × cost
```

### **4. Use Bug Tracker Routing**

ASEAGI's bug tracker uses smart routing:
- Free Tier 0: Tesseract + Ollama (local, free)
- Only calls Claude when necessary
- Can save 60-80% on costs

---

## 📁 Where Your Money Goes

**For ASEAGI Project:**

### **Document Processing (Bulk)**
- 7TB → ~700,000 documents
- Estimated: $58,000 one-time
- With routing: Save 74% → $15,000

### **Ongoing Operations**
- Daily document scanning: ~50 docs
- Telegram bot responses: ~20/day
- Dashboard queries: minimal
- **Monthly:** ~$30-50

### **Claude Code Sessions**
- Development work
- Bug fixing
- Feature implementation
- **Per hour:** ~$0.23

---

## 🔍 Monitor Your Spending

### **Daily Checklist**

```bash
# Check usage
python3 scripts/usage_dashboard.py

# View log
cat ~/.claude_usage_log.jsonl | jq '.cost' | awk '{s+=$1} END {print "Total: $"s}'
```

### **Weekly Review**

1. Visit Anthropic Console
2. Review usage trends
3. Check if within budget
4. Adjust usage if needed

### **Monthly Export**

```bash
# Export from Anthropic Console
# Analyze trends
# Compare to budget
# Plan for next month
```

---

## ❓ FAQ

**Q: Does Claude Code Web cost more than Terminal?**
A: No, they cost exactly the same. Both use the same API.

**Q: How are tokens counted?**
A: Both input (your prompts + context) and output (Claude's responses) are counted separately and charged at different rates.

**Q: What's the 200K token limit?**
A: That's the context window size (memory). It resets each session. It's not a cost limit.

**Q: Can I use multiple API keys?**
A: Yes! Create separate keys for different projects to track usage separately.

**Q: What happens if I hit my limit?**
A: API requests will fail with a 429 error. Set alerts to avoid this.

**Q: Is there a free tier?**
A: Anthropic offers $5 free credits for new accounts. After that, you pay per use.

---

## 📞 Support

**Official:**
- [Anthropic Pricing](https://www.anthropic.com/pricing)
- [API Documentation](https://docs.anthropic.com)
- support@anthropic.com

**ASEAGI Tools:**
- `scripts/track_api_usage.py` - Cost calculator
- `scripts/usage_dashboard.py` - Usage tracker
- `~/.claude_usage_log.jsonl` - Local log file

---

**Last Updated:** November 7, 2025
**Your Current Session Cost:** ~$0.29
**Estimated Monthly (current pace):** ~$8.70
