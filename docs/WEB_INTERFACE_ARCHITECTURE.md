# PROJ344 Web Interface - Unified Bot & Service Management
**Comprehensive Control Panel for All ASEAGI Services**

## 🎯 Overview

A unified web interface to manage, monitor, and execute all PROJ344 bots, services, and analysis scripts from a single dashboard.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    WEB INTERFACE (Port 8500)                     │
│                     React + FastAPI Backend                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Navigation:                                                     │
│  [Dashboard] [Bots] [Scanners] [Analysis] [Documents] [Logs]   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                             │
│                     (REST API + WebSocket)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Endpoints:                                                      │
│  - /api/bots/*          - Bot management                        │
│  - /api/scanners/*      - Scanner execution                     │
│  - /api/analysis/*      - Analysis jobs                         │
│  - /api/documents/*     - Document operations                   │
│  - /api/system/*        - System monitoring                     │
│  - /ws                  - Real-time updates                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SERVICE MANAGERS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Bot Manager    │  Scanner Manager  │  Analysis Manager         │
│  - Telegram Bot │  - WhatsApp       │  - Violation Detection   │
│  - Status       │  - Document OCR   │  - Timeline Builder      │
│  - Start/Stop   │  - Batch Process  │  - Motion Generator      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📱 Interface Sections

### 1. 🏠 **MAIN DASHBOARD** (`/`)

Real-time overview of all services:

```
┌────────────────────────────────────────────────────────────────┐
│ PROJ344 Control Center                              [Settings] │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⚡ SYSTEM STATUS                                              │
│  ├─ CPU: 45%      Memory: 2.1GB/4GB    Disk: 78GB/100GB       │
│  └─ Uptime: 10h 32m                    Supabase: ✅ Connected │
│                                                                 │
│  🤖 BOTS & SERVICES                                            │
│  ┌────────────────────┬─────────┬──────────┬─────────────────┐│
│  │ Service            │ Status  │ Uptime   │ Actions         ││
│  ├────────────────────┼─────────┼──────────┼─────────────────┤│
│  │ 📱 Telegram Bot    │ 🟢 Run  │ 2h 15m   │ [Stop] [Logs]   ││
│  │ 📊 WhatsApp Analyz │ ⚫ Stop  │ --       │ [Start] [Config]││
│  │ 🔍 Violation Scan  │ 🟡 Queue│ --       │ [View] [Cancel] ││
│  │ 📄 OCR Processor   │ 🟢 Run  │ 45m      │ [Stop] [Logs]   ││
│  │ 🤖 ASEAGI Bot      │ 🟢 Run  │ 10h 32m  │ [Restart] [Log] ││
│  └────────────────────┴─────────┴──────────┴─────────────────┘│
│                                                                 │
│  📈 RECENT ACTIVITY                                            │
│  ├─ 12:53 PM - Telegram: 12 documents received                │
│  ├─ 12:55 PM - OCR: Processing 12 images                      │
│  ├─ 01:02 PM - Violation Analysis: Running (3/12 complete)    │
│  └─ 01:05 PM - Database: 665 total documents                  │
│                                                                 │
│  🎯 QUICK ACTIONS                                              │
│  [📤 Upload Document] [🔍 Run Analysis] [📊 View Dashboards]  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 2. 🤖 **BOT MANAGEMENT** (`/bots`)

Control all bots from one place:

```
┌────────────────────────────────────────────────────────────────┐
│ Bot Management                              [+ Create New Bot] │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📱 TELEGRAM BOT                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Status: 🟢 Running (PID: 1138559)                        │ │
│  │ Uptime: 2h 15m 43s                                       │ │
│  │ Documents Received Today: 12                             │ │
│  │ Storage: /root/phase0_bug_tracker/data/telegram-inbox/   │ │
│  │                                                           │ │
│  │ [⏹️ Stop] [🔄 Restart] [📋 View Logs] [⚙️ Settings]       │ │
│  │                                                           │ │
│  │ Recent Messages:                                          │ │
│  │ • 12:53 PM - Received: Screenshot_20250930_174447...     │ │
│  │ • 12:53 PM - Stored in: telegram-inbox/2025-11-10/       │ │
│  │ • 12:53 PM - Uploaded to database: c9e504dd...           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  🤖 ASEAGI LEGAL ASSISTANT BOT                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Status: 🟢 Running                                        │ │
│  │ Commands Available: /search, /timeline, /violations      │ │
│  │ Users: 1 active                                           │ │
│  │                                                           │ │
│  │ [⏹️ Stop] [🔄 Restart] [📋 View Logs] [⚙️ Settings]       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  📲 N8N WORKFLOWS                                              │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Status: ⚫ Not Configured                                 │ │
│  │                                                           │ │
│  │ [▶️ Setup N8N] [📖 Documentation]                         │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 3. 🔍 **SCANNERS & PROCESSORS** (`/scanners`)

Execute document processing:

```
┌────────────────────────────────────────────────────────────────┐
│ Scanners & Document Processors                                  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WHATSAPP ANALYZER                                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Analyze WhatsApp chat exports for violations             │ │
│  │                                                           │ │
│  │ Input File: [📁 Browse] ___________________________      │ │
│  │             (or drag & drop .txt file here)              │ │
│  │                                                           │ │
│  │ Options:                                                  │ │
│  │ ☑ Group by date                                          │ │
│  │ ☑ Detect violations                                      │ │
│  │ ☑ Extract key quotes                                     │ │
│  │                                                           │ │
│  │ Cost Estimate: $1.00 - $2.00                             │ │
│  │                                                           │ │
│  │ [▶️ Run Analysis]                                        │ │
│  │                                                           │ │
│  │ Last Run: 50 segments processed, $1.12 cost             │ │
│  │ [📊 View Results]                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  DOCUMENT OCR & ANALYSIS                                       │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Extract text and analyze for violations                  │ │
│  │                                                           │ │
│  │ Source:                                                   │ │
│  │ ○ Upload files  ○ Telegram inbox  ○ Specific folder     │ │
│  │                                                           │ │
│  │ Telegram Inbox (12 pending):                             │ │
│  │ ☑ Screenshot_20250930_174447_Adobe Acrobat.jpg          │ │
│  │ ☑ Screenshot_20250930_174459_Adobe Acrobat.jpg          │ │
│  │ ☑ Screenshot_20250930_174511_Adobe Acrobat.jpg          │ │
│  │ ... (9 more)                                              │ │
│  │                                                           │ │
│  │ Analysis Type:                                            │ │
│  │ ☑ OCR Text Extraction                                    │ │
│  │ ☑ Violation Detection                                    │ │
│  │ ☑ Entity Extraction                                      │ │
│  │                                                           │ │
│  │ [▶️ Process Selected (12)]  [⏸️ Queue]                   │ │
│  │                                                           │ │
│  │ Current: Processing 3/12 (25%)                           │ │
│  │ [━━━━━━━━░░░░░░░░░░░░░░░░░░] 25%                        │ │
│  │ Est. Time: 6 minutes    Est. Cost: $0.48                │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  BATCH REPROCESSING                                            │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Re-analyze existing documents                            │ │
│  │                                                           │ │
│  │ Filter Documents:                                         │ │
│  │ Date Range: [2024-08-01] to [2024-08-31]                │ │
│  │ Document Type: [All ▾]                                   │ │
│  │ Current Status: [RECEIVED ▾]                             │ │
│  │                                                           │ │
│  │ Found: 15 documents                                       │ │
│  │                                                           │ │
│  │ [▶️ Reprocess All]  [Preview]                            │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 4. ⚖️ **VIOLATION ANALYSIS** (`/analysis`)

Run and view violation detection:

```
┌────────────────────────────────────────────────────────────────┐
│ Violation Analysis Center                                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 ANALYSIS DASHBOARD                                         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Total Violations Detected                                │ │
│  │                                                           │ │
│  │ 🏛️  Constitutional: 23    ⚖️  Perjury: 15              │ │
│  │ 🚨 Fraud: 8              📋 Procedural: 31              │ │
│  │                                                           │ │
│  │ By Severity:                                              │ │
│  │ 🔴 CRITICAL: 5    🟠 HIGH: 12    🟡 MEDIUM: 38          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  🔍 RUN NEW ANALYSIS                                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Analysis Type:                                            │ │
│  │ ☐ Constitutional Violations                              │ │
│  │ ☐ Perjury Detection                                      │ │
│  │ ☐ Fraud Indicators                                       │ │
│  │ ☐ Timeline Contradictions                                │ │
│  │ ☐ Full Case Review                                       │ │
│  │                                                           │ │
│  │ Scope:                                                    │ │
│  │ ○ All Documents (653)                                    │ │
│  │ ○ Date Range: [________] to [________]                  │ │
│  │ ○ Specific Documents (Select from list)                 │ │
│  │                                                           │ │
│  │ AI Model: [Claude Opus 4 ▾]                             │ │
│  │                                                           │ │
│  │ Cost Estimate: $15.20 - $22.50                           │ │
│  │                                                           │ │
│  │ [▶️ Start Analysis]  [💾 Save Configuration]             │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  📈 ANALYSIS JOBS                                              │
│  ┌────────────────┬─────────┬──────────┬──────────────────┐  │
│  │ Job            │ Status  │ Progress │ Actions          │  │
│  ├────────────────┼─────────┼──────────┼──────────────────┤  │
│  │ Ex Parte OCR   │ 🟢 Run  │ 3/12     │ [View] [Cancel]  │  │
│  │ WhatsApp Scan  │ ✅ Done │ 50/50    │ [View] [Export]  │  │
│  │ Timeline Build │ ⏳ Queue│ --       │ [Start] [Edit]   │  │
│  └────────────────┴─────────┴──────────┴──────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 5. 📄 **DOCUMENT MANAGEMENT** (`/documents`)

Upload and manage documents:

```
┌────────────────────────────────────────────────────────────────┐
│ Document Management                         [📤 Upload New]     │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  RECENT UPLOADS                                                │
│  ┌────────────────┬──────┬────────┬──────────────────────────┐│
│  │ Filename       │ Type │ Date   │ Actions                  ││
│  ├────────────────┼──────┼────────┼──────────────────────────┤│
│  │ Screenshot...  │ DECL │ 8/13   │ [View] [Analyze] [Del]  ││
│  │ WhatsApp...    │ TEXT │ 11/10  │ [View] [Analyze] [Del]  ││
│  └────────────────┴──────┴────────┴──────────────────────────┘│
│                                                                 │
│  UPLOAD NEW DOCUMENTS                                          │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │          Drag & Drop Files Here                          │ │
│  │              or [Browse Files]                           │ │
│  │                                                           │ │
│  │  Supported: PDF, JPG, PNG, TXT, DOCX                     │ │
│  │                                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  BULK OPERATIONS                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Selected: 12 documents                                    │ │
│  │                                                           │ │
│  │ [🔍 Analyze All] [📋 Export Metadata] [🗑️ Delete]        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 6. 📋 **LOGS & MONITORING** (`/logs`)

Real-time logs from all services:

```
┌────────────────────────────────────────────────────────────────┐
│ System Logs                             🔄 Auto-refresh: ON     │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Filter: [All Services ▾]  Level: [All ▾]  [🔍 Search]         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 01:02:45 [TELEGRAM] INFO  - Received document            │ │
│  │ 01:02:46 [TELEGRAM] INFO  - Stored: telegram-inbox/...   │ │
│  │ 01:02:47 [DATABASE] INFO  - Inserted doc: c9e504dd...    │ │
│  │ 01:02:50 [OCR] INFO       - Starting OCR processing      │ │
│  │ 01:02:51 [OCR] INFO       - Extracted 2,847 characters   │ │
│  │ 01:02:52 [ANALYSIS] INFO  - Running violation detection  │ │
│  │ 01:03:15 [ANALYSIS] INFO  - Found 2 constitutional viol. │ │
│  │ 01:03:16 [DATABASE] INFO  - Updated doc: c9e504dd...     │ │
│  │ 01:03:17 [TELEGRAM] INFO  - Sent confirmation to user    │ │
│  │                                                           │ │
│  │                                                           │ │
│  │                         [Load More]                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  [📥 Download Logs] [🗑️ Clear] [⏸️ Pause Auto-Refresh]        │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technical Implementation

### Backend: FastAPI

```python
# app/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.routers import bots, scanners, analysis, documents, system

app = FastAPI(title="PROJ344 Control Center")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(bots.router, prefix="/api/bots", tags=["bots"])
app.include_router(scanners.router, prefix="/api/scanners", tags=["scanners"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(system.router, prefix="/api/system", tags=["system"])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Stream logs and status updates
    ...
```

### Key API Endpoints

```python
# Bot Management
POST   /api/bots/telegram/start
POST   /api/bots/telegram/stop
GET    /api/bots/telegram/status
GET    /api/bots/telegram/logs

# Scanner Execution
POST   /api/scanners/whatsapp/analyze
POST   /api/scanners/ocr/process
GET    /api/scanners/jobs/{job_id}
DELETE /api/scanners/jobs/{job_id}

# Violation Analysis
POST   /api/analysis/run
GET    /api/analysis/results
GET    /api/analysis/stats

# Document Management
POST   /api/documents/upload
GET    /api/documents/list
DELETE /api/documents/{doc_id}

# System Monitoring
GET    /api/system/status
GET    /api/system/logs
GET    /api/system/metrics
```

### Frontend: React + TypeScript

```typescript
// src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import BotManagement from './pages/BotManagement';
import Scanners from './pages/Scanners';
import Analysis from './pages/Analysis';
import Documents from './pages/Documents';
import Logs from './pages/Logs';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/bots" element={<BotManagement />} />
          <Route path="/scanners" element={<Scanners />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/logs" element={<Logs />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
```

### Real-time Updates: WebSocket

```typescript
// src/hooks/useWebSocket.ts
export function useWebSocket() {
  const [messages, setMessages] = useState<LogMessage[]>([]);

  useEffect(() => {
    const ws = new WebSocket('ws://137.184.1.91:8500/ws');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, data]);
    };

    return () => ws.close();
  }, []);

  return messages;
}
```

---

## 🚀 Deployment

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  control-center-backend:
    build: ./backend
    ports:
      - "8500:8500"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/data
      - /var/run/docker.sock:/var/run/docker.sock  # For managing other containers

  control-center-frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - control-center-backend
```

### Quick Start

```bash
# Clone and setup
cd /root/phase0_bug_tracker
mkdir -p control-center/{backend,frontend}

# Start services
docker-compose up -d

# Access interface
# http://137.184.1.91:3000  (Frontend)
# http://137.184.1.91:8500  (API Docs)
```

---

## ✨ Key Features

### 1. **Unified Bot Control**
- Start/stop all bots from one interface
- View real-time logs
- Configure bot settings
- Monitor bot health

### 2. **One-Click Analysis**
- Upload documents via drag-and-drop
- Run OCR and violation detection
- Batch process multiple documents
- Track job progress in real-time

### 3. **Visual Job Management**
- Queue analysis jobs
- Monitor progress bars
- Cost estimation before running
- Cancel long-running jobs

### 4. **Real-Time Monitoring**
- Live logs streaming via WebSocket
- System resource usage graphs
- Bot status indicators
- Alert notifications

### 5. **Document Library**
- Browse all uploaded documents
- Filter by date, type, status
- Bulk operations
- Export metadata

---

## 📊 Benefits

✅ **Single Source of Truth** - All services manageable from one place
✅ **User-Friendly** - No command-line needed
✅ **Real-Time** - Live updates via WebSocket
✅ **Cost Aware** - See estimates before running expensive operations
✅ **Scalable** - Easy to add new bots and scanners
✅ **Professional** - Clean, modern interface

---

## 🎯 Next Steps

1. **Phase 1**: Build FastAPI backend with core endpoints
2. **Phase 2**: Create React frontend with dashboard
3. **Phase 3**: Add WebSocket for real-time updates
4. **Phase 4**: Deploy to droplet and integrate with existing services
5. **Phase 5**: Add authentication and user management

---

**Access Points After Deployment:**
- Control Center: http://137.184.1.91:3000
- API Documentation: http://137.184.1.91:8500/docs
- Existing Dashboards: http://137.184.1.91:8501-8506

**For Ashe. For Justice. For All Children. 🛡️**
