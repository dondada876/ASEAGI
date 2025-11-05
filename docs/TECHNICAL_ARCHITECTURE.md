# Technical Architecture

## System Overview

The Athena Guardian Legal Document Scoring System is a multi-tier AI-powered platform that analyzes legal documents, scores credibility, detects violations, and generates evidence packages.

---

## System Hierarchy

### Recommended: 3-TIER SYSTEM

Based on analysis of federal prosecution systems (DOJ, FBI, Sentencing Guidelines) and commercial legal analytics platforms, we recommend simplifying from the initially proposed 5-tier system to a more practical 3-tier architecture:

```
TIER 1: DOCUMENT SCORE (Per Document)
        └─ 4 composite dimensions

TIER 2: COLLECTION SCORE (Per Motion/Brief)
        └─ Aggregated from documents

TIER 3: PARTY CREDIBILITY SCORE (Overall)
        └─ Aggregated from all party actions
```

### Why 3 Tiers (Not 5)?

**Federal systems teach us:**
- Fewer major categories (3-5 max) - not 12+ dimensions per statement
- Weighted hierarchies with clear percentages
- Clear thresholds (90+ = prosecute, 75-89 = strong, <50 = weak)
- Probability-based scoring where applicable
- Historical comparison and percentile rankings

**Eliminated from original design:**
- ❌ Statement-level scoring (too granular for manual use, kept only for AI processing)
- ❌ Page-level scoring (unnecessary intermediary)

**Kept:**
- ✅ Document-level scoring (essential)
- ✅ Motion/brief-level scoring (strategic value)
- ✅ Party-level credibility (case strategy)

---

## Architecture Layers

### Layer 1: Data Ingestion

**Input Sources:**
- PDF documents (court filings, declarations, motions)
- Images (scanned documents)
- Text files (transcripts, emails)
- Structured data (court dockets, databases)

**Processing Pipeline:**
1. **Document Upload**
   - Multi-format support (PDF, DOC, RTF, images)
   - OCR for scanned documents
   - Metadata extraction (date, author, type)

2. **Document Classification**
   - Type detection (motion, declaration, report, etc.)
   - Party identification
   - Case association
   - Timeline placement

3. **Text Extraction & Cleaning**
   - OCR error correction
   - Formatting normalization
   - Statement segmentation
   - Entity recognition (names, dates, places)

### Layer 2: AI Analysis Engine

**Core AI Components:**

1. **Statement Extraction Module**
   ```python
   def extract_statements(document):
       """
       Extract individual claims, assertions, and statements
       Returns: List[Statement]
       """
       # AI identifies:
       # - Factual claims
       # - Admissions
       # - Denials
       # - Opinions vs facts
       pass
   ```

2. **Truth Analysis Module**
   ```python
   def analyze_truth(statement, case_context):
       """
       Score truth/falsity of statement
       Returns: TruthScore (0-1000)
       """
       # Analyzes against:
       # - Historical statements
       # - Contradictory evidence
       # - Corroborating evidence
       # - Timeline consistency
       pass
   ```

3. **Context Relationship Module**
   ```python
   def calculate_context(statement, timeline, events):
       """
       Calculate temporal and relational significance
       Returns: ContextScore (0-1000)
       """
       # Measures:
       # - Time proximity to key events
       # - Relationship to other statements
       # - Pattern significance
       # - Legal consequences
       pass
   ```

4. **Bad Faith Detection Module**
   ```python
   def quantify_bad_faith(statement, party_history, timing):
       """
       Quantify bad faith indicators
       Returns: BadFaithScore (0-1000)
       """
       # Detects:
       # - Timing manipulation
       # - Forum shopping
       # - Evidence concealment
       # - Child endangerment
       # - Procedural abuse
       pass
   ```

5. **Violation Detection Module**
   ```python
   def detect_violations(statement, intent, materiality):
       """
       Identify legal violations
       Returns: List[Violation]
       """
       # Identifies:
       # - Perjury (PC 118)
       # - Fraud on court (CCP 473)
       # - Child endangerment (PC 273a)
       # - Obstruction (PC 182)
       pass
   ```

### Layer 3: Scoring Engine

**TIER 1: Document Master Score (DMS)**

```
DMS = weighted_average([
    Evidence_Strength * 0.35,
    Legal_Impact * 0.35,
    Strategic_Value * 0.20,
    Intent_Conduct * 0.10
])
```

**Components:**

1. **Evidence Strength (ES): 0-1000 [Weight: 35%]**
   - Truth/Reliability (TRU): 0-1000
   - Verification Status (VER): 0-1000
   - Source Credibility (SRC): 0-1000
   - Authenticity (AUT): 0-1000
   - Evidence Type Quality (EVQ): 0-1000

2. **Legal Impact (LI): 0-1000 [Weight: 35%]**
   - Proves Statutory Element (LGW): 0-1000
   - Admissibility (ADM): 0-1000
   - Legal Standard Met: 0-1000
   - Precedent Value: 0-1000

3. **Strategic Value (SV): 0-1000 [Weight: 20%]**
   - Case Impact (IMP): 0-1000
   - Opposition Impact: 0-1000
   - Timeline Significance: 0-1000
   - Evidence Gap Filled: 0-1000

4. **Intent & Conduct (IC): 0-1000 [Weight: 10%]**
   - Intent Classification: 0-1000
   - Culpability Level: 0-1000
   - Bad Faith Score: 0-1000

**TIER 2: Collection Master Score (CMS)**

Aggregates document scores for entire motion/brief:

```python
def calculate_cms(documents):
    """
    Collection Master Score for motion/brief
    """
    doc_scores = [doc.dms for doc in documents]

    cms = {
        'avg_document_score': mean(doc_scores),
        'max_document_score': max(doc_scores),
        'min_document_score': min(doc_scores),
        'document_count': len(documents),
        'smoking_gun_count': count(doc_scores > 900),
        'weak_evidence_count': count(doc_scores < 500),
        'overall_cms': weighted_average(doc_scores)
    }

    return cms
```

**TIER 3: Party Justice Score (PJS)**

The "Legal Credit Score" for party credibility:

```python
def calculate_pjs(party_id, case_history):
    """
    Party Justice Score: Overall credibility
    """
    pjs = {
        'truthfulness_rate': calculate_truth_rate(party_id),
        'lie_density': calculate_lie_density(party_id),
        'perjury_count': count_perjuries(party_id),
        'violation_severity_avg': avg_violation_severity(party_id),
        'bad_faith_average': avg_bad_faith(party_id),
        'risk_scores': {
            'flight_risk': calculate_flight_risk(party_id),
            'compliance_risk': calculate_compliance_risk(party_id),
            'harm_risk': calculate_harm_risk(party_id)
        },
        'overall_pjs': composite_score(party_id)
    }

    return pjs
```

### Layer 4: Data Storage

**Primary Database: PostgreSQL**

Key tables:
- `documents` - All document metadata and master scores
- `statements` - Individual statements extracted (AI processing only)
- `violations` - Detected legal violations
- `parties` - Party information and credibility scores
- `cases` - Case metadata and associations
- `context_relationships` - Temporal and relational connections
- `evidence_packages` - Generated motion exhibits

**See [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) for complete schema.**

### Layer 5: API & Integration

**RESTful API Endpoints:**

```
POST   /api/v1/documents/upload          - Upload document
GET    /api/v1/documents/{id}/analyze    - Get analysis
POST   /api/v1/cases                     - Create case
GET    /api/v1/cases/{id}/credibility    - Party credibility
GET    /api/v1/violations/perjury        - Perjury evidence
POST   /api/v1/packages/generate         - Generate motion package
```

**See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference.**

---

## AI Processing Workflow

### End-to-End Document Processing

```python
def process_document(doc_path, case_context):
    """
    Complete AI-powered document analysis pipeline
    """

    # STEP 1: Extract and parse
    pages = extract_pages(doc_path)
    document_metadata = extract_metadata(doc_path)

    # STEP 2: Document classification
    doc_type = classify_document(pages)
    speaker = identify_speaker(pages, doc_type)
    date = get_document_date(doc_path, document_metadata)
    under_oath = is_under_oath(doc_path, doc_type)

    # STEP 3: Statement extraction (for AI analysis)
    statements = []
    for page_num, page_content in enumerate(pages):
        page_statements = ai_extract_statements(
            page_content,
            context={
                'doc_type': doc_type,
                'speaker': speaker,
                'date': date,
                'under_oath': under_oath,
                'case_context': case_context
            }
        )
        statements.extend(page_statements)

    # STEP 4: Analyze each statement (AI internal processing)
    analyzed_statements = []
    for statement in statements:

        # Truth analysis
        truth_analysis = ai_analyze_truth(
            statement=statement,
            case_history=case_context['historical_statements'],
            contradictory_evidence=case_context['evidence_against'],
            corroborating_evidence=case_context['evidence_for']
        )

        # Context relationship
        context_score = ai_calculate_context_relationships(
            statement=statement,
            document_date=date,
            related_events=case_context['timeline'],
            key_documents=case_context['key_docs']
        )

        # Bad faith quantification
        bad_faith = ai_quantify_bad_faith(
            statement=statement,
            timing_context=context_score['timing'],
            pattern_history=case_context['party_pattern'],
            violations_detected=truth_analysis['violations']
        )

        # Intent classification
        intent = ai_classify_intent(
            statement=statement,
            truth_value=truth_analysis['truth_score'],
            context=context_score,
            party_history=case_context['party_credibility']
        )

        # Violation detection
        violations = ai_detect_violations(
            statement=statement,
            truth_value=truth_analysis['truth_score'],
            intent=intent['intent_score'],
            materiality=assess_materiality(statement, case_context),
            under_oath=statement['under_oath']
        )

        analyzed_statements.append({
            'statement': statement,
            'truth': truth_analysis,
            'context': context_score,
            'bad_faith': bad_faith,
            'intent': intent,
            'violations': violations
        })

    # STEP 5: Aggregate to document-level scores
    document_scores = calculate_document_master_score(
        analyzed_statements,
        document_metadata,
        case_context
    )

    # STEP 6: Store results
    store_document_analysis(
        doc_id=generate_doc_id(),
        metadata=document_metadata,
        scores=document_scores,
        statements=analyzed_statements,  # For evidence trail
        case_id=case_context['case_id']
    )

    # STEP 7: Update party credibility
    update_party_justice_score(
        party_id=speaker,
        new_document=document_scores
    )

    return {
        'document_scores': document_scores,
        'violations': extract_violations(analyzed_statements),
        'smoking_guns': identify_smoking_guns(analyzed_statements),
        'impeachment_evidence': identify_impeachment(analyzed_statements)
    }
```

---

## Technology Stack

### Backend
- **Language:** Python 3.11+
- **Web Framework:** FastAPI
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy
- **Task Queue:** Celery + Redis
- **Cache:** Redis

### AI/ML
- **LLM API:** OpenAI GPT-4 / Anthropic Claude
- **OCR:** Tesseract / Google Cloud Vision
- **NLP:** spaCy, NLTK
- **Document Processing:** PyPDF2, python-docx

### Frontend
- **Framework:** React + TypeScript
- **State Management:** Redux Toolkit
- **UI Components:** Material-UI
- **Charts:** Recharts / D3.js
- **PDF Viewer:** react-pdf

### Infrastructure
- **Cloud:** AWS / Google Cloud Platform
- **Container:** Docker
- **Orchestration:** Kubernetes (production) / Docker Compose (dev)
- **CI/CD:** GitHub Actions
- **Monitoring:** Grafana + Prometheus

---

## Deployment Architecture

### Development Environment
```
Docker Compose:
- PostgreSQL container
- Redis container
- FastAPI backend container
- React frontend container
- Celery worker container
```

### Production Environment
```
Kubernetes Cluster:
- Application pods (auto-scaling)
- Database (managed service: AWS RDS)
- Redis (managed service: AWS ElastiCache)
- Load balancer (AWS ALB)
- CDN (CloudFront)
- Object storage (S3 for documents)
```

---

## Security Considerations

### Data Protection
- **Encryption at rest:** AES-256 for database and document storage
- **Encryption in transit:** TLS 1.3 for all API communications
- **Authentication:** JWT tokens with refresh mechanism
- **Authorization:** Role-based access control (RBAC)

### Privacy
- **HIPAA Compliance:** For medical records (forensic exams)
- **COPPA Compliance:** For child-related information
- **Data Retention:** Configurable retention policies
- **Anonymization:** Option to anonymize case data for research

### Audit Trail
- All document access logged
- All scoring decisions logged with AI confidence
- All exports tracked
- User actions audited

---

## Scalability Considerations

### Horizontal Scaling
- Stateless application servers
- Distributed task processing with Celery
- Database read replicas
- CDN for static assets

### Performance Optimization
- Document processing queue (async)
- Result caching (Redis)
- Database indexing strategy
- Lazy loading for large datasets

### Cost Optimization
- LLM API call batching
- Caching of common analyses
- Document de-duplication
- Tiered storage (hot/warm/cold)

---

## Monitoring & Observability

### Key Metrics
- **Application Performance:**
  - API response times
  - Document processing time
  - LLM API latency
  - Error rates

- **Business Metrics:**
  - Documents processed per day
  - Perjury instances detected
  - Cases analyzed
  - User engagement

- **AI Quality:**
  - Truth detection accuracy
  - False positive rate
  - Human review agreement rate
  - Confidence score distribution

### Alerting
- API downtime
- Database connection issues
- LLM API failures
- Processing queue backlog
- Error rate spikes

---

## Next Steps

1. **Phase 1:** MVP Development (3 months)
   - Core document processing
   - Basic scoring engine
   - Database setup
   - Simple web interface

2. **Phase 2:** AI Enhancement (3 months)
   - Advanced truth detection
   - Context analysis
   - Bad faith quantification
   - Violation detection

3. **Phase 3:** Production Deployment (2 months)
   - Security hardening
   - Performance optimization
   - User testing
   - Documentation

4. **Phase 4:** Scale & Iterate (Ongoing)
   - User feedback integration
   - Model improvements
   - Feature additions
   - Partnership development

---

**Last Updated:** 2025-11-05
**Version:** 1.0.0
