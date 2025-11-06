#!/usr/bin/env python3
"""
PROJ344 Schema Analysis Utility
Comprehensive database schema analysis with 5W+H framework:
- Why: Purpose and business logic
- When: Temporal aspects and update frequency
- Where: Storage location and relationships
- Who: Data owners and stakeholders
- How: Access patterns and usage

Generates relevancy, requirements, and importance analysis.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import json

try:
    from supabase import create_client
except ImportError:
    print("❌ Install supabase: pip install supabase")
    sys.exit(1)

# ============================================================================
# CREDENTIAL HANDLING
# ============================================================================

def get_credentials():
    """Get Supabase credentials from multiple sources"""
    url = None
    key = None

    # Try environment variables
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')

    if url and key:
        return url, key

    # Try Streamlit secrets
    try:
        import streamlit as st
        url = st.secrets.get('SUPABASE_URL')
        key = st.secrets.get('SUPABASE_KEY')
        if url and key:
            return url, key
    except:
        pass

    # Try .streamlit/secrets.toml
    try:
        import toml
        secrets_path = Path(__file__).parent.parent / '.streamlit' / 'secrets.toml'
        if secrets_path.exists():
            secrets = toml.load(secrets_path)
            url = secrets.get('SUPABASE_URL')
            key = secrets.get('SUPABASE_KEY')
            if url and key:
                return url, key
    except:
        pass

    # Default URL
    url = 'https://jvjlhxodmbkodzmggwpu.supabase.co'

    return url, key

# ============================================================================
# TABLE METADATA DEFINITIONS (5W+H Framework)
# ============================================================================

TABLE_METADATA = {
    'legal_documents': {
        'why': 'Store and track all legal documents with AI-powered scoring and analysis',
        'when': 'Created when documents uploaded; Updated during AI processing',
        'where': 'Central document repository; Links to document_pages and file_metadata',
        'who': 'Document owners: Don Bucknor; Accessed by: Legal team, AI processors',
        'how': 'Queried by dashboards for document intelligence; Updated by AI scanners',
        'relevancy': 'CRITICAL',
        'importance': 10,
        'usage_frequency': 'Very High - Core table for all dashboards',
        'requirements': 'Must have: original_filename, relevancy_number, processing_status; Optional: executive_summary, keywords',
    },

    'document_pages': {
        'why': 'Store individual page images and OCR text for document viewing',
        'when': 'Created during document processing; Rarely updated after creation',
        'where': 'Child of legal_documents; Links to Supabase Storage for images',
        'who': 'Data owner: Processing pipeline; Accessed by: Document viewers',
        'how': 'Queried when users view document pages in dashboards',
        'relevancy': 'HIGH',
        'importance': 8,
        'usage_frequency': 'Medium - Used for detailed document viewing',
        'requirements': 'Must have: document_id, page_number; Should have: image_url or image_path, ocr_text',
    },

    'court_events': {
        'why': 'Track all court hearings, filings, and proceedings for timeline analysis',
        'when': 'Created when court events scheduled; Updated with outcomes',
        'where': 'Standalone table with document references; Used in timeline dashboards',
        'who': 'Data owner: Legal team; Accessed by: All stakeholders',
        'how': 'Queried for timeline visualizations and event tracking',
        'relevancy': 'CRITICAL',
        'importance': 10,
        'usage_frequency': 'High - Core for timeline analysis',
        'requirements': 'Must have: event_date, event_type, court_name, case_number',
    },

    'legal_violations': {
        'why': 'Document due process violations and constitutional issues',
        'when': 'Created when violations identified; Updated with evidence',
        'where': 'Standalone table; Referenced by violation tracking dashboards',
        'who': 'Data owner: Legal analysis team; Accessed by: Attorneys, judges',
        'how': 'Queried for violation reports and constitutional arguments',
        'relevancy': 'CRITICAL',
        'importance': 10,
        'usage_frequency': 'Medium - Used for legal strategy',
        'requirements': 'Must have: violation_type, violation_date, description, evidence',
    },

    'file_metadata': {
        'why': 'Track raw file information from Mac Mini processing',
        'when': 'Created during initial file scan; Rarely updated',
        'where': 'Raw metadata table; May link to legal_documents after processing',
        'who': 'Data owner: File system scanner; Accessed by: Processing pipeline',
        'how': 'Used for file tracking and duplicate detection',
        'relevancy': 'MEDIUM',
        'importance': 6,
        'usage_frequency': 'Low - Backend processing only',
        'requirements': 'Must have: file_path, file_name, file_size, created_date',
    },

    'communications_matrix': {
        'why': 'Track all communications between parties (emails, texts, calls)',
        'when': 'Created when communications logged; Updated with analysis',
        'where': 'Standalone table; May reference legal_documents',
        'who': 'Data owner: Communication tracking team; Accessed by: Legal team',
        'how': 'Queried for communication pattern analysis',
        'relevancy': 'HIGH',
        'importance': 8,
        'usage_frequency': 'Medium - Used for pattern analysis',
        'requirements': 'Must have: communication_date, sender, recipient, communication_type, content',
    },

    'dvro_violations_tracker': {
        'why': 'Track violations of Domestic Violence Restraining Orders',
        'when': 'Created when DVRO violations occur; Updated with evidence',
        'where': 'Specialized tracking table; Links to legal_documents for evidence',
        'who': 'Data owner: Legal team; Accessed by: Attorneys, court',
        'how': 'Queried for DVRO violation reports and legal filings',
        'relevancy': 'HIGH',
        'importance': 9,
        'usage_frequency': 'Low-Medium - Case-specific tracking',
        'requirements': 'Must have: violation_date, violation_type, description, evidence_document_ids',
    },

    'court_case_tracker': {
        'why': 'Track multiple court cases across jurisdictions (forum shopping detection)',
        'when': 'Created when cases identified; Updated with case status',
        'where': 'Cross-jurisdiction tracking table',
        'who': 'Data owner: Legal team; Accessed by: Multi-jurisdiction analysts',
        'how': 'Queried for forum shopping analysis and case coordination',
        'relevancy': 'HIGH',
        'importance': 8,
        'usage_frequency': 'Low-Medium - Strategic analysis',
        'requirements': 'Must have: case_number, court_name, jurisdiction, filing_date, case_status',
    },

    'legal_citations': {
        'why': 'Store legal precedents, case law, and statutory citations',
        'when': 'Created during legal research; Updated with new citations',
        'where': 'Reference table; Linked from legal_documents and legal_violations',
        'who': 'Data owner: Legal research team; Accessed by: Attorneys',
        'how': 'Queried for legal brief preparation and argument support',
        'relevancy': 'MEDIUM',
        'importance': 7,
        'usage_frequency': 'Low - Research purposes',
        'requirements': 'Must have: citation_text, case_name, citation_type; Should have: relevance_to_case',
    },

    'system_processing_cache': {
        'why': 'Cache expensive AI processing results to avoid recomputation',
        'when': 'Created during AI processing; Expires based on TTL',
        'where': 'Performance optimization table (from context_preservation_schema)',
        'who': 'Data owner: System; Accessed by: All AI processing',
        'how': 'Queried before expensive operations to check for cached results',
        'relevancy': 'MEDIUM',
        'importance': 7,
        'usage_frequency': 'Very High - Every AI operation',
        'requirements': 'Must have: cache_key, cache_type, result_data, input_hash',
    },

    'dashboard_snapshots': {
        'why': 'Store complete dashboard states for quick restore and historical reference',
        'when': 'Created on manual save or auto-snapshot; Rarely updated',
        'where': 'Context preservation table',
        'who': 'Data owner: Dashboard users; Accessed by: Dashboard restore function',
        'how': 'Queried when restoring previous dashboard states',
        'relevancy': 'LOW',
        'importance': 5,
        'usage_frequency': 'Low - Snapshot/restore operations',
        'requirements': 'Must have: dashboard_name, snapshot_data, snapshot_date',
    },

    'ai_analysis_results': {
        'why': 'Track all AI model outputs with prompts, responses, and cost tracking',
        'when': 'Created after each AI API call; Never updated',
        'where': 'Audit and cost tracking table',
        'who': 'Data owner: AI processing system; Accessed by: Cost analysts, auditors',
        'how': 'Queried for cost analysis and AI performance review',
        'relevancy': 'MEDIUM',
        'importance': 6,
        'usage_frequency': 'Low - Audit and reporting',
        'requirements': 'Must have: analysis_type, model_name, response_text, api_cost_usd, tokens_used',
    },

    'query_results_cache': {
        'why': 'Cache expensive Supabase query results',
        'when': 'Created during query execution; Expires based on TTL',
        'where': 'Performance optimization table',
        'who': 'Data owner: System; Accessed by: All database queries',
        'how': 'Queried before expensive database operations',
        'relevancy': 'LOW',
        'importance': 5,
        'usage_frequency': 'High - Query optimization',
        'requirements': 'Must have: query_hash, result_data, expires_at',
    },

    'truth_score_history': {
        'why': 'Track truth scores for statements/events with 5W+H context',
        'when': 'Created when truth scores calculated; May be recalculated',
        'where': 'Analysis table for truth/justice scoring',
        'who': 'Data owner: Truth scoring system; Accessed by: Legal strategists',
        'how': 'Queried for truth analysis and credibility assessment',
        'relevancy': 'HIGH',
        'importance': 9,
        'usage_frequency': 'Medium - Truth analysis dashboards',
        'requirements': 'Must have: item_title, truth_score, when_happened, what_occurred, evidence',
    },

    'justice_score_rollups': {
        'why': 'Store aggregated justice scores with detailed breakdowns',
        'when': 'Created during rollup calculations; Recalculated periodically',
        'where': 'Aggregation table for justice metrics',
        'who': 'Data owner: Justice scoring system; Accessed by: Executive dashboards',
        'how': 'Queried for high-level justice metrics and trends',
        'relevancy': 'HIGH',
        'importance': 8,
        'usage_frequency': 'Medium - Executive reporting',
        'requirements': 'Must have: rollup_name, justice_score, total_items, score_breakdown',
    },

    'processing_jobs_log': {
        'why': 'Track all long-running processing jobs for monitoring',
        'when': 'Created when job starts; Updated during execution; Finalized on completion',
        'where': 'Job monitoring table',
        'who': 'Data owner: Processing system; Accessed by: System administrators',
        'how': 'Queried for job status monitoring and failure debugging',
        'relevancy': 'LOW',
        'importance': 6,
        'usage_frequency': 'Medium - System monitoring',
        'requirements': 'Must have: job_type, status, started_at; Should have: progress_percentage, error_message',
    },

    'context_preservation_metadata': {
        'why': 'Store conversation context and system state for AI continuity',
        'when': 'Created during AI sessions; Archived after expiration',
        'where': 'AI context storage',
        'who': 'Data owner: AI system; Accessed by: AI conversation handlers',
        'how': 'Queried to restore AI conversation context',
        'relevancy': 'MEDIUM',
        'importance': 7,
        'usage_frequency': 'High - Every AI session',
        'requirements': 'Must have: context_type, context_data, created_at',
    },
}

# ============================================================================
# SCHEMA DISCOVERY
# ============================================================================

def discover_tables(client):
    """Discover all tables in the database"""
    print("🔍 Discovering database schema...")

    tables = {}

    # List of known tables to check
    known_tables = [
        'legal_documents', 'document_pages', 'court_events', 'legal_violations',
        'file_metadata', 'communications_matrix', 'dvro_violations_tracker',
        'court_case_tracker', 'legal_citations', 'system_processing_cache',
        'dashboard_snapshots', 'ai_analysis_results', 'query_results_cache',
        'truth_score_history', 'justice_score_rollups', 'processing_jobs_log',
        'context_preservation_metadata', 'timeline_events', 'constitutional_violations',
        'police_response_analysis', 'false_statements_on_forms', 'checkbox_perjury_summary',
        'actions_intentions_matrix', 'actions_intentions_discrepancies', 'violation_patterns',
        'general_documents', 'cross_system_priorities', 'business_documents',
        'personal_documents', 'family_documents', 'error_logs'
    ]

    for table in known_tables:
        try:
            # Try to get row count and check if table exists
            response = client.table(table).select('*', count='exact').limit(0).execute()
            row_count = response.count if hasattr(response, 'count') else 0

            # Try to get first row to inspect columns
            sample = client.table(table).select('*').limit(1).execute()
            columns = []
            if sample.data and len(sample.data) > 0:
                columns = list(sample.data[0].keys())

            tables[table] = {
                'exists': True,
                'row_count': row_count,
                'columns': columns,
                'column_count': len(columns),
                'status': 'active' if row_count > 0 else 'empty'
            }

        except Exception as e:
            error_str = str(e)
            if 'PGRST205' in error_str or 'not found' in error_str.lower():
                tables[table] = {
                    'exists': False,
                    'error': 'Table not found'
                }
            else:
                tables[table] = {
                    'exists': True,
                    'error': str(e)
                }

    return tables

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_relevancy(table_name, table_info, metadata):
    """Analyze table relevancy"""
    if not table_info.get('exists'):
        return 'N/A', 0

    relevancy = metadata.get('relevancy', 'MEDIUM')
    importance = metadata.get('importance', 5)

    # Adjust based on row count
    row_count = table_info.get('row_count', 0)
    if row_count == 0:
        relevancy = 'LOW (Empty)'
        importance = max(1, importance - 3)
    elif row_count > 500:
        importance = min(10, importance + 1)

    return relevancy, importance

def categorize_table(table_name, metadata):
    """Categorize table by function"""
    categories = {
        'Core Data': ['legal_documents', 'court_events', 'legal_violations', 'document_pages'],
        'Tracking & Monitoring': ['court_case_tracker', 'dvro_violations_tracker', 'processing_jobs_log', 'error_logs'],
        'Analysis & Intelligence': ['truth_score_history', 'justice_score_rollups', 'police_response_analysis',
                                   'actions_intentions_matrix', 'violation_patterns'],
        'Communication': ['communications_matrix'],
        'Reference Data': ['legal_citations', 'file_metadata'],
        'Performance & Caching': ['system_processing_cache', 'query_results_cache'],
        'Context & State': ['dashboard_snapshots', 'context_preservation_metadata', 'ai_analysis_results'],
        'Multi-Purpose': ['general_documents', 'cross_system_priorities'],
        'CEO Dashboard': ['business_documents', 'personal_documents', 'family_documents'],
        'Timeline': ['timeline_events', 'constitutional_violations'],
        'Perjury Detection': ['false_statements_on_forms', 'checkbox_perjury_summary', 'actions_intentions_discrepancies'],
    }

    for category, tables in categories.items():
        if table_name in tables:
            return category

    return 'Uncategorized'

# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_report(client, output_format='markdown'):
    """Generate comprehensive schema analysis report"""

    print("=" * 80)
    print("PROJ344 SCHEMA ANALYSIS REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Discover tables
    tables = discover_tables(client)

    # Overall statistics
    total_tables = len(tables)
    existing_tables = len([t for t in tables.values() if t.get('exists')])
    active_tables = len([t for t in tables.values() if t.get('status') == 'active'])
    empty_tables = len([t for t in tables.values() if t.get('status') == 'empty'])
    missing_tables = total_tables - existing_tables

    total_rows = sum(t.get('row_count', 0) for t in tables.values() if t.get('exists'))
    total_columns = sum(t.get('column_count', 0) for t in tables.values() if t.get('exists'))

    print("📊 GLOBAL SCHEMA OVERVIEW")
    print("-" * 80)
    print(f"  Total Tables Analyzed: {total_tables}")
    print(f"  ✅ Existing Tables: {existing_tables}")
    print(f"  🟢 Active Tables (with data): {active_tables}")
    print(f"  ⚪ Empty Tables: {empty_tables}")
    print(f"  ❌ Missing Tables: {missing_tables}")
    print(f"  📊 Total Records: {total_rows:,}")
    print(f"  📋 Total Columns: {total_columns}")
    print()

    # Category breakdown
    print("📂 SCHEMA CATEGORIES")
    print("-" * 80)

    categories = defaultdict(list)
    for table_name, table_info in tables.items():
        if table_info.get('exists'):
            metadata = TABLE_METADATA.get(table_name, {})
            category = categorize_table(table_name, metadata)
            categories[category].append((table_name, table_info))

    for category, table_list in sorted(categories.items()):
        active_count = len([t for _, t in table_list if t.get('status') == 'active'])
        total_count = len(table_list)
        print(f"  {category}: {active_count}/{total_count} active")

    print()
    print("=" * 80)
    print("DETAILED TABLE ANALYSIS (5W+H Framework)")
    print("=" * 80)
    print()

    # Sort tables by importance
    table_importance = []
    for table_name, table_info in tables.items():
        if not table_info.get('exists'):
            continue

        metadata = TABLE_METADATA.get(table_name, {
            'why': 'No metadata available',
            'when': 'Unknown',
            'where': 'Unknown',
            'who': 'Unknown',
            'how': 'Unknown',
            'relevancy': 'MEDIUM',
            'importance': 5,
            'usage_frequency': 'Unknown',
            'requirements': 'Not documented'
        })

        relevancy, importance = analyze_relevancy(table_name, table_info, metadata)
        table_importance.append((importance, table_name, table_info, metadata, relevancy))

    # Sort by importance (descending)
    table_importance.sort(reverse=True, key=lambda x: (x[0], x[4], x[2].get('row_count', 0)))

    # Generate detailed reports
    for importance, table_name, table_info, metadata, relevancy in table_importance:
        row_count = table_info.get('row_count', 0)
        status = table_info.get('status', 'unknown')
        columns = table_info.get('columns', [])
        category = categorize_table(table_name, metadata)

        # Status emoji
        if status == 'active':
            status_emoji = '🟢'
        elif status == 'empty':
            status_emoji = '⚪'
        else:
            status_emoji = '❓'

        # Relevancy emoji
        if 'CRITICAL' in relevancy.upper():
            rel_emoji = '🔴'
        elif 'HIGH' in relevancy.upper():
            rel_emoji = '🟠'
        elif 'MEDIUM' in relevancy.upper():
            rel_emoji = '🟡'
        else:
            rel_emoji = '⚪'

        print(f"{status_emoji} {table_name.upper()}")
        print("─" * 80)
        print(f"  Category: {category}")
        print(f"  Status: {status.upper()} | Records: {row_count:,} | Columns: {len(columns)}")
        print(f"  {rel_emoji} Relevancy: {relevancy} | Importance: {importance}/10")
        print()

        print(f"  ❓ WHY (Purpose):")
        print(f"     {metadata['why']}")
        print()

        print(f"  ⏰ WHEN (Temporal Aspects):")
        print(f"     {metadata['when']}")
        print()

        print(f"  📍 WHERE (Location & Relationships):")
        print(f"     {metadata['where']}")
        print()

        print(f"  👤 WHO (Stakeholders):")
        print(f"     {metadata['who']}")
        print()

        print(f"  🔧 HOW (Usage & Access):")
        print(f"     {metadata['how']}")
        print()

        print(f"  📊 Usage Frequency: {metadata['usage_frequency']}")
        print()

        print(f"  ✅ Requirements:")
        print(f"     {metadata['requirements']}")
        print()

        if columns:
            print(f"  📋 Columns ({len(columns)}):")
            # Show first 10 columns
            for col in columns[:10]:
                print(f"     - {col}")
            if len(columns) > 10:
                print(f"     ... and {len(columns) - 10} more")

        print()
        print("=" * 80)
        print()

    # Missing tables
    print("❌ MISSING TABLES")
    print("-" * 80)
    missing = [name for name, info in tables.items() if not info.get('exists')]
    if missing:
        for table_name in missing:
            metadata = TABLE_METADATA.get(table_name, {})
            print(f"  • {table_name}")
            if metadata:
                print(f"    Purpose: {metadata.get('why', 'Not documented')}")
        print()
    else:
        print("  None - All tables exist!")
        print()

    # Recommendations
    print("=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)

    recommendations = []

    # Check for empty critical tables
    for table_name, table_info in tables.items():
        if table_info.get('status') == 'empty' and table_info.get('exists'):
            metadata = TABLE_METADATA.get(table_name, {})
            if metadata.get('relevancy') in ['CRITICAL', 'HIGH']:
                recommendations.append(f"⚠️  Populate {table_name} - marked as {metadata['relevancy']} relevancy but currently empty")

    # Check for missing critical tables
    for table_name, table_info in tables.items():
        if not table_info.get('exists'):
            metadata = TABLE_METADATA.get(table_name, {})
            if metadata.get('relevancy') in ['CRITICAL', 'HIGH']:
                recommendations.append(f"🚨 Create {table_name} - marked as {metadata['relevancy']} relevancy but missing")

    # Performance recommendations
    cache_tables = ['system_processing_cache', 'query_results_cache']
    for cache_table in cache_tables:
        if tables.get(cache_table, {}).get('row_count', 0) > 10000:
            recommendations.append(f"🔧 Consider cache cleanup for {cache_table} - has {tables[cache_table]['row_count']:,} entries")

    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        print()
    else:
        print("  ✅ Schema looks good! No critical issues found.")
        print()

    print("=" * 80)
    print("END OF SCHEMA ANALYSIS REPORT")
    print("=" * 80)

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution"""
    url, key = get_credentials()

    if not key:
        print("❌ Missing SUPABASE_KEY")
        print("\nCreate .streamlit/secrets.toml with:")
        print('SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"')
        print('SUPABASE_KEY = "your-key-here"')
        sys.exit(1)

    try:
        print(f"🔌 Connecting to Supabase...")
        client = create_client(url, key)

        # Test connection
        client.table('legal_documents').select('id', count='exact').limit(0).execute()
        print(f"✅ Connected successfully!\n")

        # Generate report
        generate_report(client)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
