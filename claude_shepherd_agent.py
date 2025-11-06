#!/usr/bin/env python3
"""
Claude Shepherd Agent - AI Guardian for ASEAGI Repository
Monitors, reviews, and guides the entire codebase using Claude AI + Qdrant
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import asyncio
from typing import Dict, Any, List, Optional
import hashlib

# Core imports
try:
    import anthropic
    from github import Github
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    import tiktoken
    from supabase import create_client, Client
    import pandas as pd
except ImportError:
    print("❌ Install: pip install anthropic PyGithub qdrant-client tiktoken supabase pandas")
    sys.exit(1)

# Load credentials
CLAUDE_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'dondada876/ASEAGI')
QDRANT_URL = os.environ.get('QDRANT_URL', 'localhost')
QDRANT_API_KEY = os.environ.get('QDRANT_API_KEY')
QDRANT_PORT = int(os.environ.get('QDRANT_PORT', 6333))
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Fallback to secrets
if not CLAUDE_API_KEY:
    try:
        import toml
        secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
        if secrets_path.exists():
            secrets = toml.load(secrets_path)
            CLAUDE_API_KEY = secrets.get('ANTHROPIC_API_KEY')
            GITHUB_TOKEN = secrets.get('GITHUB_TOKEN')
            QDRANT_URL = secrets.get('QDRANT_URL', 'localhost')
            QDRANT_API_KEY = secrets.get('QDRANT_API_KEY')
            SUPABASE_URL = secrets.get('SUPABASE_URL')
            SUPABASE_KEY = secrets.get('SUPABASE_KEY')
    except:
        pass

# Initialize clients
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None
github_client = Github(GITHUB_TOKEN) if GITHUB_TOKEN else None
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Initialize Qdrant
if QDRANT_URL and QDRANT_URL != 'localhost':
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=60
    )
else:
    qdrant_client = QdrantClient(host='localhost', port=QDRANT_PORT)

COLLECTION_NAME = "aseagi_codebase"


# ============================================================================
# REPOSITORY INDEXING
# ============================================================================

class RepositoryIndexer:
    """Index entire repository into Qdrant for semantic search"""

    def __init__(self, repo_name: str = GITHUB_REPO):
        self.repo_name = repo_name
        self.repo = github_client.get_repo(repo_name) if github_client else None
        self.encoder = tiktoken.get_encoding("cl100k_base")

    async def index_repository(self):
        """Index entire repository"""
        print(f"🔍 Indexing repository: {self.repo_name}")

        # Create collection if not exists
        try:
            qdrant_client.get_collection(COLLECTION_NAME)
            print(f"✅ Collection '{COLLECTION_NAME}' exists")
        except:
            print(f"📦 Creating collection '{COLLECTION_NAME}'")
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )

        # Get all files
        contents = self.repo.get_contents("")
        all_files = []

        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(self.repo.get_contents(file_content.path))
            else:
                all_files.append(file_content)

        print(f"📄 Found {len(all_files)} files")

        # Index each file
        points = []
        for idx, file in enumerate(all_files):
            if file.size > 100000:  # Skip very large files
                continue

            try:
                content = file.decoded_content.decode('utf-8')

                # Get embeddings from Claude (or use alternative)
                embedding = await self._get_embedding(content[:8000])  # Limit size

                # Create point
                point = PointStruct(
                    id=idx,
                    vector=embedding,
                    payload={
                        "path": file.path,
                        "name": file.name,
                        "sha": file.sha,
                        "size": file.size,
                        "content": content[:2000],  # Store snippet
                        "url": file.html_url,
                        "indexed_at": datetime.now().isoformat()
                    }
                )
                points.append(point)

                if len(points) >= 100:  # Batch insert
                    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
                    print(f"✅ Indexed {idx + 1} files")
                    points = []

            except Exception as e:
                print(f"⚠️ Skipped {file.path}: {e}")

        # Insert remaining
        if points:
            qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)

        print(f"🎉 Indexing complete! Total files indexed: {len(all_files)}")

    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text (simplified - you'd use actual embedding API)"""
        # For now, return dummy embedding
        # In production, use OpenAI embeddings or similar
        return [0.1] * 1536


# ============================================================================
# CLAUDE SHEPHERD AGENT
# ============================================================================

class ClaudeShepherdAgent:
    """AI Agent that shepherds the entire repository"""

    def __init__(self):
        self.repo_name = GITHUB_REPO
        self.repo = github_client.get_repo(GITHUB_REPO) if github_client else None
        self.knowledge_base = self._build_knowledge_base()

    def _build_knowledge_base(self) -> str:
        """Build comprehensive knowledge base about the repository"""
        kb = f"""# ASEAGI Repository Knowledge Base

## Project Overview
Repository: {self.repo_name}
Purpose: Legal case intelligence system for custody case D22-03244

## Core Components

### 1. Document Ingestion System
- Telegram bot for mobile document upload
- n8n workflow processing pipeline
- Multi-tier storage (S3, Google Drive, Backblaze)
- Supabase database with 5 core tables:
  - telegram_uploads (source of truth)
  - processing_logs (audit trail)
  - storage_registry (file locations)
  - notification_queue (user notifications)
  - legal_documents (final processed documents)

### 2. Monitoring System
- Global monitoring bot for GitHub, n8n, Qdrant, Twelve Labs
- Real-time status checks via Telegram
- Automated alerts

### 3. Dashboards
- telegram_uploads_dashboard.py - View upload status
- proj344_master_dashboard.py - Legal case dashboard
- timeline_constitutional_violations.py - Timeline analysis

### 4. Processing Pipeline
- Validation → Storage → Extraction → Enhancement → Notification
- Error handling with retry logic
- Complete audit trail

## Architecture Principles
- Mobile-first design
- Complete audit trail
- Multi-tier storage
- Real-time notifications
- Semantic search via Qdrant

## Key Files
- telegram_document_bot.py - Document upload bot
- telegram_monitoring_bot.py - Global monitoring
- telegram_system_schema.sql - Database schema
- n8n_telegram_processing_workflow.json - Main processing
- DOCUMENT_INGESTION_PRD.md - Complete specification
"""
        return kb

    async def review_code(self, code: str, file_path: str, context: str = "") -> Dict[str, Any]:
        """Review code using Claude"""
        if not claude_client:
            return {"error": "Claude API not configured"}

        prompt = f"""You are the Shepherd Agent for the ASEAGI legal case management system.

Repository Context:
{self.knowledge_base}

Additional Context: {context}

File Being Reviewed: {file_path}

Code:
```
{code}
```

Please review this code as the project shepherd and provide:

1. **Alignment Check**: Does this code align with the project's architecture and principles?
2. **Quality Assessment**: Code quality, best practices, potential issues
3. **Security Review**: Any security concerns or vulnerabilities
4. **Integration Points**: How this integrates with existing components
5. **Suggestions**: Specific improvements or recommendations
6. **Risk Assessment**: Potential risks or breaking changes

Provide a comprehensive but concise review."""

        try:
            message = claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            review_text = message.content[0].text

            return {
                "file": file_path,
                "review": review_text,
                "model": "claude-sonnet-4",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    async def review_pr(self, pr_number: int) -> Dict[str, Any]:
        """Review an entire pull request"""
        if not self.repo:
            return {"error": "GitHub not configured"}

        pr = self.repo.get_pull(pr_number)
        files = pr.get_files()

        reviews = []
        for file in files:
            if file.patch:  # Only review changed files
                review = await self.review_code(
                    code=file.patch,
                    file_path=file.filename,
                    context=f"PR #{pr_number}: {pr.title}"
                )
                reviews.append(review)

        # Generate overall PR summary
        summary = await self._generate_pr_summary(pr, reviews)

        return {
            "pr_number": pr_number,
            "title": pr.title,
            "author": pr.user.login,
            "files_changed": len(list(files)),
            "reviews": reviews,
            "summary": summary,
            "recommendation": await self._get_pr_recommendation(reviews)
        }

    async def _generate_pr_summary(self, pr, reviews: List[Dict]) -> str:
        """Generate overall PR summary using Claude"""
        if not claude_client:
            return "Claude API not configured"

        reviews_text = "\n\n".join([
            f"File: {r['file']}\n{r.get('review', r.get('error', 'No review'))}"
            for r in reviews
        ])

        prompt = f"""As the Shepherd Agent, provide an executive summary of this pull request.

PR Title: {pr.title}
PR Description: {pr.body}
Author: {pr.user.login}

File Reviews:
{reviews_text}

Provide a concise executive summary covering:
1. What this PR does
2. Overall code quality
3. Alignment with project goals
4. Key concerns or recommendations
5. Merge recommendation (Approve / Request Changes / Needs Discussion)
"""

        try:
            message = claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating summary: {e}"

    async def _get_pr_recommendation(self, reviews: List[Dict]) -> str:
        """Get merge recommendation"""
        # Simple heuristic - in production, use Claude for this
        errors = sum(1 for r in reviews if 'error' in r)
        if errors > 0:
            return "❌ Cannot Review - Errors encountered"

        # Look for security or critical issues in reviews
        critical_keywords = ['security', 'critical', 'breaking', 'danger']
        for review in reviews:
            review_text = review.get('review', '').lower()
            if any(keyword in review_text for keyword in critical_keywords):
                return "⚠️ Request Changes - Critical issues found"

        return "✅ Approve - Looks good to merge"

    async def answer_question(self, question: str) -> str:
        """Answer questions about the repository using RAG"""
        if not claude_client:
            return "Claude API not configured"

        # Search Qdrant for relevant context
        # (Simplified - you'd use actual embeddings here)
        try:
            search_results = qdrant_client.scroll(
                collection_name=COLLECTION_NAME,
                limit=5
            )

            context_files = [
                f"File: {point.payload['path']}\nContent: {point.payload['content']}"
                for point, _ in search_results[0]
            ] if search_results else []

            context = "\n\n".join(context_files[:3])  # Top 3 results
        except:
            context = "No indexed data available"

        prompt = f"""You are the Shepherd Agent with complete knowledge of the ASEAGI repository.

Repository Knowledge:
{self.knowledge_base}

Relevant Code Context:
{context}

User Question: {question}

Provide a detailed, accurate answer based on your knowledge of the repository.
If you're uncertain, say so and suggest where to look."""

        try:
            message = claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error: {e}"

    async def analyze_architecture(self) -> Dict[str, Any]:
        """Analyze entire repository architecture"""
        if not self.repo:
            return {"error": "GitHub not configured"}

        # Get repository structure
        contents = self.repo.get_contents("")
        files = []

        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(self.repo.get_contents(file_content.path))
            else:
                files.append({
                    "path": file_content.path,
                    "name": file_content.name,
                    "size": file_content.size
                })

        # Categorize files
        python_files = [f for f in files if f['name'].endswith('.py')]
        sql_files = [f for f in files if f['name'].endswith('.sql')]
        md_files = [f for f in files if f['name'].endswith('.md')]
        json_files = [f for f in files if f['name'].endswith('.json')]

        # Analyze with Claude
        analysis_prompt = f"""Analyze the architecture of this repository:

Total Files: {len(files)}
Python Files: {len(python_files)}
SQL Files: {len(sql_files)}
Documentation: {len(md_files)}
Configuration: {len(json_files)}

Key Python Files:
{chr(10).join(['- ' + f['path'] for f in python_files[:20]])}

Provide architectural analysis including:
1. System architecture overview
2. Component relationships
3. Data flow
4. Potential improvements
5. Missing components or gaps
"""

        if claude_client:
            try:
                message = claude_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=3000,
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                analysis = message.content[0].text
            except Exception as e:
                analysis = f"Error: {e}"
        else:
            analysis = "Claude API not configured"

        return {
            "total_files": len(files),
            "breakdown": {
                "python": len(python_files),
                "sql": len(sql_files),
                "markdown": len(md_files),
                "json": len(json_files)
            },
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }

    async def generate_documentation(self, file_path: str) -> str:
        """Generate documentation for a file"""
        if not self.repo:
            return "GitHub not configured"

        try:
            file_content = self.repo.get_contents(file_path)
            code = file_content.decoded_content.decode('utf-8')

            prompt = f"""Generate comprehensive documentation for this file:

File: {file_path}

Code:
```
{code[:5000]}  # Limit to avoid token limits
```

Generate documentation including:
1. Purpose and overview
2. Key functions/classes
3. Dependencies
4. Usage examples
5. Integration points with other components
"""

            if claude_client:
                message = claude_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
            else:
                return "Claude API not configured"

        except Exception as e:
            return f"Error: {e}"

    # ========================================================================
    # DATABASE MONITORING & CASE IMPACT ANALYSIS
    # ========================================================================

    async def monitor_ingestion_tables(self, time_period: str = '24h') -> Dict[str, Any]:
        """Monitor all data ingestion tables for recent activity"""
        if not supabase_client:
            return {"error": "Supabase not configured"}

        # Convert time period to hours
        hours_map = {'1h': 1, '24h': 24, '7d': 168, '30d': 720}
        hours = hours_map.get(time_period, 24)

        since_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        try:
            # Monitor telegram_uploads
            uploads = supabase_client.table('telegram_uploads')\
                .select('*')\
                .gte('created_at', since_time)\
                .execute()

            # Monitor processing_logs
            logs = supabase_client.table('processing_logs')\
                .select('*')\
                .gte('logged_at', since_time)\
                .execute()

            # Monitor storage_registry
            storage = supabase_client.table('storage_registry')\
                .select('*')\
                .gte('created_at', since_time)\
                .execute()

            # Monitor notification_queue
            notifications = supabase_client.table('notification_queue')\
                .select('*')\
                .gte('created_at', since_time)\
                .execute()

            # Analyze the data
            uploads_data = uploads.data if uploads.data else []
            logs_data = logs.data if logs.data else []
            storage_data = storage.data if storage.data else []
            notif_data = notifications.data if notifications.data else []

            # Calculate statistics
            upload_stats = {
                'total': len(uploads_data),
                'completed': len([u for u in uploads_data if u.get('status') == 'completed']),
                'failed': len([u for u in uploads_data if u.get('status') == 'failed']),
                'processing': len([u for u in uploads_data if u.get('status') == 'processing']),
                'by_type': {}
            }

            # Group by document type
            for upload in uploads_data:
                doc_type = upload.get('document_type', 'unknown')
                upload_stats['by_type'][doc_type] = upload_stats['by_type'].get(doc_type, 0) + 1

            # Processing stage analysis
            stage_stats = {}
            for log in logs_data:
                stage = log.get('stage', 'unknown')
                status = log.get('status', 'unknown')
                key = f"{stage}_{status}"
                stage_stats[key] = stage_stats.get(key, 0) + 1

            # Storage analysis
            storage_stats = {
                'total_files': len(storage_data),
                'by_provider': {},
                'total_size_mb': 0
            }

            for storage_item in storage_data:
                provider = storage_item.get('primary_storage_provider', 'unknown')
                storage_stats['by_provider'][provider] = storage_stats['by_provider'].get(provider, 0) + 1
                size = storage_item.get('file_size', 0)
                storage_stats['total_size_mb'] += size / (1024 * 1024)

            # Notification analysis
            notif_stats = {
                'total': len(notif_data),
                'sent': len([n for n in notif_data if n.get('status') == 'sent']),
                'pending': len([n for n in notif_data if n.get('status') == 'pending']),
                'failed': len([n for n in notif_data if n.get('status') == 'failed'])
            }

            return {
                'period': time_period,
                'timestamp': datetime.now().isoformat(),
                'uploads': upload_stats,
                'processing': stage_stats,
                'storage': storage_stats,
                'notifications': notif_stats,
                'health_score': self._calculate_health_score(upload_stats, notif_stats)
            }

        except Exception as e:
            return {"error": str(e)}

    def _calculate_health_score(self, upload_stats: Dict, notif_stats: Dict) -> str:
        """Calculate system health score"""
        total_uploads = upload_stats.get('total', 0)
        if total_uploads == 0:
            return "🟢 HEALTHY - No activity"

        completed = upload_stats.get('completed', 0)
        failed = upload_stats.get('failed', 0)

        success_rate = (completed / total_uploads) * 100 if total_uploads > 0 else 0

        if success_rate >= 95:
            return f"🟢 HEALTHY - {success_rate:.1f}% success rate"
        elif success_rate >= 80:
            return f"🟡 DEGRADED - {success_rate:.1f}% success rate"
        else:
            return f"🔴 CRITICAL - {success_rate:.1f}% success rate"

    async def generate_case_impact_report(self, time_period: str = '24h') -> Dict[str, Any]:
        """Generate report showing how new data impacts the legal case"""
        if not supabase_client or not claude_client:
            return {"error": "Supabase or Claude API not configured"}

        # Get recent uploads
        hours_map = {'1h': 1, '24h': 24, '7d': 168, '30d': 720}
        hours = hours_map.get(time_period, 24)
        since_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        try:
            # Get recent uploads with details
            uploads = supabase_client.table('telegram_uploads')\
                .select('*')\
                .gte('created_at', since_time)\
                .order('created_at', desc=True)\
                .execute()

            if not uploads.data or len(uploads.data) == 0:
                return {
                    'period': time_period,
                    'new_documents': 0,
                    'impact': 'No new documents uploaded in this period'
                }

            # Also get from legal_documents for context
            legal_docs = supabase_client.table('legal_documents')\
                .select('*')\
                .gte('upload_date', since_time)\
                .execute()

            # Prepare document summary for Claude
            doc_summaries = []
            for upload in uploads.data[:20]:  # Limit to recent 20
                doc_summaries.append({
                    'type': upload.get('document_type', 'Unknown'),
                    'title': upload.get('document_title', 'Untitled'),
                    'notes': upload.get('user_notes', ''),
                    'date': upload.get('document_date', upload.get('created_at', '')),
                    'relevancy_score': upload.get('relevancy_score', 0)
                })

            # Use Claude to analyze impact
            prompt = f"""You are analyzing new evidence for legal case D22-03244, a custody case involving Richmond PD and Berkeley PD.

**Case Context:**
- Custody case D22-03244
- Involves police reports, declarations, evidence from Richmond PD and Berkeley PD
- Critical dates: August 4, 2024 (Richmond PD report 24-7889)
- Focus on constitutional violations, police conduct, custody arrangements

**New Documents ({len(doc_summaries)} in last {time_period}):**

{json.dumps(doc_summaries, indent=2)}

**Analysis Required:**

1. **Document Classification**: Categorize each document by type and relevance
2. **Case Impact**: How do these documents strengthen or weaken the case?
3. **Timeline Updates**: Do any documents add critical timeline events?
4. **Evidence Strength**: Rate the evidentiary value (1-10) of each document
5. **Contradictions**: Any documents that contradict existing evidence?
6. **Next Steps**: What actions should be taken based on this new evidence?
7. **Priority Documents**: Which documents require immediate attention?

Provide a comprehensive analysis that helps understand how this new information impacts case strategy and scope."""

            message = claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            analysis = message.content[0].text

            # Calculate aggregate metrics
            avg_relevancy = sum(d['relevancy_score'] for d in doc_summaries) / len(doc_summaries) if doc_summaries else 0
            doc_types_count = {}
            for doc in doc_summaries:
                doc_type = doc['type']
                doc_types_count[doc_type] = doc_types_count.get(doc_type, 0) + 1

            return {
                'period': time_period,
                'timestamp': datetime.now().isoformat(),
                'new_documents_count': len(uploads.data),
                'documents_analyzed': len(doc_summaries),
                'average_relevancy': round(avg_relevancy, 2),
                'document_types': doc_types_count,
                'claude_analysis': analysis,
                'documents': doc_summaries
            }

        except Exception as e:
            return {"error": str(e)}

    async def monitor_schema_changes(self) -> Dict[str, Any]:
        """Monitor database schema for changes"""
        if not supabase_client:
            return {"error": "Supabase not configured"}

        try:
            # Query information schema for table structures
            # Note: This requires service_role permissions
            result = supabase_client.table('information_schema.tables')\
                .select('table_name')\
                .eq('table_schema', 'public')\
                .execute()

            # Expected tables
            expected_tables = [
                'telegram_uploads',
                'processing_logs',
                'storage_registry',
                'notification_queue',
                'user_preferences',
                'legal_documents'
            ]

            actual_tables = [t['table_name'] for t in result.data] if result.data else []

            missing_tables = [t for t in expected_tables if t not in actual_tables]
            unexpected_tables = [t for t in actual_tables if t not in expected_tables and not t.startswith('_')]

            return {
                'timestamp': datetime.now().isoformat(),
                'expected_tables': expected_tables,
                'actual_tables': actual_tables,
                'missing_tables': missing_tables,
                'unexpected_tables': unexpected_tables,
                'schema_health': 'HEALTHY' if len(missing_tables) == 0 else 'DEGRADED'
            }

        except Exception as e:
            return {"error": str(e), "note": "Requires service_role permissions"}

    async def analyze_document_relevance(self, document_id: str) -> Dict[str, Any]:
        """Deep analysis of a specific document's relevance to the case"""
        if not supabase_client or not claude_client:
            return {"error": "Supabase or Claude API not configured"}

        try:
            # Get document details
            upload = supabase_client.table('telegram_uploads')\
                .select('*')\
                .eq('id', document_id)\
                .single()\
                .execute()

            if not upload.data:
                return {"error": "Document not found"}

            doc = upload.data

            # Get processing logs for this document
            logs = supabase_client.table('processing_logs')\
                .select('*')\
                .eq('telegram_upload_id', document_id)\
                .order('logged_at', desc=False)\
                .execute()

            # Analyze with Claude
            prompt = f"""Analyze this document's relevance to legal case D22-03244:

**Document Details:**
- Type: {doc.get('document_type', 'Unknown')}
- Title: {doc.get('document_title', 'Untitled')}
- Date: {doc.get('document_date', 'Unknown')}
- User Notes: {doc.get('user_notes', 'None')}
- Relevancy Score: {doc.get('relevancy_score', 0)}
- File Type: {doc.get('file_type')}
- Size: {doc.get('file_size', 0)} bytes

**Processing History:**
{json.dumps(logs.data if logs.data else [], indent=2)}

**Analysis Required:**

1. **Relevance Assessment**: Why is this document important (or not)?
2. **Case Integration**: How does it fit with existing evidence?
3. **Timeline Placement**: Where does this fit in the case timeline?
4. **Legal Value**: What legal arguments does it support/contradict?
5. **Action Items**: What should be done with this document?
6. **Related Documents**: What other documents should be reviewed alongside this?
7. **Risk Assessment**: Any risks or issues with this document?

Provide detailed analysis."""

            message = claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            return {
                'document_id': document_id,
                'document': doc,
                'processing_history': logs.data if logs.data else [],
                'analysis': message.content[0].text,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}


# ============================================================================
# TELEGRAM INTERFACE
# ============================================================================

async def shepherd_telegram_command(update, context):
    """Handle shepherd commands in Telegram"""
    agent = ClaudeShepherdAgent()

    command = update.message.text

    if command.startswith('/shepherd_review_pr'):
        # Extract PR number
        parts = command.split()
        if len(parts) < 2:
            await update.message.reply_text("Usage: /shepherd_review_pr <number>")
            return

        pr_number = int(parts[1])
        await update.message.reply_text(f"🔍 Reviewing PR #{pr_number}...")

        review = await agent.review_pr(pr_number)

        message = f"""**PR #{review['pr_number']} Review**

**Title:** {review['title']}
**Author:** {review['author']}
**Files Changed:** {review['files_changed']}

**Summary:**
{review['summary']}

**Recommendation:** {review['recommendation']}
"""
        await update.message.reply_text(message, parse_mode='Markdown')

    elif command.startswith('/shepherd_ask'):
        # Extract question
        question = command.replace('/shepherd_ask', '').strip()
        if not question:
            await update.message.reply_text("Usage: /shepherd_ask <your question>")
            return

        await update.message.reply_text("🤔 Consulting repository knowledge...")
        answer = await agent.answer_question(question)
        await update.message.reply_text(answer, parse_mode='Markdown')

    elif command == '/shepherd_analyze':
        await update.message.reply_text("📊 Analyzing repository architecture...")
        analysis = await agent.analyze_architecture()

        message = f"""**Repository Architecture Analysis**

**Total Files:** {analysis['total_files']}

**Breakdown:**
• Python: {analysis['breakdown']['python']}
• SQL: {analysis['breakdown']['sql']}
• Documentation: {analysis['breakdown']['markdown']}
• Config: {analysis['breakdown']['json']}

**Analysis:**
{analysis['analysis'][:1000]}...
"""
        await update.message.reply_text(message, parse_mode='Markdown')

    elif command.startswith('/shepherd_monitor'):
        # Extract time period (default 24h)
        parts = command.split()
        period = parts[1] if len(parts) > 1 else '24h'

        await update.message.reply_text(f"📊 Monitoring ingestion tables for last {period}...")
        report = await agent.monitor_ingestion_tables(period)

        if 'error' in report:
            await update.message.reply_text(f"❌ Error: {report['error']}")
            return

        message = f"""**📊 System Monitoring Report**
**Period:** {report['period']}
**Health:** {report['health_score']}

**📤 Uploads:**
• Total: {report['uploads']['total']}
• Completed: {report['uploads']['completed']}
• Failed: {report['uploads']['failed']}
• Processing: {report['uploads']['processing']}

**💾 Storage:**
• Files Stored: {report['storage']['total_files']}
• Total Size: {report['storage']['total_size_mb']:.2f} MB

**🔔 Notifications:**
• Sent: {report['notifications']['sent']}
• Pending: {report['notifications']['pending']}
• Failed: {report['notifications']['failed']}
"""
        await update.message.reply_text(message, parse_mode='Markdown')

    elif command.startswith('/shepherd_impact'):
        # Extract time period (default 24h)
        parts = command.split()
        period = parts[1] if len(parts) > 1 else '24h'

        await update.message.reply_text(f"📈 Generating case impact report for last {period}...")
        report = await agent.generate_case_impact_report(period)

        if 'error' in report:
            await update.message.reply_text(f"❌ Error: {report['error']}")
            return

        message = f"""**📈 Case Impact Report**
**Period:** {report['period']}

**📄 New Documents:** {report['new_documents_count']}
**⭐ Average Relevancy:** {report['average_relevancy']}

**Document Types:**
"""
        for doc_type, count in report['document_types'].items():
            message += f"• {doc_type}: {count}\n"

        message += f"\n**🤖 AI Analysis:**\n{report['claude_analysis'][:800]}..."

        await update.message.reply_text(message, parse_mode='Markdown')

    elif command.startswith('/shepherd_analyze_doc'):
        # Extract document ID
        parts = command.split()
        if len(parts) < 2:
            await update.message.reply_text("Usage: /shepherd_analyze_doc <document_id>")
            return

        doc_id = parts[1]
        await update.message.reply_text(f"🔍 Analyzing document {doc_id}...")

        analysis = await agent.analyze_document_relevance(doc_id)

        if 'error' in analysis:
            await update.message.reply_text(f"❌ Error: {analysis['error']}")
            return

        doc = analysis['document']
        message = f"""**🔍 Document Analysis**

**Type:** {doc.get('document_type', 'Unknown')}
**Title:** {doc.get('document_title', 'Untitled')}
**Relevancy:** {doc.get('relevancy_score', 0)}

**AI Analysis:**
{analysis['analysis'][:1000]}...
"""
        await update.message.reply_text(message, parse_mode='Markdown')

    elif command == '/shepherd_schema':
        await update.message.reply_text("🗄️ Checking database schema...")
        schema = await agent.monitor_schema_changes()

        if 'error' in schema:
            await update.message.reply_text(f"❌ Error: {schema['error']}")
            return

        message = f"""**🗄️ Database Schema Status**

**Health:** {schema['schema_health']}
**Tables Found:** {len(schema['actual_tables'])}

**Missing Tables:** {len(schema['missing_tables'])}
{', '.join(schema['missing_tables']) if schema['missing_tables'] else 'None'}

**Unexpected Tables:** {len(schema['unexpected_tables'])}
{', '.join(schema['unexpected_tables'][:5]) if schema['unexpected_tables'] else 'None'}
"""
        await update.message.reply_text(message, parse_mode='Markdown')

    elif command == '/shepherd_help':
        help_text = """**🐑 Claude Shepherd Agent Commands**

**Code & Repository:**
• `/shepherd_review_pr <number>` - Review a pull request
• `/shepherd_ask <question>` - Ask about the codebase
• `/shepherd_analyze` - Analyze repository architecture

**Database & Monitoring:**
• `/shepherd_monitor [period]` - Monitor ingestion tables (1h/24h/7d/30d)
• `/shepherd_impact [period]` - Generate case impact report
• `/shepherd_analyze_doc <id>` - Analyze specific document
• `/shepherd_schema` - Check database schema health

**Examples:**
• `/shepherd_ask How does document upload work?`
• `/shepherd_monitor 7d`
• `/shepherd_impact 24h`
• `/shepherd_review_pr 5`
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')


# ============================================================================
# CLI INTERFACE
# ============================================================================

async def main_cli():
    """CLI interface for shepherd agent"""
    print("🐑 Claude Shepherd Agent")
    print("=" * 50)

    agent = ClaudeShepherdAgent()

    while True:
        print("\n" + "=" * 50)
        print("CODE & REPOSITORY:")
        print("1. Index repository")
        print("2. Review PR")
        print("3. Answer question")
        print("4. Analyze architecture")
        print("5. Generate documentation")
        print("\nDATABASE & MONITORING:")
        print("6. Monitor ingestion tables")
        print("7. Generate case impact report")
        print("8. Analyze document relevance")
        print("9. Monitor schema changes")
        print("\n0. Exit")

        choice = input("\nChoice: ")

        if choice == '1':
            indexer = RepositoryIndexer()
            await indexer.index_repository()

        elif choice == '2':
            pr_num = int(input("PR number: "))
            print(f"\n🔍 Reviewing PR #{pr_num}...")
            review = await agent.review_pr(pr_num)
            print(json.dumps(review, indent=2))

        elif choice == '3':
            question = input("Your question: ")
            print(f"\n🤔 Thinking...")
            answer = await agent.answer_question(question)
            print(f"\n{answer}")

        elif choice == '4':
            print("\n📊 Analyzing architecture...")
            analysis = await agent.analyze_architecture()
            print(json.dumps(analysis, indent=2))

        elif choice == '5':
            file_path = input("File path: ")
            print(f"\n📝 Generating documentation...")
            docs = await agent.generate_documentation(file_path)
            print(f"\n{docs}")

        elif choice == '6':
            period = input("Time period (1h/24h/7d/30d) [default: 24h]: ") or '24h'
            print(f"\n📊 Monitoring ingestion tables for last {period}...")
            report = await agent.monitor_ingestion_tables(period)
            print(json.dumps(report, indent=2))

        elif choice == '7':
            period = input("Time period (1h/24h/7d/30d) [default: 24h]: ") or '24h'
            print(f"\n📈 Generating case impact report for last {period}...")
            report = await agent.generate_case_impact_report(period)
            print(json.dumps(report, indent=2))

        elif choice == '8':
            doc_id = input("Document ID (UUID): ")
            print(f"\n🔍 Analyzing document {doc_id}...")
            analysis = await agent.analyze_document_relevance(doc_id)
            print(json.dumps(analysis, indent=2))

        elif choice == '9':
            print("\n🗄️ Monitoring schema changes...")
            schema_report = await agent.monitor_schema_changes()
            print(json.dumps(schema_report, indent=2))

        elif choice == '0':
            print("👋 Goodbye!")
            break


if __name__ == '__main__':
    asyncio.run(main_cli())
