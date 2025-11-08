# Emergency Legal Form Filler Guide
**Created:** 2025-11-07
**System:** ASEAGI Legal Intelligence Platform
**Purpose:** Automated generation of JV-180 and JV-575 court forms

---

## 📋 Overview

The Emergency Legal Form Filler automatically generates professional court forms by:
1. **Querying Supabase** for high-scoring case evidence (score ≥ 900)
2. **Using Claude API** to generate compelling legal arguments
3. **Creating PDF documents** in proper court format

### Forms Generated:
- **JV-180:** Petition to Change Court Order (W&I § 388)
- **JV-575:** Declaration in Support of Petition
- **Evidence Summary:** Organized exhibit list

---

## 🗂️ File Structure

```
ASEAGI/
├── core/
│   └── form_generation/
│       ├── __init__.py                    # Package init
│       ├── emergency_form_filler.py       # Main class (600+ lines)
│       └── run_form_filler.py             # CLI wrapper (150+ lines)
├── notes/
│   └── 25-11-07-Emergency_Form_Filler_Guide.md  # This guide
├── config.toml                            # API credentials
└── requirements.txt                       # Dependencies
```

---

## ⚙️ Installation

### 1. Install Dependencies

```bash
cd /home/user/ASEAGI
pip install anthropic>=0.18.0 reportlab>=4.0.0 toml>=0.10.0
```

Or add to `requirements.txt`:
```
anthropic>=0.18.0
reportlab>=4.0.0
toml>=0.10.0
```

Then run:
```bash
pip install -r requirements.txt
```

### 2. Configure API Credentials

Create or update `config.toml` in repo root:

```toml
[apis]
supabase_url = "https://jvjlhxodmbkodzmggwpu.supabase.co"
supabase_key = "your-service-role-key-here"
anthropic_api_key = "your-anthropic-api-key-here"
```

**Important:**
- Use **service_role** key for Supabase (full database access)
- Get Anthropic key at: https://console.anthropic.com/

### 3. Verify Setup

```bash
python core/form_generation/run_form_filler.py --help
```

Should display usage information.

---

## 🚀 Usage

### Basic Command

```bash
python core/form_generation/run_form_filler.py \
  --case-id J24-00478 \
  --output ./filing_package
```

### Advanced Options

```bash
python core/form_generation/run_form_filler.py \
  --case-id J24-00478 \
  --output ./filing_package \
  --config /path/to/custom/config.toml \
  --verbose
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--case-id` | ✅ Yes | Case identifier (e.g., J24-00478) |
| `--output` | ✅ Yes | Output directory for PDFs |
| `--config` | ⬜ No | Path to config.toml (default: repo root) |
| `--verbose` | ⬜ No | Show detailed error messages |

---

## 📊 How It Works

### Step 1: Gather Evidence

Queries Supabase `legal_documents` table for:

1. **Critical Documents** (relevancy_number ≥ 900)
2. **Mother's Admissions** (summary ILIKE '%mother%admit%')
3. **Medical/Forensic Records** (document_type IN 'Medical Record', 'Forensic Report', 'CPS Report')
4. **Police Reports** (filename ILIKE '%police%')
5. **Dismissal Records** (summary ILIKE '%dismissal%')
6. **Timeline** (all documents ordered by date)

### Step 2: Generate Legal Arguments

Uses **Claude Sonnet 4** to generate:

1. **Changed Circumstances** (300-500 words)
   - What new evidence emerged
   - Why it wasn't available before
   - How circumstances materially changed

2. **Best Interest of Child** (300-400 words)
   - Focus on child safety (not parental rights)
   - Why investigation is necessary
   - Potential harm if petition denied

3. **Orders Requested** (numbered list)
   - Accept ex parte petition
   - Set hearing date
   - Order CPS report
   - Appoint investigator
   - Any protective orders needed

4. **JV-575 Declaration** (2000-3000 words)
   - 12 comprehensive sections
   - Introduction through Conclusion
   - Professional legal tone
   - Cites specific evidence

### Step 3: Create PDFs

Generates two PDF files:

1. **{case_id}_JV180_JV575.pdf**
   - Professional court format
   - Times New Roman, 10pt
   - 0.75" margins
   - Proper headings and spacing
   - Signature blocks

2. **{case_id}_Evidence_Summary.pdf**
   - Organized by exhibit (A-E)
   - Top 10 documents per category
   - Filenames, scores, summaries

---

## 📄 Output Files

### Example Output

After running:
```bash
python core/form_generation/run_form_filler.py \
  --case-id J24-00478 \
  --output ./filing_package
```

You'll get:
```
filing_package/
├── J24-00478_JV180_JV575.pdf           # Main petition (8-12 pages)
└── J24-00478_Evidence_Summary.pdf      # Exhibit list (3-5 pages)
```

### JV180_JV575.pdf Contents

**Pages 1-2: JV-180 Petition**
- Court header
- Case number
- Changed Circumstances section
- Best Interest section
- Orders Requested
- Date and signature block

**Pages 3+: JV-575 Declaration**
- Title and case info
- 12 detailed sections:
  1. Introduction
  2. Child's Disclosure
  3. Forensic Examination
  4. Mother's Admission
  5. Systemic Failure
  6. False Allegations
  7. Dismissal Records
  8. New Evidence
  9. Pattern Analysis
  10. Urgency
  11. Best Interest
  12. Conclusion
- Declaration under penalty of perjury
- Signature block

### Evidence_Summary.pdf Contents

**Exhibit A:** Critical Documents (score ≥ 900)
**Exhibit B:** Mother's Admissions
**Exhibit C:** Medical/Forensic Records
**Exhibit D:** Police Reports
**Exhibit E:** Dismissal Records

Each exhibit lists:
- Document filename
- Relevancy score
- Executive summary (truncated)

---

## 🔍 Class Reference

### EmergencyFormFiller

Main class in `emergency_form_filler.py`

#### Constructor

```python
from core.form_generation import EmergencyFormFiller

filler = EmergencyFormFiller(
    supabase_url="https://jvjlhxodmbkodzmggwpu.supabase.co",
    supabase_key="your-service-role-key",
    anthropic_key="your-anthropic-key"
)
```

#### Methods

##### `gather_evidence(case_id: str) -> dict`

Queries Supabase for case evidence.

**Returns:**
```python
{
    'critical_docs': [...],       # Score ≥ 900
    'mother_admissions': [...],   # Admissions
    'medical_forensic': [...],    # Medical/forensic
    'dismissals': [...],          # Dismissal records
    'police_reports': [...],      # Police reports
    'timeline': [...],            # Dated events
    'high_scoring': [...]         # Score ≥ 850
}
```

##### `generate_changed_circumstances() -> str`

Uses Claude API to generate "Changed Circumstances" section.

**Returns:** 300-500 word legal argument

##### `generate_best_interest() -> str`

Uses Claude API to generate "Best Interest of Child" section.

**Returns:** 300-400 word legal argument

##### `generate_orders_requested() -> str`

Uses Claude API to generate numbered list of requested orders.

**Returns:** Numbered list (4-8 items)

##### `generate_jv575_declaration() -> str`

Uses Claude API to generate comprehensive declaration.

**Returns:** 2000-3000 word declaration with 12 sections

##### `create_pdf(form_data: dict, output_path: str)`

Creates professional PDF with proper court formatting.

**Args:**
- `form_data`: Dict with sections (changed_circumstances, best_interest, etc.)
- `output_path`: Path to save PDF

##### `create_evidence_summary(output_path: str)`

Creates exhibit list PDF.

**Args:**
- `output_path`: Path to save exhibits PDF

##### `run(case_id: str, output_dir: str)`

Main orchestration method - generates complete filing package.

**Args:**
- `case_id`: Case identifier (e.g., J24-00478)
- `output_dir`: Directory to save output files

---

## 💡 Usage Examples

### Example 1: Basic Usage

```bash
python core/form_generation/run_form_filler.py \
  --case-id J24-00478 \
  --output ./filing_package
```

**Output:**
```
🏛️  EMERGENCY LEGAL FORM FILLER
📋 Case ID: J24-00478
📁 Output: ./filing_package

📊 Gathering evidence for case J24-00478...
  🔥 Querying critical documents (score >= 900)...
     Found 23 critical documents
  🎯 Searching for mother's admissions...
     Found 5 documents with admissions
  🏥 Querying medical and forensic records...
     Found 32 medical/forensic records
  ⚖️ Searching for dismissal documents...
     Found 8 dismissal-related documents
  🚔 Querying police reports...
     Found 47 police reports
  📅 Building timeline...
     Timeline includes 145 dated events

✅ Evidence gathered: 260 documents across 7 categories

📝 Generating Changed Circumstances section...
✅ Generated 387 words

📝 Generating Best Interest section...
✅ Generated 342 words

📝 Generating Orders Requested section...
✅ Generated orders list

📝 Generating JV-575 Declaration (this may take a moment)...
✅ Generated 2,456 words

📄 Creating PDF: ./filing_package/J24-00478_JV180_JV575.pdf
✅ PDF created successfully
   Size: 156,234 bytes (152.6 KB)

📋 Creating evidence summary: ./filing_package/J24-00478_Evidence_Summary.pdf
✅ Evidence summary created

✅ FILING PACKAGE COMPLETE

📄 Forms Generated:
   • ./filing_package/J24-00478_JV180_JV575.pdf
   • ./filing_package/J24-00478_Evidence_Summary.pdf

📊 Evidence Summary:
   • critical_docs: 23 documents
   • mother_admissions: 5 documents
   • medical_forensic: 32 documents
   • dismissals: 8 documents
   • police_reports: 47 documents
   • timeline: 145 documents
   • high_scoring: 87 documents

🎯 Next Steps:
   1. Review generated forms for accuracy
   2. Add personal information (name, address, signature)
   3. Attach exhibits referenced in declaration
   4. File with court clerk
   5. Serve on all parties
```

### Example 2: Programmatic Usage

```python
from core.form_generation import EmergencyFormFiller
import toml

# Load config
config = toml.load('config.toml')
apis = config['apis']

# Initialize
filler = EmergencyFormFiller(
    supabase_url=apis['supabase_url'],
    supabase_key=apis['supabase_key'],
    anthropic_key=apis['anthropic_api_key']
)

# Generate forms
filler.run(
    case_id='J24-00478',
    output_dir='./filing_package'
)
```

### Example 3: Custom Evidence Query

```python
from core.form_generation import EmergencyFormFiller
import toml

config = toml.load('config.toml')
apis = config['apis']

filler = EmergencyFormFiller(
    supabase_url=apis['supabase_url'],
    supabase_key=apis['supabase_key'],
    anthropic_key=apis['anthropic_api_key']
)

# Just gather evidence
evidence = filler.gather_evidence('J24-00478')

# Inspect critical documents
for doc in evidence['critical_docs']:
    print(f"{doc['original_filename']}: {doc['relevancy_number']}")
    print(f"  {doc['executive_summary'][:100]}...")
```

---

## ⚠️ Important Notes

### Legal Considerations

1. **Review All Output**
   - AI-generated content should be reviewed by attorney
   - Verify all facts and citations
   - Ensure compliance with local court rules

2. **Complete Personal Information**
   - Add declarant's name and address
   - Sign where indicated
   - Add contact information

3. **Attach Exhibits**
   - Reference actual documents in exhibits
   - Organize per exhibit list
   - Number pages properly

4. **Filing Requirements**
   - Check local court rules for formatting
   - May need to adjust margins/fonts
   - Verify signature requirements

### Technical Considerations

1. **API Costs**
   - Each run uses Claude API (~$0.50-1.00 per form)
   - Monitor Anthropic usage dashboard
   - Budget accordingly for multiple cases

2. **Database Access**
   - Requires service_role key for full access
   - Keep credentials secure
   - Don't commit config.toml to git

3. **Evidence Quality**
   - Output quality depends on database content
   - Ensure documents have good summaries
   - Higher scoring docs get more weight

4. **Processing Time**
   - Full generation takes 2-5 minutes
   - Most time is Claude API calls
   - Be patient during declaration generation

---

## 🛠️ Troubleshooting

### Error: "Missing supabase_key in config.toml"

**Solution:** Add service_role key to config.toml:
```toml
[apis]
supabase_key = "eyJhbG...YOUR_SERVICE_ROLE_KEY"
```

Get key from: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/settings/api

---

### Error: "Missing anthropic_api_key in config.toml"

**Solution:** Add Anthropic API key to config.toml:
```toml
[apis]
anthropic_api_key = "sk-ant-...YOUR_API_KEY"
```

Get key from: https://console.anthropic.com/

---

### Error: "Access denied" from Supabase

**Problem:** Row Level Security blocking access

**Solution:** Use service_role key (not anon key) in config.toml

---

### Error: "No critical documents found"

**Problem:** Database doesn't have documents with score ≥ 900

**Solution:**
1. Check if documents are in database: `python utilities/db_query.py --summary`
2. Lower threshold in code (edit `emergency_form_filler.py` line with `.gte('relevancy_number', 900)`)
3. Ensure documents have been scored

---

### Error: "ModuleNotFoundError: No module named 'anthropic'"

**Solution:** Install dependencies:
```bash
pip install anthropic reportlab toml
```

---

### PDF formatting issues

**Problem:** Text overlapping, margins wrong, fonts odd

**Solution:**
1. Check ReportLab version: `pip show reportlab`
2. Update if < 4.0: `pip install --upgrade reportlab`
3. Verify PDF viewer (try different viewer if rendering looks wrong)

---

## 📈 Future Enhancements

### Planned Features

1. **Multiple Case Support**
   - Batch processing for multiple cases
   - Template customization per case type

2. **Evidence Filtering**
   - Custom date ranges
   - Specific document types
   - Keyword filtering

3. **Form Templates**
   - Additional form types (JV-180, etc.)
   - Customizable templates
   - Court-specific formatting

4. **Export Formats**
   - DOCX output (editable)
   - HTML preview
   - Exhibit organization

5. **Interactive Mode**
   - Web interface for form generation
   - Real-time preview
   - Evidence selection UI

---

## 📞 Support

### Documentation
- This guide: `notes/25-11-07-Emergency_Form_Filler_Guide.md`
- Database query guide: `DATABASE_QUERY_GUIDE.md`
- Supabase RLS fix: `SUPABASE_RLS_FIX_GUIDE.md`

### Getting Help

1. Check error messages (use `--verbose` flag)
2. Review this guide's troubleshooting section
3. Verify config.toml has correct API keys
4. Test database access: `python utilities/db_query.py --summary`

---

## 📊 System Requirements

### Software
- Python 3.8+
- pip package manager
- Supabase account with populated database
- Anthropic API account

### Dependencies
- `anthropic>=0.18.0` - Claude API client
- `reportlab>=4.0.0` - PDF generation
- `toml>=0.10.0` - Config file parsing
- `supabase>=2.0.0` - Database client (from existing requirements)

### Database
- Supabase project with `legal_documents` table
- Documents with scoring and summaries
- Service role key for access

### API Access
- Anthropic API key with credits
- Sufficient quota for multiple API calls

---

## 🎯 Quick Start Checklist

- [ ] Install dependencies: `pip install anthropic reportlab toml`
- [ ] Create `config.toml` with API keys
- [ ] Get Supabase service_role key
- [ ] Get Anthropic API key
- [ ] Verify database access: `python utilities/db_query.py --summary`
- [ ] Run form filler: `python core/form_generation/run_form_filler.py --case-id J24-00478 --output ./test`
- [ ] Review generated PDFs
- [ ] Customize as needed

---

**Last Updated:** 2025-11-07
**Version:** 1.0
**Status:** Production Ready
