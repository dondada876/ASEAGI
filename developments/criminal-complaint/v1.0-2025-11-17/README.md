# Criminal Complaint Evidence Analysis System

**Version:** 1.0
**Date:** 2025-11-17
**Status:** Testing
**Port:** 8506 (dashboard)

## Description

Complete system to query all 601+ documents against perjury claims in the criminal complaint. Maps evidence to 5 specific false statements made under oath.

## Files

- `schema.py` - Defines 5 false statements with scoring algorithms
- `analyzer.py` - Analysis engine with master report generator
- `dashboard.py` - Real-time visual analysis
- `GUIDE.md` - Complete user documentation (50+ pages)
- `VERSION.txt` - Version number (1.0)
- `CHANGELOG.md` - Version history

## Usage

### Command-Line Analysis

```bash
# Set environment variables
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your_key"

# Run analysis of all claims
python3 developments/criminal-complaint/current/analyzer.py

# Analyze specific claim
python3 developments/criminal-complaint/current/analyzer.py --claim FS-001-JAMAICA-FLIGHT

# Generate master report
python3 developments/criminal-complaint/current/analyzer.py --export-report MASTER_PERJURY_REPORT.md
```

### Dashboard

```bash
streamlit run developments/criminal-complaint/current/dashboard.py --server.port 8506

# Access at: http://localhost:8506
```

## Features

- ✅ Cross-reference 601+ documents with 5 false statements
- ✅ Keyword matching with configurable search terms
- ✅ Date relevance scoring (0-100)
- ✅ Document type matching (TEXT, TRANSCRIPT, etc.)
- ✅ Contradiction scoring (0-999 scale)
- ✅ Prosecutability assessment (0-100)
- ✅ Master report generation (markdown)
- ✅ JSON export for automation
- ✅ Real-time dashboard visualization

## False Statements Tracked

1. **FS-001-JAMAICA-FLIGHT** - "Will abscond to Jamaica" (ZERO evidence in 201+ texts)
2. **FS-002-RETURN-AGREEMENT** - "Agreed to return child on 8/9" (contradicted by Good Cause Report text)
3. **FS-003-HISTORY-VIOLATIONS** - "History of ignoring orders" (first lawful retention)
4. **FS-004-CONCEALED-INVESTIGATION** - Failed to disclose grandfather investigation
5. **FS-005-MOTHER-ASHES-CLAIM** - False travel motive (transcript shows uncle's funeral)

## Testing

- ✅ Tested with 601 documents from Supabase
- ✅ All 5 claims analyzed successfully
- ✅ Dashboard functional on port 8506
- ✅ Master report generates correctly
- ✅ JSON export verified

## Dependencies

Requires from main project:
- Supabase client
- Streamlit (for dashboard)
- Plotly (for visualizations)
- Pandas (for data handling)

## Performance

- Analysis of 601 documents: ~5 seconds
- Dashboard load time: <2 seconds
- Master report generation: ~3 seconds
- Memory usage: ~150 MB

## Next Steps

1. Run full analysis on production data
2. Review master report with legal team
3. Prepare for DA submission
4. Consider promotion to production if stable

## Related

- **Case:** D22-03244 (Family Court)
- **Subject:** Mariyam Yonas Rufael
- **Complainant:** Don Bucknor
- **Penal Codes:** PC-118.1, PC-135, PC-148
- **Guide:** See GUIDE.md for 50+ page complete documentation
