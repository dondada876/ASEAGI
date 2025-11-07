# INTELLIGENT TIERED STORAGE ARCHITECTURE
**Post-Scan Document Routing Based on Scores & Access Patterns**

---

## 🎯 CONCEPT OVERVIEW

```
DOCUMENT ARRIVES
    ↓
SCAN & SCORE (Vast.AI processing)
    ↓
INTELLIGENT ROUTER analyzes:
├─ Overall score (0-999)
├─ Document importance (critical/high/medium/low)
├─ Expected access frequency
├─ Legal deadlines/case status
└─ Storage cost optimization
    ↓
ROUTE TO OPTIMAL STORAGE TIER
```

---

## 💾 STORAGE TIER DEFINITIONS

### Tier 1: HOT STORAGE (Instant Access)
**Purpose:** Critical documents accessed frequently

**Characteristics:**
- Score: 900-999 (smoking guns, critical evidence)
- Access: Daily/weekly
- Speed: <1 second retrieval
- Cost: $$$ (highest)

**Storage Options:**
1. **Supabase Storage** ($0.021/GB/month)
   - Direct database integration
   - RLS security built-in
   - Best for: <100GB critical docs

2. **Digital Ocean Spaces** ($5/month for 250GB + $0.02/GB over)
   - S3-compatible API
   - CDN included
   - Best for: 100GB-1TB

3. **Google Drive Premium** ($9.99/month for 2TB)
   - Already using
   - Instant preview
   - Best for: Active case documents

**Retention:** Until case closed + 7 years

---

### Tier 2: WARM STORAGE (Fast Access)
**Purpose:** Important documents accessed occasionally

**Characteristics:**
- Score: 700-899 (high value, strong evidence)
- Access: Weekly/monthly
- Speed: 1-5 seconds retrieval
- Cost: $$ (moderate)

**Storage Options:**
1. **Backblaze B2** ($0.005/GB/month)
   - S3-compatible
   - Free egress to Cloudflare
   - Best for: 1TB-10TB

2. **Wasabi** ($6.99/month per TB)
   - Flat rate, no egress fees
   - Hot cloud pricing model
   - Best for: Predictable access patterns

3. **AWS S3 Standard** ($0.023/GB/month)
   - Industry standard
   - Integrated with everything
   - Best for: Enterprise integration

**Retention:** Until case closed + 5 years

---

### Tier 3: COOL STORAGE (Occasional Access)
**Purpose:** Supporting documents accessed rarely

**Characteristics:**
- Score: 400-699 (supporting, contextual)
- Access: Monthly/quarterly
- Speed: 5-60 seconds retrieval
- Cost: $ (low)

**Storage Options:**
1. **AWS S3 Intelligent-Tiering** ($0.0125/GB/month + auto-tiering)
   - Automatically moves to cheaper tiers
   - No retrieval fees
   - Best for: Unknown access patterns

2. **Google Cloud Storage Nearline** ($0.01/GB/month)
   - 30-day minimum storage
   - $0.01/GB retrieval
   - Best for: Quarterly access

3. **Azure Blob Cool** ($0.01/GB/month)
   - Microsoft ecosystem
   - Good integration
   - Best for: Office 365 users

**Retention:** Until case closed + 3 years

---

### Tier 4: COLD STORAGE (Archive)
**Purpose:** Historical records, rarely needed

**Characteristics:**
- Score: 0-399 (archive, low relevance)
- Access: Annually or never
- Speed: 1-12 hours retrieval
- Cost: ¢ (very low)

**Storage Options:**
1. **AWS S3 Glacier Deep Archive** ($0.00099/GB/month)
   - Cheapest option available
   - 12-hour retrieval
   - Best for: Long-term archive

2. **Google Cloud Archive** ($0.0012/GB/month)
   - 180-day minimum
   - Similar to Glacier
   - Best for: Google ecosystem

3. **Backblaze B2 with Archive Policy** ($0.002/GB/month)
   - Custom lifecycle rules
   - Cheaper than hot tier
   - Best for: Flexible policies

**Retention:** Permanent (or until legally allowed to delete)

---

## 🏗️ COMPLETE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                  VAST.AI PROCESSING SWARM                        │
│  (Processes documents, assigns scores 0-999)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              STORAGE ROUTER (Digital Ocean)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 Analyzes Each Document:                                      │
│     ├─ Overall Score (0-999)                                    │
│     ├─ Micro Score (fact-level importance)                      │
│     ├─ Macro Score (strategic value)                            │
│     ├─ Legal Score (motion relevance)                           │
│     ├─ Document Type (transcript, medical, text, etc.)          │
│     ├─ Case Status (active, pending, closed)                    │
│     └─ Predicted Access Frequency                               │
│                                                                  │
│  🎯 Routing Decision Matrix:                                     │
│                                                                  │
│     ┌──────────────────────────────────────────────────┐       │
│     │ IF overall_score >= 900:                          │       │
│     │    → TIER 1 (Hot Storage)                         │       │
│     │    → Store in: Supabase + Google Drive Premium    │       │
│     │    → Replicate: Yes (3 copies)                    │       │
│     │    → Index: Full-text + vector embeddings         │       │
│     │                                                    │       │
│     │ ELSE IF overall_score >= 700:                     │       │
│     │    → TIER 2 (Warm Storage)                        │       │
│     │    → Store in: Backblaze B2                       │       │
│     │    → Replicate: Yes (2 copies)                    │       │
│     │    → Index: Full-text only                        │       │
│     │                                                    │       │
│     │ ELSE IF overall_score >= 400:                     │       │
│     │    → TIER 3 (Cool Storage)                        │       │
│     │    → Store in: AWS S3 Intelligent-Tiering         │       │
│     │    → Replicate: No (single copy)                  │       │
│     │    → Index: Metadata only                         │       │
│     │                                                    │       │
│     │ ELSE:                                              │       │
│     │    → TIER 4 (Cold Archive)                        │       │
│     │    → Store in: AWS Glacier Deep Archive           │       │
│     │    → Replicate: No (single copy)                  │       │
│     │    → Index: Minimal (ID, date, type)              │       │
│     └──────────────────────────────────────────────────┘       │
│                                                                  │
│  📝 Log Every Decision:                                          │
│     - Document ID                                                │
│     - Score breakdown                                            │
│     - Tier assigned                                              │
│     - Storage provider                                           │
│     - Monthly cost estimate                                      │
│     - Retrieval speed                                            │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┬────────────────┐
        │                │                │                │
        ▼                ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   TIER 1     │ │   TIER 2     │ │   TIER 3     │ │   TIER 4     │
│  HOT ($$$$)  │ │  WARM ($$)   │ │  COOL ($)    │ │  COLD (¢)    │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│              │ │              │ │              │ │              │
│ 12 critical  │ │ 24 high-val  │ │ 38 support   │ │ 626 archive  │
│ docs         │ │ docs         │ │ docs         │ │ docs         │
│              │ │              │ │              │ │              │
│ Supabase     │ │ Backblaze B2 │ │ AWS S3       │ │ Glacier      │
│ + GDrive     │ │              │ │ Intel-Tier   │ │ Deep Archive │
│              │ │              │ │              │ │              │
│ <1s access   │ │ 1-5s access  │ │ 5-60s access │ │ 1-12h access │
│              │ │              │ │              │ │              │
│ $0.252/mo    │ │ $0.120/mo    │ │ $0.475/mo    │ │ $0.620/mo    │
│ (12GB × $21) │ │ (24GB × $5)  │ │ (38GB × $12) │ │ (626GB × $1) │
│              │ │              │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │                │                │                │
        └────────────────┴────────────────┴────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              UNIFIED METADATA DATABASE                           │
│                    (PostgreSQL)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Tracks ALL documents regardless of storage tier:               │
│                                                                  │
│  document_id | filename | tier | provider | score | url | cost  │
│  ──────────────────────────────────────────────────────────────│
│  DOC-001     | 2021...  |  1   | supabase | 941  | ... | 0.021 │
│  DOC-002     | 2024...  |  1   | supabase | 955  | ... | 0.021 │
│  DOC-032     | 2022...  |  2   | b2       | 825  | ... | 0.005 │
│  DOC-156     | 2021...  |  4   | glacier  | 245  | ... | 0.001 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 COST COMPARISON (700K Documents Example)

### Scenario: 700,000 documents, 7TB total

**Distribution by Score:**
- Tier 1 (900-999): 1.7% = 12,000 docs = 120GB
- Tier 2 (700-899): 3.4% = 24,000 docs = 240GB
- Tier 3 (400-699): 5.4% = 38,000 docs = 380GB
- Tier 4 (0-399): 89.5% = 626,000 docs = 6,260GB

### Cost Analysis

```
SINGLE TIER (Everything in Google Drive):
├─ 7TB × $10/TB/month = $70/month
└─ Total: $70/month

INTELLIGENT TIERED STORAGE:
├─ Tier 1: 120GB × $0.021/GB = $2.52/month
├─ Tier 2: 240GB × $0.005/GB = $1.20/month
├─ Tier 3: 380GB × $0.0125/GB = $4.75/month
├─ Tier 4: 6,260GB × $0.001/GB = $6.26/month
└─ Total: $14.73/month

SAVINGS: $70 - $14.73 = $55.27/month (79% reduction!)
         $55.27 × 12 months = $663.24/year saved
```

---

## 🔄 AUTOMATIC TIER MIGRATION

### Access Pattern Learning

Documents can automatically move between tiers based on actual usage:

```python
class TierMigrationEngine:
    """
    Monitors access patterns and migrates documents between tiers
    """
    
    def analyze_access_patterns(self):
        """
        Run nightly to optimize storage costs
        """
        # Get documents accessed in last 30 days
        hot_accessed = self.db.query("""
            SELECT document_id, storage_tier, access_count, last_accessed
            FROM documents
            WHERE last_accessed > NOW() - INTERVAL '30 days'
        """)
        
        # Promote frequently accessed documents
        for doc in hot_accessed:
            if doc['storage_tier'] > 2 and doc['access_count'] > 5:
                # Being accessed frequently from cold storage - promote!
                self.promote_document(doc['document_id'], target_tier=2)
        
        # Demote rarely accessed documents
        cold_candidates = self.db.query("""
            SELECT document_id, storage_tier, last_accessed
            FROM documents
            WHERE storage_tier < 3
            AND last_accessed < NOW() - INTERVAL '6 months'
        """)
        
        for doc in cold_candidates:
            # Not accessed in 6 months - demote to save cost
            self.demote_document(doc['document_id'], target_tier=3)
    
    def promote_document(self, doc_id: str, target_tier: int):
        """
        Move document to faster/more expensive tier
        """
        # Get document metadata
        doc = self.db.get_document(doc_id)
        
        # Copy to new tier
        new_url = self.copy_to_tier(doc['storage_url'], target_tier)
        
        # Update database
        self.db.execute("""
            UPDATE documents 
            SET storage_tier = %s,
                storage_url = %s,
                tier_migration_date = NOW(),
                tier_migration_reason = 'Frequent access detected'
            WHERE document_id = %s
        """, (target_tier, new_url, doc_id))
        
        # Delete from old tier after confirmation
        self.delete_from_tier(doc['storage_url'])
        
        print(f"✅ Promoted {doc_id} to Tier {target_tier}")
    
    def demote_document(self, doc_id: str, target_tier: int):
        """
        Move document to slower/cheaper tier
        """
        # Similar to promote but moves to cheaper storage
        # ...
```

### Migration Rules

```
PROMOTE (Move to faster tier):
├─ Accessed >5 times in 30 days
├─ Attached to active case/motion
├─ Score increased (re-analysis)
└─ Legal deadline approaching

DEMOTE (Move to cheaper tier):
├─ Not accessed in 6+ months
├─ Case closed/archived
├─ Score decreased (re-analysis)
└─ Past statute of limitations

KEEP IN CURRENT TIER:
├─ Access pattern matches tier
├─ Cost-optimized already
└─ Migration cost > savings
```

---

## 🎯 IMPLEMENTATION

### Phase 1: Storage Router Service

```python
# /home/user/ASEAGI/storage-router/router.py

import boto3
from google.cloud import storage as gcs
from supabase import create_client
import backblaze

class StorageRouter:
    """
    Routes documents to optimal storage tier based on scores
    """
    
    def __init__(self):
        # Initialize all storage clients
        self.supabase = create_client(os.getenv("SUPABASE_URL"), 
                                       os.getenv("SUPABASE_KEY"))
        
        self.s3 = boto3.client('s3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
        )
        
        self.b2 = backblaze.B2Api()
        self.b2.authorize_account(
            'production',
            os.getenv("B2_KEY_ID"),
            os.getenv("B2_APP_KEY")
        )
        
        self.glacier = boto3.client('glacier',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
        )
    
    def route_document(self, doc_metadata: dict, file_path: str) -> dict:
        """
        Route document to optimal storage tier
        """
        # Calculate tier based on score
        tier = self._calculate_tier(doc_metadata)
        
        # Get provider for tier
        provider = self._get_provider_for_tier(tier)
        
        # Upload to provider
        storage_url = self._upload_to_provider(file_path, provider, tier)
        
        # Update database
        self._update_database(doc_metadata, tier, provider, storage_url)
        
        # Calculate monthly cost
        file_size_gb = os.path.getsize(file_path) / (1024**3)
        monthly_cost = self._calculate_cost(tier, file_size_gb)
        
        return {
            'document_id': doc_metadata['document_id'],
            'tier': tier,
            'provider': provider,
            'storage_url': storage_url,
            'monthly_cost': monthly_cost,
            'retrieval_speed': self._get_retrieval_speed(tier)
        }
    
    def _calculate_tier(self, doc_metadata: dict) -> int:
        """
        Determine storage tier based on document scores
        """
        overall_score = doc_metadata['overall_score']
        document_type = doc_metadata['document_type']
        case_status = doc_metadata.get('case_status', 'active')
        
        # Tier 1: Critical documents (score 900-999)
        if overall_score >= 900:
            return 1
        
        # Tier 2: High value (score 700-899)
        elif overall_score >= 700:
            return 2
        
        # Tier 3: Supporting docs (score 400-699)
        elif overall_score >= 400:
            return 3
        
        # Tier 4: Archive (score 0-399)
        else:
            # Exception: Keep court transcripts in Tier 2 even if low score
            if document_type == 'TRANSCRIPT':
                return 2
            # Exception: Medical records always Tier 2 minimum
            elif document_type == 'MEDICAL':
                return 2
            else:
                return 4
    
    def _get_provider_for_tier(self, tier: int) -> str:
        """
        Map tier to storage provider
        """
        providers = {
            1: 'supabase',      # Hot: Supabase Storage
            2: 'backblaze',     # Warm: Backblaze B2
            3: 's3_intelligent', # Cool: AWS S3 Intelligent-Tiering
            4: 'glacier'        # Cold: AWS Glacier Deep Archive
        }
        return providers[tier]
    
    def _upload_to_provider(self, file_path: str, provider: str, 
                           tier: int) -> str:
        """
        Upload file to specific storage provider
        """
        filename = os.path.basename(file_path)
        
        if provider == 'supabase':
            # Upload to Supabase Storage
            with open(file_path, 'rb') as f:
                result = self.supabase.storage\
                    .from_('documents-tier1')\
                    .upload(filename, f)
            
            return result.get('Key')
        
        elif provider == 'backblaze':
            # Upload to Backblaze B2
            bucket = self.b2.get_bucket_by_name('aseagi-tier2')
            bucket.upload_local_file(
                local_file=file_path,
                file_name=filename
            )
            
            return f"b2://aseagi-tier2/{filename}"
        
        elif provider == 's3_intelligent':
            # Upload to AWS S3 with Intelligent-Tiering
            self.s3.upload_file(
                file_path,
                'aseagi-tier3',
                filename,
                ExtraArgs={
                    'StorageClass': 'INTELLIGENT_TIERING'
                }
            )
            
            return f"s3://aseagi-tier3/{filename}"
        
        elif provider == 'glacier':
            # Upload to AWS Glacier Deep Archive
            with open(file_path, 'rb') as f:
                response = self.glacier.upload_archive(
                    vaultName='aseagi-tier4',
                    body=f
                )
            
            return response['archiveId']
    
    def _calculate_cost(self, tier: int, size_gb: float) -> float:
        """
        Calculate monthly storage cost
        """
        costs_per_gb = {
            1: 0.021,   # Supabase
            2: 0.005,   # Backblaze B2
            3: 0.0125,  # S3 Intelligent-Tiering
            4: 0.00099  # Glacier Deep Archive
        }
        
        return size_gb * costs_per_gb[tier]
    
    def _get_retrieval_speed(self, tier: int) -> str:
        """
        Get retrieval speed for tier
        """
        speeds = {
            1: '<1 second',
            2: '1-5 seconds',
            3: '5-60 seconds',
            4: '1-12 hours'
        }
        return speeds[tier]
    
    def retrieve_document(self, doc_id: str) -> bytes:
        """
        Retrieve document from any tier
        """
        # Get document metadata from database
        doc = self.supabase.table('documents')\
            .select('*')\
            .eq('document_id', doc_id)\
            .single()\
            .execute()
        
        tier = doc.data['storage_tier']
        provider = doc.data['storage_provider']
        storage_url = doc.data['storage_url']
        
        # Log access
        self._log_access(doc_id)
        
        # Retrieve from provider
        if provider == 'supabase':
            return self.supabase.storage\
                .from_('documents-tier1')\
                .download(storage_url)
        
        elif provider == 'backblaze':
            # Download from B2
            bucket = self.b2.get_bucket_by_name('aseagi-tier2')
            download_dest = f"/tmp/{doc_id}"
            bucket.download_file_by_name(storage_url, download_dest)
            
            with open(download_dest, 'rb') as f:
                return f.read()
        
        elif provider == 's3_intelligent':
            # Download from S3
            obj = self.s3.get_object(
                Bucket='aseagi-tier3',
                Key=storage_url.split('/')[-1]
            )
            return obj['Body'].read()
        
        elif provider == 'glacier':
            # Initiate Glacier retrieval (takes 12 hours)
            print("⏳ Glacier retrieval initiated - will take 12 hours")
            
            job = self.glacier.initiate_job(
                vaultName='aseagi-tier4',
                jobParameters={
                    'Type': 'archive-retrieval',
                    'ArchiveId': storage_url,
                    'Tier': 'Bulk'  # Cheapest option
                }
            )
            
            return {
                'status': 'pending',
                'job_id': job['jobId'],
                'estimated_completion': '12 hours',
                'message': 'Document retrieval job started'
            }
    
    def _log_access(self, doc_id: str):
        """
        Log document access for tier migration analysis
        """
        self.supabase.table('documents').update({
            'last_accessed': 'NOW()',
            'access_count': 'access_count + 1'
        }).eq('document_id', doc_id).execute()
```

### Phase 2: Database Schema Updates

```sql
-- Add storage tier columns to documents table
ALTER TABLE documents ADD COLUMN IF NOT EXISTS storage_tier INT DEFAULT 3;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS storage_provider VARCHAR(50);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS storage_url TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS storage_cost_monthly DECIMAL(10, 4);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS retrieval_speed VARCHAR(50);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS last_accessed TIMESTAMP;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS access_count INT DEFAULT 0;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS tier_migration_date TIMESTAMP;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS tier_migration_reason TEXT;

-- Create storage costs tracking table
CREATE TABLE storage_costs (
    id SERIAL PRIMARY KEY,
    month DATE NOT NULL,
    tier INT NOT NULL,
    provider VARCHAR(50),
    document_count INT,
    total_size_gb DECIMAL(12, 3),
    total_cost_usd DECIMAL(10, 2),
    avg_cost_per_doc DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create tier migration log
CREATE TABLE tier_migrations (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(50),
    from_tier INT,
    to_tier INT,
    reason TEXT,
    cost_before DECIMAL(10, 4),
    cost_after DECIMAL(10, 4),
    cost_savings DECIMAL(10, 4),
    migrated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_documents_storage_tier ON documents(storage_tier);
CREATE INDEX idx_documents_last_accessed ON documents(last_accessed);
CREATE INDEX idx_tier_migrations_document_id ON tier_migrations(document_id);

-- View: Storage cost summary
CREATE VIEW storage_cost_summary AS
SELECT 
    storage_tier,
    storage_provider,
    COUNT(*) as document_count,
    SUM(file_size) / (1024.0 * 1024.0 * 1024.0) as total_size_gb,
    SUM(storage_cost_monthly) as monthly_cost,
    AVG(storage_cost_monthly) as avg_cost_per_doc
FROM documents
GROUP BY storage_tier, storage_provider
ORDER BY storage_tier;
```

### Phase 3: Docker Compose Update

```yaml
# Add storage router service
services:
  storage-router:
    build: ./storage-router
    container_name: aseagi-storage-router
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - AWS_ACCESS_KEY=${AWS_ACCESS_KEY}
      - AWS_SECRET_KEY=${AWS_SECRET_KEY}
      - B2_KEY_ID=${B2_KEY_ID}
      - B2_APP_KEY=${B2_APP_KEY}
    volumes:
      - /workspace/processed:/data
    depends_on:
      - api
    networks:
      - aseagi-network
```

---

## 📈 EXPECTED SAVINGS

### 7TB Dataset (700,000 documents)

```
BEFORE (All in Google Drive):
$70/month

AFTER (Intelligent Tiering):
├─ Tier 1 (120GB): $2.52/month
├─ Tier 2 (240GB): $1.20/month
├─ Tier 3 (380GB): $4.75/month
└─ Tier 4 (6,260GB): $6.26/month
TOTAL: $14.73/month

SAVINGS: $55.27/month (79%)
ANNUAL: $663.24/year saved
```

### 5-Year Cost Comparison

```
Google Drive Only:
$70/month × 60 months = $4,200

Tiered Storage:
$14.73/month × 60 months = $883.80

TOTAL SAVINGS: $3,316.20 over 5 years
```

---

## 🚀 DEPLOYMENT TIMELINE

### Week 1: Setup Storage Accounts
- [ ] Create AWS account, enable S3 + Glacier
- [ ] Create Backblaze B2 account
- [ ] Configure Supabase Storage
- [ ] Set up credentials

### Week 2: Build Storage Router
- [ ] Implement router.py
- [ ] Test uploads to each tier
- [ ] Update database schema
- [ ] Deploy Docker container

### Week 3: Integration
- [ ] Connect to Vast.AI processing pipeline
- [ ] Route processed documents automatically
- [ ] Monitor costs in real-time
- [ ] Verify all tiers working

### Week 4: Migration Engine
- [ ] Build tier migration logic
- [ ] Set up nightly analysis job
- [ ] Test promote/demote functions
- [ ] Document access patterns

---

**This completes the tiered storage architecture!** 

Documents are automatically routed to cost-optimized storage after processing, saving 79% on storage costs while maintaining instant access to critical evidence.

Want me to build the complete implementation?
