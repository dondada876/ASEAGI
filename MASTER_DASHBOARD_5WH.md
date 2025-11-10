# PROJ344 Master Dashboard - 5W+H Framework

## Overview

The **Master 5W+H Dashboard** is a comprehensive legal intelligence interface that allows you to query and analyze your 601 legal documents using the journalism framework:

- **WHO**: People, parties, attorneys, judges
- **WHAT**: Document types, evidence types
- **WHEN**: Timeline, chronological analysis
- **WHERE**: Jurisdiction, locations, courts
- **WHY**: Purposes, intent, reasons
- **HOW**: Methods, mechanisms, violations

## Key Features

### 1. Multi-Dimensional Analysis
Query your legal documents from ANY perspective:
- See all documents by a specific person
- Find all motions filed in a date range
- Identify fraud patterns across jurisdictions
- Track constitutional violations by method

### 2. Deep Visual Analytics
- Interactive Plotly charts
- Timeline visualizations
- Geographic/jurisdictional mapping
- Score distribution analysis
- Entity relationship mapping

### 3. Custom Query Builder
Combine multiple dimensions:
```
WHO: "Judge Smith"
WHAT: "Motion to Dismiss"
WHEN: January 2024 - March 2024
WHERE: J24 Jurisdiction
WHY: Relevancy ≥ 900 (Smoking Guns)
HOW: Contains perjury indicators
```

### 4. Real-Time Insights
- Automatic entity extraction
- Smart pattern detection
- Cross-reference capabilities
- Export query results to CSV

## How It Works

### The 5W+H Framework

#### 👤 WHO Analysis
**Identifies:**
- All individuals mentioned in documents
- Frequency of mentions
- Documents per person
- Role classification (judge, attorney, parent, etc.)

**Use Cases:**
- "Show me all documents mentioning Judge Anderson"
- "Who are the top 10 most frequently mentioned people?"
- "Find documents where both Parent A and Attorney B are mentioned"

**Visualizations:**
- Bar chart of most mentioned individuals
- Person-to-document relationship network
- Timeline of person involvement

---

#### 📄 WHAT Analysis
**Identifies:**
- Document types (Motions, Orders, Declarations, etc.)
- Evidence categories
- Submission types
- Document classifications

**Use Cases:**
- "Show me all Declarations with relevancy > 900"
- "What types of documents have the most perjury indicators?"
- "Compare Court Orders vs Filed Motions"

**Visualizations:**
- Pie chart of document type distribution
- Bar chart by category
- Score breakdown per document type
- Category comparison matrix

---

#### 📅 WHEN Analysis
**Identifies:**
- Document dates
- Filing dates
- Processing dates
- Timeline sequences

**Use Cases:**
- "Show me all documents from March 2024"
- "What's the timeline of smoking gun evidence?"
- "Find documents filed within 30 days of hearing"

**Visualizations:**
- Timeline scatter plot (date vs relevancy)
- Monthly document volume chart
- Chronological sequence view
- Date range filter with results

---

#### 📍 WHERE Analysis
**Identifies:**
- Jurisdictions (from docket numbers)
- Court locations
- Geographic references
- Multi-jurisdiction cases

**Use Cases:**
- "Show documents by jurisdiction"
- "How many documents per court?"
- "Cross-jurisdictional analysis"

**Visualizations:**
- Jurisdiction distribution bar chart
- Court-level breakdown
- Geographic mapping (if coordinates available)

---

#### ❓ WHY Analysis
**Identifies:**
- Document purposes
- Filing reasons
- Legal arguments
- Intent indicators

**Use Cases:**
- "Why were these motions filed?"
- "What are the stated purposes across all documents?"
- "Find documents with specific legal arguments"

**Visualizations:**
- Purpose treemap
- Intent classification breakdown
- Argument frequency analysis

---

#### ⚙️ HOW Analysis
**Identifies:**
- Methods of fraud
- Perjury techniques
- Constitutional violation mechanisms
- Process workflows

**Use Cases:**
- "How is perjury being committed?"
- "What methods of fraud are most common?"
- "Show violation mechanisms by type"

**Visualizations:**
- Fraud method frequency chart
- Perjury technique breakdown
- Violation mechanism analysis
- Process flow diagrams

---

### 🎯 Custom Query Builder

**Combine ALL dimensions simultaneously:**

Example Query:
```
Find documents where:
  WHO: "Attorney Johnson" OR "Judge Martinez"
  WHAT: Document Type = "Motion" OR "Declaration"
  WHEN: Date Range = Jan 1, 2024 - Mar 31, 2024
  WHERE: Jurisdiction = "J24"
  WHY: Relevancy ≥ 900 (Smoking Gun Evidence)
  HOW: Contains Perjury Indicators = TRUE
```

**Result:** All smoking gun evidence documents that are motions or declarations filed in J24 jurisdiction between Jan-Mar 2024, mentioning specific people, with perjury indicators.

## Installation & Deployment

### Option 1: Add to Existing Ports (Port 8506)

Update `docker-compose.yml`:

```yaml
  # Master 5W+H Dashboard - Port 8506
  master-5wh:
    build: .
    container_name: master-5wh-dashboard
    ports:
      - "8506:8506"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    command: ["streamlit", "run", "dashboards/master_5wh_dashboard.py", "--server.port=8506", "--server.address=0.0.0.0"]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8506/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Deploy:
```bash
ssh root@137.184.1.91
cd /opt/ASEAGI
git pull
docker compose up -d master-5wh
```

Access: http://137.184.1.91:8506

---

### Option 2: Replace Master Dashboard (Port 8501)

If you want this as your PRIMARY dashboard:

```bash
# Backup current master
mv dashboards/proj344_master_dashboard.py dashboards/proj344_master_dashboard_old.py

# Use 5W+H as new master
cp dashboards/master_5wh_dashboard.py dashboards/proj344_master_dashboard.py

# Restart container
docker compose restart proj344-master
```

Access: http://137.184.1.91:8501

---

### Option 3: Local Testing

```bash
cd ~/ASEAGI
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"
streamlit run dashboards/master_5wh_dashboard.py --server.port=8506
```

Access: http://localhost:8506

---

## Usage Examples

### Example 1: Find All Documents About a Specific Person

1. Select **👤 WHO** from sidebar
2. Scroll to "Search for Specific Person"
3. Enter: "Anderson"
4. View all documents mentioning that person
5. See relevancy scores, summaries, document types

### Example 2: Timeline of Smoking Gun Evidence

1. Select **📅 WHEN** from sidebar
2. View timeline scatter plot
3. Look for red dots (high relevancy)
4. Filter date range to specific period
5. Export results

### Example 3: Perjury Pattern Analysis

1. Select **⚙️ HOW** from sidebar
2. View fraud/perjury methods breakdown
3. See top 10 indicators
4. Identify patterns
5. Cross-reference with WHO analysis

### Example 4: Complex Multi-Dimensional Query

1. Select **🎯 Custom Query** from sidebar
2. Enter person name: "Smith"
3. Select document types: "Motion", "Declaration"
4. Set minimum relevancy: 850
5. Check "Perjury Indicators Only"
6. View filtered results
7. Export to CSV

---

## Technical Details

### Data Processing

**Entity Extraction:**
- Regex pattern matching for names
- NLP-based entity recognition
- Automatic categorization
- Smart filtering and deduplication

**Scoring Integration:**
- PROJ344 4-dimensional scores
- Relevancy thresholds
- Dynamic filtering
- Real-time calculations

**Performance:**
- Caching with 5-minute TTL
- Lazy loading for large datasets
- Optimized queries
- Responsive UI

### Database Schema Used

The dashboard queries these fields:
```python
- file_name
- document_type
- category
- purpose
- micro_number
- macro_number
- legal_number
- relevancy_number
- summary
- key_quotes
- fraud_indicators (array)
- perjury_indicators (array)
- contains_false_statements (boolean)
- document_date
- processed_at
- docket_number
- api_cost_usd
```

### Customization

Add new analysis dimensions by editing:
```python
# dashboards/master_5wh_dashboard.py

# Add new framework choice in sidebar
framework_choice = st.sidebar.radio(
    "Analysis Dimension",
    ["🏠 Overview", "👤 WHO", "📄 WHAT", "📅 WHEN",
     "📍 WHERE", "❓ WHY", "⚙️ HOW", "🎯 Custom Query",
     "🆕 YOUR NEW DIMENSION"],  # Add here
    index=0
)

# Add new elif block
elif framework_choice == "🆕 YOUR NEW DIMENSION":
    st.markdown("## 🆕 Your Custom Analysis")
    # Your code here
```

---

## Comparison to Other Dashboards

| Feature | Old Master (8501) | Legal Intel (8502) | CEO (8503) | **5W+H Master (8506)** |
|---------|-------------------|-------------------|------------|------------------------|
| Document List | ✅ | ✅ | ❌ | ✅ |
| Smoking Gun Filter | ✅ | ✅ | ❌ | ✅ |
| Timeline Analysis | ❌ | ⚠️ Basic | ❌ | ✅ **Advanced** |
| Person Search | ❌ | ❌ | ❌ | ✅ |
| Multi-Dimensional Query | ❌ | ❌ | ❌ | ✅ |
| Entity Extraction | ❌ | ❌ | ❌ | ✅ |
| Custom Query Builder | ❌ | ❌ | ❌ | ✅ |
| Export Results | ❌ | ❌ | ❌ | ✅ |
| 5W+H Framework | ❌ | ❌ | ❌ | ✅ |

---

## Best Practices

### For Case Research
1. Start with **🏠 Overview** to understand the data landscape
2. Use **👤 WHO** to identify key players
3. Use **📅 WHEN** to establish timeline
4. Use **🎯 Custom Query** for targeted research

### For Evidence Preparation
1. Use **❓ WHY** to understand document purposes
2. Use **⚙️ HOW** to identify violation patterns
3. Use **🎯 Custom Query** to build evidence packages
4. Export results for attorney review

### For Pattern Detection
1. Use **⚙️ HOW** to find fraud methods
2. Cross-reference with **👤 WHO** for perpetrators
3. Use **📅 WHEN** for temporal patterns
4. Use **📍 WHERE** for jurisdictional patterns

---

## Troubleshooting

### No data showing
- Check Supabase connection
- Verify environment variables
- Check database has documents

### Slow performance
- Reduce date range
- Use specific filters
- Clear browser cache
- Restart container

### Person search not working
- Check spelling
- Try partial names
- Use case-insensitive search
- Check document summaries have data

---

## Future Enhancements

Planned features:
- [ ] AI-powered relationship mapping
- [ ] Predictive case outcome analysis
- [ ] Automatic brief generation
- [ ] Voice query interface
- [ ] Mobile responsive design
- [ ] Real-time collaboration
- [ ] Advanced NLP entity extraction
- [ ] Machine learning pattern detection

---

## Support

For issues or enhancements:
1. Check logs: `docker compose logs master-5wh`
2. Review database connection
3. Test with smaller datasets
4. Check CLAUDE.md for architecture details

---

**Created:** November 10, 2025
**For:** Case J24-00478 - In re Ashe Bucknor
**Purpose:** Comprehensive 5W+H legal intelligence analysis

*"Every question answered. Every pattern revealed. Every child protected."* 🛡️
