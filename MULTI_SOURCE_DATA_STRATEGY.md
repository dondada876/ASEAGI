# Multi-Source Data Consolidation Strategy
**Case:** In re Ashe B., J24-00478
**Goal:** Unified document processing across Mac Mini, Work Laptop, and Google Drive

---

## 🎯 Challenge Overview

### **Data Sources:**
1. **Mac Mini (Home)** - Primary document storage
2. **Laptop (Work)** - Current working documents
3. **Google Drive** - Cloud backup and sharing

### **Requirements:**
- ✅ No duplicate processing
- ✅ Unified document registry
- ✅ Support all file types (RTF, DOC, DOCX, PDF, MD, TXT)
- ✅ Future: Video/audio with Twelve Labs
- ✅ Future: Graph RAG with Neo4j
- ✅ All documents in Supabase with embeddings

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Sources Layer                        │
├─────────────────┬──────────────────┬────────────────────────┤
│  Mac Mini       │  Work Laptop     │  Google Drive          │
│  (Home)         │  (Current)       │  (Cloud)               │
│  ~/Documents    │  ~/Documents     │  drive.google.com      │
└────────┬────────┴────────┬─────────┴───────────┬────────────┘
         │                 │                     │
         └─────────────────┼─────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Document Scanner & Deduplication                │
│  - Scans all sources recursively                            │
│  - Generates MD5 hash for each file                         │
│  - Checks against master registry                           │
│  - Skips duplicates automatically                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  Master Document Registry                    │
│                     (Supabase Table)                         │
│  - file_hash (MD5) - PRIMARY KEY for deduplication         │
│  - file_path (original location)                            │
│  - file_name, file_type, file_size                         │
│  - source_location (mac_mini | laptop | gdrive)            │
│  - processing_status (pending | processing | complete)      │
│  - last_modified, discovered_date                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  Processing Pipeline                         │
│  1. Extract text (document_extractor.py)                   │
│  2. AI Analysis (Claude - macro/micro scoring)              │
│  3. Generate embeddings (OpenAI)                            │
│  4. Store in repository                                      │
│  5. Upload to Supabase                                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  Storage & Analysis Layer                    │
├─────────────────┬──────────────────┬────────────────────────┤
│  Supabase       │  pgvector        │  Document Repository   │
│  (Structured)   │  (Embeddings)    │  (Full Text)           │
│  - 39 tables    │  - Semantic      │  - raw_text/           │
│  - 52 views     │    search        │  - metadata/           │
│  - SQL queries  │  - RAG           │  - json/               │
└─────────────────┴──────────────────┴────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Future Enhancements                       │
├─────────────────┬──────────────────┬────────────────────────┤
│  Neo4j          │  Twelve Labs     │  FastAPI               │
│  (Graph RAG)    │  (Video/Audio)   │  (Multi-Device)        │
│  - Relationships│  - Transcription │  - Phone access        │
│  - Knowledge    │  - Scene detect  │  - Web access          │
│    graph        │  - Speaker ID    │  - API endpoints       │
└─────────────────┴──────────────────┴────────────────────────┘
```

---

## 🔑 Deduplication Strategy

### **How It Works:**

```python
# Step 1: Calculate MD5 hash for each file
import hashlib

def calculate_hash(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()

# Step 2: Check against master registry
SELECT COUNT(*) FROM master_document_registry
WHERE file_hash = 'abc123...'

# Step 3: Skip if exists, process if new
if count > 0:
    print("Duplicate found - SKIP")
else:
    print("New document - PROCESS")
```

### **Duplicate Detection Scenarios:**

| Scenario | Detection Method | Action |
|----------|------------------|--------|
| Same file on Mac Mini + Laptop | MD5 hash match | Process once, record both locations |
| Same file renamed | MD5 hash match | Link to original |
| Same file in Google Drive | MD5 hash match | Mark as backed up |
| File edited/updated | MD5 hash different | Process as new version |
| Different files, same name | MD5 hash different | Process both |

---

## 📊 Master Document Registry Schema

```sql
-- Master registry for all document sources
CREATE TABLE IF NOT EXISTS master_document_registry (
    id BIGSERIAL PRIMARY KEY,

    -- Deduplication key
    file_hash TEXT UNIQUE NOT NULL,  -- MD5 hash

    -- File metadata
    file_name TEXT NOT NULL,
    file_type TEXT,  -- rtf, doc, docx, pdf, txt, md, mp4, mp3
    file_size BIGINT,
    file_extension TEXT,

    -- Location tracking (support multiple locations per hash)
    source_locations JSONB,  -- [{"source": "mac_mini", "path": "/path/to/file", "discovered": "2025-11-06"}]
    primary_location TEXT,  -- mac_mini | laptop | gdrive

    -- Processing status
    processing_status TEXT DEFAULT 'pending',  -- pending | processing | complete | failed
    processed_date TIMESTAMPTZ,
    extraction_success BOOLEAN,

    -- Content metadata
    word_count INTEGER,
    char_count INTEGER,
    page_count INTEGER,

    -- Links to other tables
    document_id BIGINT REFERENCES document_repository(id),  -- After upload to Supabase
    embedding_id BIGINT REFERENCES document_embeddings(id),  -- After embedding generation

    -- Timestamps
    first_discovered TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    last_modified TIMESTAMPTZ,

    -- Tags and categorization
    categories TEXT[],
    tags TEXT[],
    case_relevance INTEGER,  -- 0-999 score

    -- Notes
    notes TEXT,

    CONSTRAINT unique_file_hash UNIQUE (file_hash)
);

-- Index for fast duplicate detection
CREATE INDEX idx_master_registry_hash ON master_document_registry(file_hash);
CREATE INDEX idx_master_registry_status ON master_document_registry(processing_status);
CREATE INDEX idx_master_registry_location ON master_document_registry(primary_location);

-- View: Duplicates across sources
CREATE VIEW document_duplicates AS
SELECT
    file_hash,
    file_name,
    jsonb_array_length(source_locations) as location_count,
    source_locations,
    file_size
FROM master_document_registry
WHERE jsonb_array_length(source_locations) > 1
ORDER BY location_count DESC;

-- View: Processing queue
CREATE VIEW documents_to_process AS
SELECT
    id,
    file_name,
    file_type,
    primary_location,
    file_size,
    first_discovered
FROM master_document_registry
WHERE processing_status = 'pending'
ORDER BY first_discovered ASC;
```

---

## 🛠️ Implementation: Multi-Source Scanner

### **Step 1: Scan Local Sources (Mac Mini + Laptop)**

```python
# scan_local_sources.py
import os
import hashlib
from pathlib import Path
from datetime import datetime
import json

class MultiSourceScanner:
    """Scan multiple local directories and register documents"""

    def __init__(self, source_name='laptop'):
        self.source_name = source_name  # 'mac_mini' | 'laptop' | 'gdrive'
        self.registry = {}  # In-memory registry

    def calculate_hash(self, file_path):
        """Calculate MD5 hash for file"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def scan_directory(self, root_path, file_extensions=None):
        """Recursively scan directory for documents"""

        if file_extensions is None:
            file_extensions = ['.rtf', '.doc', '.docx', '.pdf', '.txt', '.md']

        discovered = []
        duplicates = []

        print(f"🔍 Scanning: {root_path}")
        print(f"📂 Source: {self.source_name}")
        print()

        for root, dirs, files in os.walk(root_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]

            for file in files:
                file_path = Path(root) / file
                extension = file_path.suffix.lower()

                if extension not in file_extensions:
                    continue

                try:
                    # Calculate hash
                    file_hash = self.calculate_hash(file_path)
                    file_stat = file_path.stat()

                    # Check if already seen (duplicate)
                    if file_hash in self.registry:
                        duplicates.append({
                            'file_hash': file_hash,
                            'file_name': file,
                            'duplicate_path': str(file_path),
                            'original_path': self.registry[file_hash]['file_path']
                        })
                        print(f"⚠️  DUPLICATE: {file} (already in {self.registry[file_hash]['source']})")
                        continue

                    # New document - add to registry
                    doc_info = {
                        'file_hash': file_hash,
                        'file_name': file,
                        'file_path': str(file_path),
                        'file_type': extension.replace('.', ''),
                        'file_size': file_stat.st_size,
                        'last_modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        'source': self.source_name,
                        'discovered': datetime.now().isoformat()
                    }

                    self.registry[file_hash] = doc_info
                    discovered.append(doc_info)

                    print(f"✅ NEW: {file} ({file_stat.st_size:,} bytes)")

                except Exception as e:
                    print(f"❌ ERROR: {file} - {e}")

        print()
        print("=" * 80)
        print(f"📊 SCAN COMPLETE: {self.source_name}")
        print("=" * 80)
        print(f"✅ New documents: {len(discovered)}")
        print(f"⚠️  Duplicates found: {len(duplicates)}")
        print(f"📝 Total unique: {len(self.registry)}")
        print()

        return {
            'source': self.source_name,
            'discovered': discovered,
            'duplicates': duplicates,
            'total_unique': len(self.registry)
        }

    def save_registry(self, output_path):
        """Save registry to JSON"""
        with open(output_path, 'w') as f:
            json.dump({
                'source': self.source_name,
                'scan_date': datetime.now().isoformat(),
                'documents': list(self.registry.values()),
                'total_documents': len(self.registry)
            }, f, indent=2)
        print(f"💾 Registry saved: {output_path}")

# Usage
if __name__ == "__main__":
    scanner = MultiSourceScanner(source_name='laptop')

    # Scan all common document locations
    paths_to_scan = [
        "/home/user/ASEAGI",
        "/home/user/Documents",
        "/home/user/Downloads"
    ]

    for path in paths_to_scan:
        if os.path.exists(path):
            scanner.scan_directory(path)

    scanner.save_registry('laptop_document_registry.json')
```

---

### **Step 2: Google Drive Integration**

```python
# scan_google_drive.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import hashlib

class GoogleDriveScanner:
    """Scan Google Drive for documents"""

    def __init__(self, credentials_path='credentials.json'):
        self.creds = self.authenticate(credentials_path)
        self.service = build('drive', 'v3', credentials=self.creds)
        self.registry = {}

    def authenticate(self, credentials_path):
        """Authenticate with Google Drive API"""
        # Use Google OAuth2 flow
        # See: https://developers.google.com/drive/api/quickstart/python
        from google_auth_oauthlib.flow import InstalledAppFlow

        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)

        return creds

    def list_files(self, mime_types=None):
        """List all files in Google Drive"""

        if mime_types is None:
            mime_types = [
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # docx
                'application/msword',  # doc
                'application/rtf',
                'application/pdf',
                'text/plain',
                'text/markdown'
            ]

        query = f"mimeType in [{','.join([f\"'{m}'\" for m in mime_types])}]"

        results = self.service.files().list(
            q=query,
            fields="files(id, name, mimeType, size, modifiedTime, md5Checksum)",
            pageSize=1000
        ).execute()

        files = results.get('files', [])

        print(f"🔍 Found {len(files)} documents in Google Drive")

        for file in files:
            file_hash = file.get('md5Checksum', 'NO_HASH')

            doc_info = {
                'file_hash': file_hash,
                'file_name': file['name'],
                'file_id': file['id'],
                'file_type': file['mimeType'],
                'file_size': int(file.get('size', 0)),
                'last_modified': file.get('modifiedTime'),
                'source': 'gdrive',
                'gdrive_link': f"https://drive.google.com/file/d/{file['id']}"
            }

            self.registry[file_hash] = doc_info
            print(f"✅ {file['name']}")

        return self.registry

    def download_file(self, file_id, output_path):
        """Download file from Google Drive"""
        request = self.service.files().get_media(fileId=file_id)

        with open(output_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%")

# Usage
if __name__ == "__main__":
    scanner = GoogleDriveScanner('google_credentials.json')
    scanner.list_files()
    scanner.save_registry('gdrive_document_registry.json')
```

---

### **Step 3: Registry Consolidation**

```python
# consolidate_registries.py
import json
from supabase import create_client

def consolidate_registries(registry_files, supabase_url, supabase_key):
    """Merge all source registries into master Supabase registry"""

    supabase = create_client(supabase_url, supabase_key)

    all_documents = {}
    duplicates = []

    # Load all registries
    for registry_file in registry_files:
        with open(registry_file) as f:
            data = json.load(f)
            source = data['source']

            for doc in data['documents']:
                file_hash = doc['file_hash']

                if file_hash in all_documents:
                    # Duplicate across sources - add location
                    all_documents[file_hash]['source_locations'].append({
                        'source': source,
                        'path': doc['file_path'],
                        'discovered': doc['discovered']
                    })
                    duplicates.append(doc)
                else:
                    # New document
                    all_documents[file_hash] = {
                        'file_hash': file_hash,
                        'file_name': doc['file_name'],
                        'file_type': doc['file_type'],
                        'file_size': doc['file_size'],
                        'last_modified': doc['last_modified'],
                        'primary_location': source,
                        'source_locations': [{
                            'source': source,
                            'path': doc.get('file_path', doc.get('gdrive_link')),
                            'discovered': doc['discovered']
                        }],
                        'processing_status': 'pending'
                    }

    # Upload to Supabase
    print(f"📤 Uploading {len(all_documents)} unique documents to Supabase...")

    for doc in all_documents.values():
        try:
            supabase.table('master_document_registry').upsert(doc).execute()
            print(f"✅ {doc['file_name']}")
        except Exception as e:
            print(f"❌ {doc['file_name']}: {e}")

    print()
    print("=" * 80)
    print("CONSOLIDATION COMPLETE")
    print("=" * 80)
    print(f"Total unique documents: {len(all_documents)}")
    print(f"Duplicates across sources: {len(duplicates)}")
    print()

    # Show duplicate summary
    if duplicates:
        print("📊 Documents found in multiple locations:")
        for dup in duplicates:
            print(f"  - {dup['file_name']} ({dup['source']})")

# Usage
if __name__ == "__main__":
    consolidate_registries(
        registry_files=[
            'laptop_document_registry.json',
            'mac_mini_document_registry.json',
            'gdrive_document_registry.json'
        ],
        supabase_url='https://jvjlhxodmbkodzmggwpu.supabase.co',
        supabase_key='your-key'
    )
```

---

## 🚀 Processing Pipeline

### **Step 4: Unified Document Processor**

```python
# process_all_sources.py
from document_extractor import DocumentExtractor
from document_repository_to_supabase import DocumentRepositoryUploader

def process_document_queue():
    """Process all pending documents from master registry"""

    # Get pending documents from Supabase
    supabase = create_client(...)
    pending = supabase.table('master_document_registry')\
        .select('*')\
        .eq('processing_status', 'pending')\
        .execute()

    print(f"📋 Found {len(pending.data)} documents to process")

    extractor = DocumentExtractor()
    uploader = DocumentRepositoryUploader()

    for doc in pending.data:
        print(f"\n🔄 Processing: {doc['file_name']}")

        # Step 1: Extract text
        extracted = extractor.extract_document(doc['file_path'])

        # Step 2: Upload to document repository
        uploader.upload_documents()

        # Step 3: Generate embeddings
        uploader.generate_embeddings()

        # Step 4: Update master registry
        supabase.table('master_document_registry')\
            .update({'processing_status': 'complete'})\
            .eq('file_hash', doc['file_hash'])\
            .execute()

        print(f"✅ Complete: {doc['file_name']}")

# Usage
if __name__ == "__main__":
    process_document_queue()
```

---

## 🎬 Future: Twelve Labs Video/Audio Integration

### **Architecture:**

```python
# video_audio_processor.py (FUTURE)
import twelvelabs

class MediaProcessor:
    """Process video and audio files with Twelve Labs"""

    def __init__(self, api_key):
        self.client = twelvelabs.Client(api_key=api_key)

    def process_video(self, file_path):
        """Transcribe and analyze video"""

        # Upload to Twelve Labs
        task = self.client.tasks.create(
            file=file_path,
            engines=['transcription', 'visual', 'audio']
        )

        # Get results
        results = {
            'transcription': task.transcription,
            'scenes': task.visual_scenes,
            'speakers': task.audio_speakers,
            'topics': task.topics,
            'emotions': task.emotions
        }

        # Store in Supabase
        supabase.table('media_analysis').insert({
            'file_hash': calculate_hash(file_path),
            'file_name': Path(file_path).name,
            'transcription': results['transcription'],
            'analysis': results
        }).execute()

        return results

# Schema for video/audio
CREATE TABLE media_analysis (
    id BIGSERIAL PRIMARY KEY,
    file_hash TEXT REFERENCES master_document_registry(file_hash),
    file_name TEXT,
    file_type TEXT,  -- mp4, mp3, wav, etc.
    duration_seconds INTEGER,

    -- Twelve Labs results
    transcription TEXT,
    speakers JSONB,  -- Speaker identification
    scenes JSONB,  -- Visual scene detection
    topics JSONB,  -- Topic classification
    emotions JSONB,  -- Emotion analysis

    -- Embeddings for semantic search
    transcription_embedding vector(1536),

    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 💰 Cost Estimate

### **One-Time Setup:**
| Task | Cost |
|------|------|
| Scan all sources | $0 |
| Upload to registry | $0 |
| Extract 570 documents | $0 |
| Process with Claude | ~$6 (570 × $0.01) |
| Generate embeddings | ~$0.57 (570 × $0.001) |
| **Total Setup** | **~$6.57** |

### **Monthly Ongoing:**
| Service | Cost |
|---------|------|
| Supabase (Free tier) | $0 |
| Vector embeddings (incremental) | ~$0.10 |
| Claude processing (new docs) | ~$0.50 |
| Google Drive API | $0 |
| **Total Monthly** | **~$0.60** |

### **Future Additions:**
| Service | Cost |
|---------|------|
| Neo4j Community (self-hosted) | $0 |
| Neo4j Aura (cloud) | $65/month |
| Twelve Labs (transcription) | $0.03/min |
| Twelve Labs (100 hours) | ~$180 |

---

## 📋 Implementation Checklist

### **Phase 1: Scan & Register (This Week)**
- [ ] Run laptop scanner: `python3 scan_local_sources.py`
- [ ] Run Mac Mini scanner (when home)
- [ ] Set up Google Drive API credentials
- [ ] Run Google Drive scanner: `python3 scan_google_drive.py`
- [ ] Consolidate registries: `python3 consolidate_registries.py`
- [ ] Deploy master registry SQL to Supabase

### **Phase 2: Process & Analyze (Next Week)**
- [ ] Add OpenAI key to secrets.toml
- [ ] Process document queue: `python3 process_all_sources.py`
- [ ] Generate embeddings for all documents
- [ ] Test semantic search

### **Phase 3: Graph RAG (Month 2)**
- [ ] Set up Neo4j (Community Edition)
- [ ] Design relationship schema
- [ ] Build knowledge graph
- [ ] Create graph visualization

### **Phase 4: Video/Audio (Month 3)**
- [ ] Get Twelve Labs API key
- [ ] Set up media_analysis table
- [ ] Process video/audio files
- [ ] Integrate transcriptions with search

---

## 🎯 Next Immediate Steps

**Right now:**
1. ✅ Add OpenAI key to secrets.toml
2. ⏳ Deploy master registry SQL
3. ⏳ Run laptop scanner
4. ⏳ Consolidate with existing PROJ344 documents

**This week:**
1. Scan Mac Mini (when home)
2. Set up Google Drive API
3. Process all discovered documents

---

**For Ashe. For Justice. For All Children.** 🛡️
