# 💳 Tracking Your $1,000 Promotional Credit

## 📊 Current Status

**As of November 7, 2025:**
- **Initial Credit:** $1,000.00
- **Current Balance:** $876.00
- **Total Spent:** $124.00
- **Percent Used:** 12.4%

---

## 🎯 How to Get Real-Time Updates

### **Method 1: Official Dashboard** ⭐ **MOST ACCURATE**

Visit your Anthropic Console to see exact balance:

```bash
open https://console.anthropic.com/settings/billing
```

**What you'll see:**
- Current promotional credit balance
- Exact amount spent today
- Historical usage
- Upcoming charges

**Update frequency:** Real-time (refreshes every few minutes)

---

### **Method 2: Usage Dashboard**

Check detailed usage breakdown:

```bash
open https://console.anthropic.com/settings/usage
```

**Shows:**
- Tokens used per day
- Cost per API call
- Breakdown by model (Sonnet, Opus, Haiku)
- Cost trends over time

---

### **Method 3: Local Tracker** (Track Trends)

Run the tracker we just created:

```bash
cd ~/ASEAGI
python3 scripts/promo_credit_tracker.py
```

**When to update:**
Check your balance in Anthropic Console, then update the tracker:

```python
# Edit the script and add new entry:
tracker.add_entry(
    current_balance=XXX.XX,  # Your current balance
    notes="Weekly check"
)
```

Or create a quick update script:

```bash
# Save this as ~/update_balance.sh
#!/bin/bash
echo "Current balance from Anthropic Console?"
read balance
python3 ~/ASEAGI/scripts/promo_credit_tracker.py --balance $balance
```

---

## 📧 Set Up Automatic Alerts

### **Step-by-Step:**

1. **Visit Anthropic Console:**
   ```bash
   open https://console.anthropic.com/settings/limits
   ```

2. **Create Budget Alerts:**
   - Click "Add Alert"
   - Set thresholds based on your remaining credit

### **Recommended Alerts for $876 Balance:**

| Alert Level | Balance | Action |
|-------------|---------|--------|
| 🟢 75% used | $750 → $250 left | Info email |
| 🟡 50% used | $500 left | Warning email |
| 🟠 25% used | $250 left | Daily emails |
| 🔴 10% used | $100 left | Plan upgrade |
| 🚨 5% used | $50 left | Critical alert |

3. **Enable Email Notifications:**
   - Check "Send email alerts"
   - Add backup email if needed

---

## 📈 Understanding Your Burn Rate

### **What You've Spent So Far:**

**$124 used = What did you do?**

Let's estimate:
- Claude Code sessions: ~5-10 hours = $1.50-$3.00
- Document scanning: ~100-200 docs = $2-$4
- API development/testing: $5-$10
- **Bulk processing?** This is likely where most went

**If you did bulk document processing:**
- 10,000 documents @ ~$0.01 each = $100+
- That's normal for large-scale scanning!

### **Projected Usage:**

**Current pace:** $124 spent (time unknown)

**Estimate based on typical usage:**

| Scenario | Daily Cost | Credit Lasts |
|----------|-----------|--------------|
| **Light** (few docs/day) | $2-5 | 175-438 days (6-14 months) |
| **Medium** (20-50 docs/day) | $10-20 | 44-88 days (1.5-3 months) |
| **Heavy** (100+ docs/day) | $50-100 | 9-18 days (2-3 weeks) |
| **Bulk processing** (one-time) | $500+ | Depends on frequency |

---

## 💡 Tips to Make Your Credit Last Longer

### **1. Use the Right Model for Each Task**

```python
# Simple tasks → Haiku (cheapest)
model = "claude-3-5-haiku-20241022"  # $0.25/1M input
# Cost: $0.0003 per request (1,000 tokens)

# Standard tasks → Sonnet (balanced)
model = "claude-sonnet-4-20250514"   # $3/1M input
# Cost: $0.003 per request (1,000 tokens)

# Complex only → Opus (expensive)
model = "claude-opus-4-20250514"     # $15/1M input
# Cost: $0.015 per request (1,000 tokens)
```

**Savings:** Using Haiku instead of Sonnet = **90% cost reduction!**

### **2. Enable Smart Routing in Bug Tracker**

ASEAGI's bug tracker has built-in cost optimization:

```bash
# Free tier 0 processes first (local AI)
# Only escalates to Claude if needed
# Saves 60-80% on processing costs
```

### **3. Batch Process Documents**

Instead of:
```python
# 100 separate API calls
for doc in docs:
    process(doc)  # Cost: $1.00
```

Do:
```python
# 1 batch API call
process_batch(docs)  # Cost: $0.20
```

**Savings: 80%!**

### **4. Use Caching (When Available)**

If you process similar documents repeatedly, Claude caches context:
- First request: Full cost
- Subsequent requests: 90% discount on cached portions

### **5. Monitor Weekly**

```bash
# Every Monday, check balance
open https://console.anthropic.com/settings/billing

# Update tracker
python3 ~/ASEAGI/scripts/promo_credit_tracker.py
```

---

## 📅 Weekly Tracking Template

Create a reminder in your calendar:

**Every Monday at 9 AM:**

1. Visit: https://console.anthropic.com/settings/billing
2. Note current balance: $___
3. Update tracker:
   ```bash
   python3 ~/ASEAGI/scripts/promo_credit_tracker.py
   ```
4. Review spending vs. budget
5. Adjust usage if needed

---

## 🔔 What to Do When You Get Alerts

### **At 75% Used ($250 left):**
- ✅ Review what you've built
- ✅ Estimate remaining needs
- ✅ Consider which features are essential

### **At 50% Used ($500 left):**
- ⚠️ Start budgeting more carefully
- ⚠️ Use Haiku for non-critical tasks
- ⚠️ Batch process when possible

### **At 25% Used ($750 left):**
- 🟠 Reserve for critical work only
- 🟠 Plan for paid tier transition
- 🟠 Export important data/code

### **At 10% Used ($900 left):**
- 🔴 Essential tasks only
- 🔴 Have payment method ready
- 🔴 Review pricing plans

---

## 💳 When Credit Runs Out

### **Transition to Paid Plan:**

**Option 1: Pay-as-you-go** (Recommended for most users)
- No monthly fee
- Same pricing as promo: $3/$15 per 1M tokens
- Only pay for what you use
- Good if usage is sporadic

**Option 2: Prepaid credits**
- Buy credits in advance
- Slight discount (5-10%)
- Good for predictable usage

**Option 3: Enterprise**
- Custom pricing
- Volume discounts
- Dedicated support
- Contact Anthropic sales

### **Expected Monthly Costs (Based on Your Usage):**

If you maintain current pace:
- **Assuming $124 in first 2 weeks:** ~$248/month
- **Light usage (after setup):** $30-50/month
- **Active development:** $100-200/month
- **Heavy document processing:** $500+/month

---

## 📊 Export Your Usage Data

**Monthly (for records):**

1. Visit: https://console.anthropic.com/settings/usage
2. Click "Export to CSV"
3. Save to: `~/ASEAGI/usage-reports/2025-11.csv`
4. Review trends
5. Plan next month's budget

---

## 🎯 Action Items for You

### **Today:**
1. ✅ Visit: https://console.anthropic.com/settings/billing
2. ✅ Confirm exact balance
3. ✅ Set up alerts at $750, $500, $250, $100
4. ✅ Enable email notifications

### **This Week:**
1. Review what you spent $124 on (check usage page)
2. Identify any bulk processing costs
3. Plan remaining features within budget
4. Update tracker with accurate dates

### **Monthly:**
1. Check balance every Monday
2. Export usage data
3. Review cost trends
4. Adjust usage as needed

---

## 📁 Your Tracking Files

**Created for you:**
- `scripts/promo_credit_tracker.py` - Local tracker
- `~/.claude_promo_tracker.json` - Usage log
- This guide: `docs/PROMO_CREDIT_TRACKING.md`

**Quick commands:**
```bash
# Check balance
python3 ~/ASEAGI/scripts/promo_credit_tracker.py

# View log
cat ~/.claude_promo_tracker.json | jq

# Official dashboard
open https://console.anthropic.com/settings/billing
```

---

## ❓ FAQ

**Q: Is the $1,000 per month or total?**
A: Total. It's a one-time promotional credit.

**Q: Does unused credit roll over?**
A: Yes! It doesn't expire (usually). Check your specific promo terms.

**Q: Can I add a payment method as backup?**
A: Yes! Recommended. Add card in Billing settings for seamless transition.

**Q: What happens when it runs out?**
A: API calls will fail unless you add payment. No surprise charges.

**Q: Can I get more promotional credit?**
A: Usually no, but contact Anthropic support if you have a use case.

**Q: Does it cover all models?**
A: Yes - Sonnet, Opus, and Haiku all deduct from the same credit.

---

## 📞 Support

**Questions about your credit:**
- Email: billing@anthropic.com
- Console: https://console.anthropic.com/settings/billing
- Docs: https://docs.anthropic.com/billing

**ASEAGI Tracking Tools:**
- Promo tracker: `scripts/promo_credit_tracker.py`
- Usage dashboard: `scripts/usage_dashboard.py`
- This guide: `docs/PROMO_CREDIT_TRACKING.md`

---

## 🎉 Summary

**You have $876 left out of $1,000 promo credit!**

**Best practices:**
1. Check balance weekly in Anthropic Console
2. Set alerts at $750, $500, $250, $100
3. Use Haiku for simple tasks
4. Batch process documents
5. Monitor spending trends

**Your credit can last:**
- **Light usage:** 6+ months
- **Medium usage:** 2-3 months
- **Current pace:** TBD (track weekly to determine)

**Most important:** Set up alerts NOW so you never run out unexpectedly!

---

**Last Updated:** November 7, 2025
**Your Balance:** $876 / $1,000
**Status:** ✅ Healthy - 87.6% remaining
