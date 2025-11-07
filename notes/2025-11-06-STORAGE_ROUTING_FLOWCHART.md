# STORAGE TIER ROUTING FLOWCHART

## 🎯 Quick Reference Guide

```
DOCUMENT ARRIVES FROM VAST.AI
    ↓
Has Overall Score?
    │
    ├─ Yes → Continue
    └─ No → ERROR: Document must be scored first
    ↓
Overall Score = ?
    │
    ├─ 900-999 → TIER 1 (HOT STORAGE)
    │   ├─ Storage: Supabase + Google Drive
    │   ├─ Cost: $0.021/GB/month
    │   ├─ Speed: <1 second
    │   ├─ Replicas: 3 copies
    │   └─ Use: Active case, smoking guns
    │
    ├─ 700-899 → TIER 2 (WARM STORAGE)
    │   ├─ Storage: Backblaze B2
    │   ├─ Cost: $0.005/GB/month
    │   ├─ Speed: 1-5 seconds
    │   ├─ Replicas: 2 copies
    │   └─ Use: High value evidence
    │
    ├─ 400-699 → TIER 3 (COOL STORAGE)
    │   ├─ Storage: AWS S3 Intelligent-Tiering
    │   ├─ Cost: $0.0125/GB/month
    │   ├─ Speed: 5-60 seconds
    │   ├─ Replicas: 1 copy
    │   └─ Use: Supporting documents
    │
    └─ 0-399 → TIER 4 (COLD ARCHIVE)
        ├─ Storage: AWS Glacier Deep Archive
        ├─ Cost: $0.00099/GB/month
        ├─ Speed: 1-12 hours
        ├─ Replicas: 1 copy
        └─ Use: Historical archive
```

## 🔄 EXCEPTION RULES

```
Override Standard Routing:

1. Court Transcripts → ALWAYS Tier 2 (minimum)
   Reason: Legal importance regardless of score

2. Medical Records → ALWAYS Tier 2 (minimum)
   Reason: HIPAA compliance, liability protection

3. Active Case Docs → Upgrade by 1 tier
   Example: Score 650 → Tier 3, but active case → Tier 2

4. Past Deadline Docs → Downgrade by 1 tier
   Example: Score 750 → Tier 2, but case closed → Tier 3

5. Frequently Accessed → Promote to faster tier
   Rule: >5 accesses in 30 days = upgrade 1 tier
```

## 💰 REAL-WORLD COST EXAMPLES

### Example 1: Mother's April 2021 Text (Smoking Gun)
```
Document: Mother admits grandfather abuse
Score: 941 (overall)
Size: 2.5 MB

Routing Decision:
├─ Score 941 → TIER 1
├─ Type: TEXT → No override
├─ Active case: Yes → No change (already Tier 1)
└─ RESULT: Tier 1

Storage:
├─ Supabase: $0.021/GB × 0.0025GB = $0.000053/month
├─ Google Drive: Included in existing plan
└─ Total: ~$0.00 (negligible)

Access: Instant (<1 second)
Replicas: 3 copies (Supabase + GDrive + local cache)
```

### Example 2: Dr. Brown Forensic Exam
```
Document: CAL OES 2-925 form
Score: 955 (overall)
Size: 8.2 MB

Routing Decision:
├─ Score 955 → TIER 1
├─ Type: MEDICAL → Override to Tier 2 (but already Tier 1)
├─ Active case: Yes → No change
└─ RESULT: Tier 1

Storage:
├─ Supabase: $0.021/GB × 0.0082GB = $0.00017/month
└─ Total: $0.0002/month

Access: Instant (<1 second)
```

### Example 3: Low-Score Background Doc
```
Document: Generic policy document
Score: 245 (overall)
Size: 450 KB

Routing Decision:
├─ Score 245 → TIER 4
├─ Type: DOCUMENT → No override
├─ Case closed: Yes → No change
└─ RESULT: Tier 4

Storage:
├─ Glacier: $0.00099/GB × 0.00045GB = $0.00000045/month
└─ Total: ~$0.00 (essentially free)

Access: 12 hours (Glacier retrieval)
Use: Archive only, rarely needed
```

### Example 4: Supporting Evidence
```
Document: Email communication
Score: 675 (overall)
Size: 125 KB

Routing Decision:
├─ Score 675 → TIER 3
├─ Type: EMAIL → No override
├─ Active case: Yes → Upgrade to TIER 2
└─ RESULT: Tier 2

Storage:
├─ Backblaze B2: $0.005/GB × 0.000125GB = $0.000000625/month
└─ Total: ~$0.00 (negligible)

Access: 1-5 seconds
```

## 📊 AGGREGATE COST PROJECTION

### Your 7TB Dataset (700,000 documents)

```
Distribution:
├─ Tier 1: 12,000 docs (1.7%) = 120GB
│   Cost: $2.52/month
│   Documents: Critical evidence, smoking guns
│
├─ Tier 2: 24,000 docs (3.4%) = 240GB
│   Cost: $1.20/month
│   Documents: High-value evidence, transcripts
│
├─ Tier 3: 38,000 docs (5.4%) = 380GB
│   Cost: $4.75/month
│   Documents: Supporting documents
│
└─ Tier 4: 626,000 docs (89.5%) = 6,260GB
    Cost: $6.26/month
    Documents: Archive, historical records

TOTAL MONTHLY COST: $14.73
TOTAL ANNUAL COST: $176.76

VS SINGLE TIER (all Google Drive):
$70/month = $840/year

SAVINGS: $663.24/year (79%)
```

## 🚦 MIGRATION TRIGGERS

### Automatic Promotion (Move to Faster Tier)

```
Trigger: Accessed >5 times in 30 days
Example:
├─ Doc in Tier 3, accessed 6 times → Promote to Tier 2
├─ Cost increase: $0.0125 → $0.005 per GB
└─ Benefit: 5-60s → 1-5s retrieval

Trigger: Added to active motion
Example:
├─ Doc in Tier 4, cited in W&I 388 petition → Promote to Tier 2
├─ Cost increase: $0.001 → $0.005 per GB
└─ Benefit: 12 hours → 1-5s retrieval

Trigger: Score increased (re-analysis)
Example:
├─ Doc score updated 450 → 850 → Promote to Tier 2
└─ Triggered by: New evidence discovery, case developments
```

### Automatic Demotion (Move to Cheaper Tier)

```
Trigger: Not accessed in 6 months
Example:
├─ Doc in Tier 2, no access for 6+ months → Demote to Tier 3
├─ Cost savings: $0.005 → $0.0125 per GB (actually more expensive!)
└─ Review: Keep in Tier 2 (demote doesn't save here)

Trigger: Case closed
Example:
├─ All case docs, case closed 2+ years → Demote by 1 tier
├─ Tier 1 → Tier 2
├─ Tier 2 → Tier 3
└─ Tier 3 → Tier 4

Trigger: Past statute of limitations
Example:
├─ Doc from 2018, statute expired → Demote to Tier 4
└─ Cost savings: Varies by current tier
```

## 📱 USER INTERFACE EXAMPLES

### Telegram Bot Integration

```
User: /search mother admission

Bot: 🔍 Found 3 results:

1. 📄 2021-04-16_TEXT_MOT-FAT_985_900_950_941...
   Score: 941 | Tier: 1 (Hot)
   Access: Instant | Cost: $0.0001/month
   [View Document]

2. 📄 2022-01-20_TEXT_MOT-FAT_920_880_910_903...
   Score: 903 | Tier: 1 (Hot)
   Access: Instant | Cost: $0.0001/month
   [View Document]

3. 📄 2022-06-01_AUDIO_FAT_820_840_780_810...
   Score: 810 | Tier: 2 (Warm)
   Access: 3 seconds | Cost: $0.0002/month
   ⚠️ Retrieving... (2-3 seconds)
   [View Document]

💰 Storage: $0.0004/month for these 3 docs
```

### Dashboard Display

```
Storage Tier Distribution:

┌─────────────────────────────────────────────────┐
│ TIER 1 (Hot - Instant Access)       12,000 docs │
│ ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1.7%       │
│ Cost: $2.52/month | 120GB                       │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ TIER 2 (Warm - Fast Access)         24,000 docs │
│ ███████░░░░░░░░░░░░░░░░░░░░░░░░░░░  3.4%       │
│ Cost: $1.20/month | 240GB                       │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ TIER 3 (Cool - Occasional)           38,000 docs│
│ ██████████░░░░░░░░░░░░░░░░░░░░░░░░  5.4%       │
│ Cost: $4.75/month | 380GB                       │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ TIER 4 (Archive - Rarely)          626,000 docs │
│ ████████████████████████████████████  89.5%     │
│ Cost: $6.26/month | 6,260GB                     │
└─────────────────────────────────────────────────┘

TOTAL: $14.73/month | Saving: $55.27/month (79%)
```

## 🎯 DECISION MATRIX

Use this matrix to manually override tier assignments:

| Score | Type | Case Status | Default Tier | Override? | Final Tier |
|-------|------|-------------|--------------|-----------|------------|
| 950 | TEXT | Active | 1 | No | **1** |
| 950 | TEXT | Closed | 1 | Yes | **2** (demote) |
| 850 | MEDICAL | Active | 2 | No | **2** (medical minimum) |
| 850 | DOCUMENT | Active | 2 | No | **2** |
| 650 | TRANSCRIPT | Active | 3 | Yes | **2** (transcript minimum) |
| 650 | EMAIL | Closed | 3 | No | **3** |
| 350 | DOCUMENT | Active | 4 | Maybe | **3** (if frequently accessed) |
| 350 | DOCUMENT | Closed | 4 | No | **4** |

## 🔧 MANUAL TIER CONTROL

### Force Document to Specific Tier

```python
# Via API
POST /storage/override
{
  "document_id": "DOC-001",
  "force_tier": 1,
  "reason": "Referenced in active motion",
  "expires": "2025-12-31"  # Auto-revert after date
}

# Via Telegram
/tier DOC-001 1 "Active motion reference"

# Via Dashboard
Document Actions → Change Storage Tier → Tier 1
```

### Batch Tier Operations

```python
# Promote all documents in active case
POST /storage/batch-override
{
  "case_id": "PROJ344",
  "operation": "promote",
  "tiers": 1,  # Promote by 1 tier
  "reason": "Case going to trial"
}

# Demote all closed case documents
POST /storage/batch-override
{
  "case_id": "D22-03244",
  "operation": "demote",
  "tiers": 1,  # Demote by 1 tier
  "reason": "Case closed, archive mode"
}
```

---

**Ready to implement? This gives you 79% storage cost savings while maintaining instant access to critical evidence!**
