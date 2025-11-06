# Tiered Deduplication Strategy + Mobile Scanner
**Smart content-based duplicate detection with mobile document capture**

---

## 🚨 Problem: Current Approach is Flawed

### **Why MD5 Hash Alone Fails:**

```
Original file: "JUV_2024_Motion.pdf" → Hash: abc123
Renamed file: "Alameda_Custody_Motion_Ashe.pdf" → Hash: def456
SAME CONTENT but different hash! ❌

Already processed in Supabase: "Motion for Custody.pdf"
New scan from phone: "IMG_20251106_143022.jpg" (same document photo)
DUPLICATE but no hash match! ❌
```

### **Better Approach: Tiered Content Matching**

```
Tier 0: Filename similarity (fast, free)
   ↓ No match?
Tier 1: OCR text extraction + fuzzy matching (local Tesseract)
   ↓ No match?
Tier 2: AI embeddings + semantic similarity (pgvector)
   ↓ No match?
CONFIRMED NEW DOCUMENT → Process
```

---

## 🎯 Tiered Deduplication System

### **Architecture:**

```
New Document Input
       │
       ↓
┌─────────────────────────────────────┐
│ TIER 0: Filename Matching           │
│ - Fuzzy string matching             │
│ - Levenshtein distance              │
│ - Common patterns (JUV, CPSR, etc.) │
│ Cost: $0 | Speed: <1ms              │
└─────────────────────────────────────┘
       │
       ↓ 70% match? → SKIP (likely duplicate)
       ↓ <70% match? → Continue
       ↓
┌─────────────────────────────────────┐
│ TIER 1: OCR Content Matching        │
│ - Extract text with Tesseract       │
│ - Compare first 1000 chars          │
│ - Jaccard similarity score          │
│ Cost: $0 (local) | Speed: 2-5s      │
└─────────────────────────────────────┘
       │
       ↓ 85% match? → SKIP (duplicate content)
       ↓ <85% match? → Continue
       ↓
┌─────────────────────────────────────┐
│ TIER 2: AI Semantic Matching        │
│ - Generate embedding (OpenAI)       │
│ - Query pgvector for similar docs   │
│ - Cosine similarity > 0.95          │
│ Cost: $0.0001 | Speed: 500ms        │
└─────────────────────────────────────┘
       │
       ↓ >0.95 similarity? → SKIP (semantic duplicate)
       ↓ <0.95 similarity? → NEW DOCUMENT
       ↓
┌─────────────────────────────────────┐
│ CONFIRMED NEW DOCUMENT              │
│ - Full processing                   │
│ - Store in repository               │
│ - Generate embeddings               │
│ - Add to search index               │
└─────────────────────────────────────┘
```

---

## 📱 Mobile Phone Scanner

### **How It Works:**

```
┌─────────────────────────────────┐
│  Your Phone (iOS/Android)       │
│                                 │
│  1. Open mobile web app         │
│  2. Tap "Scan Document"         │
│  3. Camera captures photo       │
│  4. Auto-crop & enhance         │
│  5. OCR extraction (local)      │
│  6. Check for duplicates        │
│  7. Upload to Supabase          │
└─────────────────────────────────┘
         │
         ↓ HTTPS Upload
         ↓
┌─────────────────────────────────┐
│  FastAPI Backend                │
│  (Running on laptop or cloud)   │
│                                 │
│  - Receive upload               │
│  - Run tiered deduplication     │
│  - Process if new               │
│  - Return status to phone       │
└─────────────────────────────────┘
         │
         ↓ Store
         ↓
┌─────────────────────────────────┐
│  Supabase Database              │
│  - master_document_registry     │
│  - document_repository          │
│  - document_embeddings          │
└─────────────────────────────────┘
```

---

## 🏗️ Mobile Scanner Architecture

### **Option 1: Progressive Web App (PWA)** ✅ RECOMMENDED

**Pros:**
- Works on ALL phones (iOS + Android)
- No app store approval needed
- Install to home screen
- Works offline
- Access phone camera

**Tech Stack:**
- Frontend: HTML5 + JavaScript
- Camera: WebRTC / getUserMedia API
- OCR: Tesseract.js (runs in browser)
- Upload: Fetch API → Supabase
- Offline: Service Workers + IndexedDB

**User Experience:**
```
1. Visit: https://aseagi-scanner.app (or local IP)
2. "Add to Home Screen" → App icon appears
3. Open app → Camera view
4. Snap photo → Auto-processes
5. Shows: "✅ New document" or "⚠️ Duplicate detected"
6. Uploads when online
```

---

### **Option 2: Native Mobile App**

**Pros:**
- Better performance
- Native camera access
- Push notifications
- App store presence

**Cons:**
- Need to build for iOS + Android separately
- App store approval (weeks)
- More development time

---

## 💻 Implementation: Tiered Deduplication

### **Tier 0: Filename Matching**

```python
# tier0_filename_matcher.py
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
import re

class FilenameMatcher:
    """Fast filename-based duplicate detection"""

    def __init__(self, supabase):
        self.supabase = supabase

    def normalize_filename(self, filename: str) -> str:
        """Normalize filename for comparison"""
        # Remove extension
        name = filename.rsplit('.', 1)[0]

        # Remove common prefixes/suffixes
        name = re.sub(r'(IMG_|SCAN_|DOC_|Copy of |Final |Draft )', '', name, flags=re.IGNORECASE)

        # Remove numbers (dates, versions)
        name = re.sub(r'\d+', '', name)

        # Remove special chars
        name = re.sub(r'[_\-\.]', ' ', name)

        # Lowercase and strip
        return name.lower().strip()

    def find_similar_filenames(self, filename: str, threshold: float = 0.7):
        """Find documents with similar filenames"""

        normalized = self.normalize_filename(filename)

        # Get all documents from registry
        docs = self.supabase.table('master_document_registry')\
            .select('file_name, file_hash, id')\
            .execute()

        matches = []

        for doc in docs.data:
            existing_normalized = self.normalize_filename(doc['file_name'])

            # Calculate similarity
            similarity = fuzz.ratio(normalized, existing_normalized) / 100.0

            if similarity >= threshold:
                matches.append({
                    'file_name': doc['file_name'],
                    'file_hash': doc['file_hash'],
                    'similarity': similarity,
                    'match_type': 'filename'
                })

        return sorted(matches, key=lambda x: x['similarity'], reverse=True)


# Usage
matcher = FilenameMatcher(supabase)
matches = matcher.find_similar_filenames('JUV_2024_Custody_Motion.pdf')

if matches and matches[0]['similarity'] > 0.7:
    print(f"⚠️ Possible duplicate: {matches[0]['file_name']} ({matches[0]['similarity']:.0%} match)")
    print("SKIP Tier 1 & 2")
else:
    print("✅ No filename match, proceeding to Tier 1")
```

---

### **Tier 1: OCR Content Matching**

```python
# tier1_ocr_matcher.py
import pytesseract
from PIL import Image
import io
from difflib import SequenceMatcher

class OCRMatcher:
    """OCR-based content duplicate detection"""

    def __init__(self, supabase):
        self.supabase = supabase

    def extract_text(self, file_path_or_bytes) -> str:
        """Extract text using Tesseract OCR"""

        if isinstance(file_path_or_bytes, bytes):
            image = Image.open(io.BytesIO(file_path_or_bytes))
        else:
            image = Image.open(file_path_or_bytes)

        # Extract text
        text = pytesseract.image_to_string(image)

        return text.strip()

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between texts"""

        # Normalize
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()

        # Take first 1000 chars (representative sample)
        text1 = text1[:1000]
        text2 = text2[:1000]

        # Calculate Jaccard similarity
        set1 = set(text1.split())
        set2 = set(text2.split())

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        if union == 0:
            return 0.0

        return intersection / union

    def find_similar_content(self, new_text: str, threshold: float = 0.85):
        """Find documents with similar OCR content"""

        # Get all documents with OCR text
        docs = self.supabase.table('document_repository')\
            .select('id, file_name, content')\
            .execute()

        matches = []

        for doc in docs.data:
            existing_text = doc.get('content', '')

            if not existing_text:
                continue

            similarity = self.calculate_text_similarity(new_text, existing_text)

            if similarity >= threshold:
                matches.append({
                    'file_name': doc['file_name'],
                    'document_id': doc['id'],
                    'similarity': similarity,
                    'match_type': 'ocr_content'
                })

        return sorted(matches, key=lambda x: x['similarity'], reverse=True)


# Usage
ocr_matcher = OCRMatcher(supabase)

# Extract text from new document
new_text = ocr_matcher.extract_text('scanned_document.pdf')

# Find similar
matches = ocr_matcher.find_similar_content(new_text)

if matches and matches[0]['similarity'] > 0.85:
    print(f"⚠️ Duplicate content detected: {matches[0]['file_name']} ({matches[0]['similarity']:.0%} match)")
    print("SKIP Tier 2")
else:
    print("✅ No OCR match, proceeding to Tier 2")
```

---

### **Tier 2: AI Semantic Matching**

```python
# tier2_semantic_matcher.py
import openai
from supabase import create_client

class SemanticMatcher:
    """AI embeddings-based semantic duplicate detection"""

    def __init__(self, supabase, openai_key):
        self.supabase = supabase
        openai.api_key = openai_key

    def generate_embedding(self, text: str):
        """Generate embedding for text"""

        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text[:8000]  # Max tokens
        )

        return response['data'][0]['embedding']

    def find_similar_embeddings(self, text: str, threshold: float = 0.95):
        """Find semantically similar documents using pgvector"""

        # Generate embedding for new text
        embedding = self.generate_embedding(text)

        # Query pgvector for similar documents
        # Uses cosine similarity via <=> operator
        result = self.supabase.rpc('match_documents', {
            'query_embedding': embedding,
            'match_threshold': threshold,
            'match_count': 5
        }).execute()

        matches = []
        for doc in result.data:
            matches.append({
                'file_name': doc['file_name'],
                'document_id': doc['document_id'],
                'similarity': doc['similarity'],
                'match_type': 'semantic'
            })

        return matches


# Usage
semantic_matcher = SemanticMatcher(supabase, openai_key)

matches = semantic_matcher.find_similar_embeddings(new_text)

if matches and matches[0]['similarity'] > 0.95:
    print(f"⚠️ Semantic duplicate: {matches[0]['file_name']} ({matches[0]['similarity']:.0%} similar)")
    print("SKIP processing")
else:
    print("✅ CONFIRMED NEW DOCUMENT - Process fully")
```

---

## 📱 Mobile Scanner Implementation

### **Progressive Web App (PWA)**

```html
<!-- mobile_scanner.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <title>ASEAGI Document Scanner</title>
    <link rel="manifest" href="/manifest.json">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #000;
            color: #fff;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            padding: 20px 0;
        }

        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }

        .header p {
            color: #999;
            font-size: 14px;
        }

        #camera-view {
            width: 100%;
            max-height: 70vh;
            background: #222;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
        }

        #video {
            width: 100%;
            height: auto;
        }

        #canvas {
            display: none;
        }

        .controls {
            margin-top: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        button {
            flex: 1;
            min-width: 150px;
            padding: 15px;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-primary {
            background: #007AFF;
            color: white;
        }

        .btn-primary:hover {
            background: #0051D5;
        }

        .btn-secondary {
            background: #333;
            color: white;
        }

        .btn-success {
            background: #34C759;
            color: white;
        }

        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            background: #1C1C1E;
        }

        .status.success {
            background: #1B5E20;
        }

        .status.warning {
            background: #F57C00;
        }

        .status.error {
            background: #C62828;
        }

        .preview {
            margin-top: 20px;
        }

        .preview img {
            width: 100%;
            border-radius: 8px;
        }

        .duplicate-info {
            background: #FFF3CD;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #007AFF;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ ASEAGI Scanner</h1>
            <p>Document Scanner with Smart Deduplication</p>
        </div>

        <div id="camera-view">
            <video id="video" autoplay playsinline></video>
            <canvas id="canvas"></canvas>
        </div>

        <div class="controls">
            <button id="start-camera" class="btn-primary">Start Camera</button>
            <button id="capture" class="btn-success" style="display:none;">Capture Document</button>
            <button id="upload-file" class="btn-secondary">Upload File</button>
            <input type="file" id="file-input" accept="image/*,application/pdf" style="display:none;">
        </div>

        <div id="status" class="status" style="display:none;"></div>

        <div id="preview" class="preview" style="display:none;">
            <h3>Captured Image:</h3>
            <img id="preview-img" src="" alt="Preview">
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@4/dist/tesseract.min.js"></script>
    <script>
        // Mobile Scanner JavaScript
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const startCameraBtn = document.getElementById('start-camera');
        const captureBtn = document.getElementById('capture');
        const uploadFileBtn = document.getElementById('upload-file');
        const fileInput = document.getElementById('file-input');
        const statusDiv = document.getElementById('status');
        const previewDiv = document.getElementById('preview');
        const previewImg = document.getElementById('preview-img');

        const SUPABASE_URL = 'https://jvjlhxodmbkodzmggwpu.supabase.co';
        const SUPABASE_KEY = 'your-anon-key';

        // Start camera
        startCameraBtn.addEventListener('click', async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'environment' }  // Use back camera
                });
                video.srcObject = stream;
                startCameraBtn.style.display = 'none';
                captureBtn.style.display = 'block';
                showStatus('Camera ready ✅', 'success');
            } catch (error) {
                showStatus('Camera access denied ❌', 'error');
            }
        });

        // Capture photo
        captureBtn.addEventListener('click', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);

            // Get image data
            canvas.toBlob(async (blob) => {
                await processDocument(blob);
            }, 'image/jpeg', 0.95);
        });

        // Upload file
        uploadFileBtn.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file) {
                await processDocument(file);
            }
        });

        // Process document with tiered deduplication
        async function processDocument(blob) {
            showStatus('Processing... <div class="spinner"></div>', 'info');

            try {
                // Show preview
                const url = URL.createObjectURL(blob);
                previewImg.src = url;
                previewDiv.style.display = 'block';

                // Step 1: Extract text with Tesseract.js
                showStatus('Extracting text... 📄', 'info');
                const { data: { text } } = await Tesseract.recognize(blob, 'eng');

                // Step 2: Check for duplicates
                showStatus('Checking for duplicates... 🔍', 'info');
                const isDuplicate = await checkDuplicates(text, blob);

                if (isDuplicate) {
                    showStatus(`⚠️ Duplicate detected!<br>Similar to: ${isDuplicate.file_name}<br>Similarity: ${(isDuplicate.similarity * 100).toFixed(0)}%`, 'warning');
                } else {
                    // Step 3: Upload to Supabase
                    showStatus('Uploading... ☁️', 'info');
                    await uploadToSupabase(blob, text);
                    showStatus('✅ Document uploaded successfully!', 'success');
                }

            } catch (error) {
                showStatus('❌ Error: ' + error.message, 'error');
            }
        }

        // Check for duplicates (calls backend API)
        async function checkDuplicates(text, blob) {
            // This would call your FastAPI backend
            // For now, returning mock data
            const response = await fetch('/api/check-duplicate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text.substring(0, 1000) })
            });

            if (response.ok) {
                const result = await response.json();
                return result.is_duplicate ? result : null;
            }

            return null;
        }

        // Upload to Supabase
        async function uploadToSupabase(blob, text) {
            const filename = `mobile_scan_${Date.now()}.jpg`;

            // Upload to Supabase Storage
            const formData = new FormData();
            formData.append('file', blob, filename);

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            return response.json();
        }

        // Show status message
        function showStatus(message, type) {
            statusDiv.innerHTML = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
        }

        // Install PWA
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js');
        }
    </script>
</body>
</html>
```

---

## 🚀 Deployment

### **Option A: Run on Local Network**

```bash
# Start FastAPI backend on laptop
python3 mobile_scanner_api.py

# Access from phone:
# http://192.168.1.100:8000
# (Your laptop's local IP)
```

### **Option B: Deploy to Cloud**

```bash
# Deploy to Vercel/Netlify (free)
vercel deploy

# Access from anywhere:
# https://aseagi-scanner.vercel.app
```

---

## 💰 Cost Comparison

| Tier | Speed | Cost | When to Use |
|------|-------|------|-------------|
| Tier 0: Filename | <1ms | $0 | Always check first |
| Tier 1: OCR | 2-5s | $0 | After Tier 0 fails |
| Tier 2: Embeddings | 500ms | $0.0001 | After Tier 1 fails |
| Full Processing | 10-30s | $0.01 | Only if all tiers fail |

**Cost savings example:**
- 1000 documents scanned
- 400 caught by Tier 0 (filename) → Save $4
- 300 caught by Tier 1 (OCR) → Save $3
- 200 caught by Tier 2 (embeddings) → Save $1.98
- 100 new documents → Process for $1
- **Total cost: $1.02 instead of $10**

---

## ✅ Next Steps

1. **Deploy master registry schema** (if not done)
2. **Install Tesseract OCR**: `brew install tesseract` (Mac) or `apt-get install tesseract-ocr` (Linux)
3. **Create FastAPI backend** for mobile scanner
4. **Test mobile scanner** on local network
5. **Deploy to cloud** for anywhere access

**What would you like me to build first?**
1. Tiered deduplication implementation files
2. Mobile scanner PWA
3. FastAPI backend for mobile integration
4. All of the above

