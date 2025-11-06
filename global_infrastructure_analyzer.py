#!/usr/bin/env python3
"""
ASEAGI Global Infrastructure Analyzer
======================================
Comprehensive analysis of all existing infrastructure:
- All Supabase tables and schemas
- Table relationships and foreign keys
- All Streamlit dashboards
- Data flow patterns
- Orchestration opportunities
- Optimization recommendations

Generates unified infrastructure map and workflow recommendations.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import json
import re

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Core imports
try:
    from supabase import create_client
    import toml
    import pandas as pd
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("📦 Install: pip install supabase toml pandas")
    sys.exit(1)


class GlobalInfrastructureAnalyzer:
    """Analyze all existing ASEAGI infrastructure"""

    def __init__(self):
        """Initialize with Supabase connection"""
        self.config = self._load_config()
        self.supabase = create_client(
            self.config['SUPABASE_URL'],
            self.config['SUPABASE_KEY']
        )

        self.tables_info = {}
        self.relationships = []
        self.dashboards = []
        self.python_scripts = []
        self.orchestration_patterns = []

    def _load_config(self) -> Dict[str, str]:
        """Load configuration"""
        secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
        if secrets_path.exists():
            secrets = toml.load(secrets_path)
            return {
                'SUPABASE_URL': secrets.get('SUPABASE_URL'),
                'SUPABASE_KEY': secrets.get('SUPABASE_KEY')
            }
        raise ValueError("❌ Configuration not found")

    # ========================================================================
    # SUPABASE ANALYSIS
    # ========================================================================

    def analyze_all_tables(self) -> Dict[str, Any]:
        """Get comprehensive info about all Supabase tables"""
        print("\n🔍 Analyzing Supabase Tables...")
        print("="*70)

        # Query information_schema to get all tables
        try:
            # Get all tables in public schema
            result = self.supabase.rpc('get_table_info').execute()

            # Fallback: Query each known table
            known_tables = [
                'legal_documents',
                'telegram_uploads',
                'processing_logs',
                'court_events',
                'timeline_events',
                'constitutional_violations',
                'error_logs',
                'user_preferences',
                'document_metadata',
                'case_notes',
                'evidence_registry',
                'notification_queue'
            ]

            for table_name in known_tables:
                try:
                    # Get table structure
                    sample = self.supabase.table(table_name).select('*').limit(1).execute()

                    if sample.data:
                        columns = list(sample.data[0].keys())

                        # Get row count
                        count_result = self.supabase.table(table_name).select('*', count='exact').limit(0).execute()
                        row_count = count_result.count if hasattr(count_result, 'count') else 'Unknown'

                        # Get sample data
                        sample_data = self.supabase.table(table_name).select('*').limit(5).execute()

                        self.tables_info[table_name] = {
                            'columns': columns,
                            'row_count': row_count,
                            'sample_data': sample_data.data,
                            'column_types': self._infer_column_types(sample_data.data[0]) if sample_data.data else {}
                        }

                        print(f"  ✅ {table_name:30} | {len(columns):2} columns | {row_count:5} rows")

                except Exception as e:
                    if 'does not exist' not in str(e):
                        print(f"  ⚠️  {table_name:30} | Error: {str(e)[:50]}")

        except Exception as e:
            print(f"  ⚠️  RPC call failed: {e}")
            print("  ℹ️  Using known tables list")

        print(f"\n📊 Found {len(self.tables_info)} tables")
        return self.tables_info

    def _infer_column_types(self, sample_row: Dict) -> Dict[str, str]:
        """Infer column types from sample data"""
        types = {}
        for col, val in sample_row.items():
            if val is None:
                types[col] = 'nullable'
            elif isinstance(val, int):
                types[col] = 'integer'
            elif isinstance(val, float):
                types[col] = 'float'
            elif isinstance(val, bool):
                types[col] = 'boolean'
            elif isinstance(val, list):
                types[col] = 'array'
            elif isinstance(val, dict):
                types[col] = 'json'
            elif isinstance(val, str):
                if re.match(r'^\d{4}-\d{2}-\d{2}', val):
                    types[col] = 'timestamp'
                elif len(val) > 100:
                    types[col] = 'text'
                else:
                    types[col] = 'string'
            else:
                types[col] = 'unknown'
        return types

    def analyze_relationships(self) -> List[Dict[str, Any]]:
        """Identify relationships between tables"""
        print("\n🔗 Analyzing Table Relationships...")
        print("="*70)

        # Common foreign key patterns
        fk_patterns = {
            '_id': 'ID reference',
            'document_id': 'legal_documents.id',
            'upload_id': 'telegram_uploads.id',
            'event_id': 'court_events.id',
            'case_id': 'case reference',
            'user_id': 'user reference'
        }

        for table_name, info in self.tables_info.items():
            columns = info['columns']

            for col in columns:
                # Check if column matches FK pattern
                for pattern, target in fk_patterns.items():
                    if pattern in col.lower():
                        relationship = {
                            'from_table': table_name,
                            'from_column': col,
                            'to_table': target.split('.')[0] if '.' in target else 'unknown',
                            'relationship_type': 'foreign_key',
                            'confidence': 'high' if '.' in target else 'medium'
                        }
                        self.relationships.append(relationship)
                        print(f"  🔗 {table_name}.{col} → {target}")

        # Look for implicit relationships (same column names)
        common_columns = {}
        for table_name, info in self.tables_info.items():
            for col in info['columns']:
                if col not in ['id', 'created_at', 'updated_at']:
                    if col not in common_columns:
                        common_columns[col] = []
                    common_columns[col].append(table_name)

        print("\n  📎 Implicit Relationships (shared columns):")
        for col, tables in common_columns.items():
            if len(tables) > 1:
                print(f"     {col}: {', '.join(tables)}")
                for i in range(len(tables)):
                    for j in range(i+1, len(tables)):
                        self.relationships.append({
                            'from_table': tables[i],
                            'from_column': col,
                            'to_table': tables[j],
                            'relationship_type': 'shared_column',
                            'confidence': 'low'
                        })

        print(f"\n📊 Found {len(self.relationships)} relationships")
        return self.relationships

    # ========================================================================
    # STREAMLIT DASHBOARD ANALYSIS
    # ========================================================================

    def analyze_dashboards(self) -> List[Dict[str, Any]]:
        """Analyze all Streamlit dashboards"""
        print("\n📊 Analyzing Streamlit Dashboards...")
        print("="*70)

        # Find all .py files in current directory
        dashboard_files = list(Path('.').glob('*.py'))

        for file_path in dashboard_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Check if it's a Streamlit dashboard
                if 'import streamlit' in content or 'streamlit' in content:
                    dashboard_info = {
                        'name': file_path.stem,
                        'file_path': str(file_path),
                        'file_size': file_path.stat().st_size,
                        'tables_accessed': self._extract_tables(content),
                        'functions': self._extract_functions(content),
                        'streamlit_components': self._extract_st_components(content),
                        'external_apis': self._extract_apis(content)
                    }

                    self.dashboards.append(dashboard_info)

                    print(f"  📊 {dashboard_info['name']:40}")
                    print(f"      Tables: {', '.join(dashboard_info['tables_accessed']) if dashboard_info['tables_accessed'] else 'None'}")
                    print(f"      Components: {len(dashboard_info['streamlit_components'])} | Functions: {len(dashboard_info['functions'])}")

            except Exception as e:
                print(f"  ⚠️  {file_path.name:40} | Error: {e}")

        print(f"\n📊 Found {len(self.dashboards)} Streamlit dashboards")
        return self.dashboards

    def _extract_tables(self, content: str) -> List[str]:
        """Extract table names from code"""
        tables = set()
        patterns = [
            r'\.table\([\'"](\w+)[\'"]\)',
            r'from (\w+)',
            r'SELECT .* FROM (\w+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            tables.update(matches)

        # Filter to known tables
        known_tables = set(self.tables_info.keys())
        return list(tables.intersection(known_tables))

    def _extract_functions(self, content: str) -> List[str]:
        """Extract function definitions"""
        pattern = r'def\s+(\w+)\s*\('
        return re.findall(pattern, content)

    def _extract_st_components(self, content: str) -> List[str]:
        """Extract Streamlit components used"""
        components = set()
        pattern = r'st\.(\w+)\('
        matches = re.findall(pattern, content)
        components.update(matches)
        return list(components)

    def _extract_apis(self, content: str) -> List[str]:
        """Extract external API calls"""
        apis = []
        if 'anthropic' in content:
            apis.append('Claude API')
        if 'telegram' in content:
            apis.append('Telegram Bot API')
        if 'qdrant' in content:
            apis.append('Qdrant Vector DB')
        return apis

    # ========================================================================
    # PYTHON SCRIPT ANALYSIS
    # ========================================================================

    def analyze_python_scripts(self) -> List[Dict[str, Any]]:
        """Analyze all Python scripts (non-dashboard)"""
        print("\n🐍 Analyzing Python Scripts...")
        print("="*70)

        python_files = list(Path('.').glob('*.py'))

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Skip if it's a dashboard
                if any(d['file_path'] == str(file_path) for d in self.dashboards):
                    continue

                script_info = {
                    'name': file_path.stem,
                    'file_path': str(file_path),
                    'file_size': file_path.stat().st_size,
                    'script_type': self._classify_script(file_path.stem, content),
                    'tables_accessed': self._extract_tables(content),
                    'functions': self._extract_functions(content),
                    'imports': self._extract_imports(content)
                }

                self.python_scripts.append(script_info)

                print(f"  🐍 {script_info['name']:40} | Type: {script_info['script_type']}")

            except Exception as e:
                print(f"  ⚠️  {file_path.name:40} | Error: {e}")

        print(f"\n📊 Found {len(self.python_scripts)} Python scripts")
        return self.python_scripts

    def _classify_script(self, name: str, content: str) -> str:
        """Classify script by purpose"""
        if 'telegram' in name.lower() or 'bot' in name.lower():
            return 'Telegram Bot'
        elif 'test' in name.lower():
            return 'Test Script'
        elif 'setup' in name.lower() or 'config' in name.lower():
            return 'Setup/Config'
        elif 'bulk' in name.lower() or 'batch' in name.lower():
            return 'Bulk Processing'
        elif 'monitor' in name.lower():
            return 'Monitoring'
        elif 'class ' in content and 'def ' in content:
            return 'Library/Module'
        else:
            return 'Utility Script'

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        imports = set()
        patterns = [
            r'import\s+([\w.]+)',
            r'from\s+([\w.]+)\s+import'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            imports.update(matches)

        return list(imports)

    # ========================================================================
    # ORCHESTRATION ANALYSIS
    # ========================================================================

    def analyze_orchestration(self) -> List[Dict[str, Any]]:
        """Identify orchestration patterns and opportunities"""
        print("\n🔄 Analyzing Orchestration Patterns...")
        print("="*70)

        # Pattern 1: Data flow patterns
        print("\n  📤 Data Flow Patterns:")
        for rel in self.relationships:
            if rel['confidence'] == 'high':
                pattern = {
                    'type': 'data_flow',
                    'source': rel['from_table'],
                    'destination': rel['to_table'],
                    'via': rel['from_column'],
                    'opportunity': f"Automate data sync from {rel['from_table']} to {rel['to_table']}"
                }
                self.orchestration_patterns.append(pattern)
                print(f"     {rel['from_table']} → {rel['to_table']}")

        # Pattern 2: Dashboard-to-table mapping
        print("\n  📊 Dashboard Data Dependencies:")
        for dashboard in self.dashboards:
            if dashboard['tables_accessed']:
                pattern = {
                    'type': 'dashboard_dependency',
                    'dashboard': dashboard['name'],
                    'tables': dashboard['tables_accessed'],
                    'opportunity': f"Real-time updates from {', '.join(dashboard['tables_accessed'])}"
                }
                self.orchestration_patterns.append(pattern)
                print(f"     {dashboard['name']}: {', '.join(dashboard['tables_accessed'])}")

        # Pattern 3: Bot-to-table ingestion
        print("\n  🤖 Bot Ingestion Patterns:")
        bot_scripts = [s for s in self.python_scripts if s['script_type'] == 'Telegram Bot']
        for bot in bot_scripts:
            if bot['tables_accessed']:
                pattern = {
                    'type': 'bot_ingestion',
                    'bot': bot['name'],
                    'tables': bot['tables_accessed'],
                    'opportunity': f"Unified ingestion pipeline via {bot['name']}"
                }
                self.orchestration_patterns.append(pattern)
                print(f"     {bot['name']}: {', '.join(bot['tables_accessed'])}")

        print(f"\n📊 Found {len(self.orchestration_patterns)} orchestration patterns")
        return self.orchestration_patterns

    # ========================================================================
    # GENERATE REPORTS
    # ========================================================================

    def generate_infrastructure_map(self) -> str:
        """Generate complete infrastructure map"""
        print("\n📋 Generating Infrastructure Map...")

        report = []
        report.append("# ASEAGI Global Infrastructure Map")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*70)

        # Tables Section
        report.append("\n## 🗄️  Supabase Tables\n")
        report.append(f"**Total Tables:** {len(self.tables_info)}\n")

        for table_name, info in sorted(self.tables_info.items()):
            report.append(f"### {table_name}")
            report.append(f"- **Rows:** {info['row_count']}")
            report.append(f"- **Columns:** {len(info['columns'])}")
            report.append(f"- **Column List:**")
            for col in info['columns']:
                col_type = info['column_types'].get(col, 'unknown')
                report.append(f"  - `{col}` ({col_type})")
            report.append("")

        # Relationships Section
        report.append("\n## 🔗 Table Relationships\n")
        report.append(f"**Total Relationships:** {len(self.relationships)}\n")

        high_conf = [r for r in self.relationships if r['confidence'] == 'high']
        report.append(f"### High Confidence Relationships ({len(high_conf)})\n")
        for rel in high_conf:
            report.append(f"- `{rel['from_table']}.{rel['from_column']}` → `{rel['to_table']}`")

        # Dashboards Section
        report.append("\n## 📊 Streamlit Dashboards\n")
        report.append(f"**Total Dashboards:** {len(self.dashboards)}\n")

        for dash in sorted(self.dashboards, key=lambda x: x['name']):
            report.append(f"### {dash['name']}")
            report.append(f"- **File:** `{dash['file_path']}`")
            report.append(f"- **Size:** {dash['file_size']:,} bytes")
            report.append(f"- **Tables Accessed:** {', '.join(dash['tables_accessed']) if dash['tables_accessed'] else 'None'}")
            report.append(f"- **Components:** {len(dash['streamlit_components'])} Streamlit components")
            report.append(f"- **Functions:** {len(dash['functions'])} functions")
            report.append("")

        # Scripts Section
        report.append("\n## 🐍 Python Scripts\n")
        report.append(f"**Total Scripts:** {len(self.python_scripts)}\n")

        script_types = {}
        for script in self.python_scripts:
            stype = script['script_type']
            if stype not in script_types:
                script_types[stype] = []
            script_types[stype].append(script)

        for stype, scripts in sorted(script_types.items()):
            report.append(f"### {stype} ({len(scripts)})\n")
            for script in scripts:
                report.append(f"- **{script['name']}**")
                report.append(f"  - Tables: {', '.join(script['tables_accessed']) if script['tables_accessed'] else 'None'}")
                report.append("")

        # Orchestration Section
        report.append("\n## 🔄 Orchestration Patterns\n")
        report.append(f"**Total Patterns:** {len(self.orchestration_patterns)}\n")

        pattern_types = {}
        for pattern in self.orchestration_patterns:
            ptype = pattern['type']
            if ptype not in pattern_types:
                pattern_types[ptype] = []
            pattern_types[ptype].append(pattern)

        for ptype, patterns in sorted(pattern_types.items()):
            report.append(f"### {ptype.replace('_', ' ').title()} ({len(patterns)})\n")
            for pattern in patterns:
                report.append(f"- **{pattern.get('source', pattern.get('dashboard', pattern.get('bot', 'Unknown')))}**")
                report.append(f"  - Opportunity: {pattern['opportunity']}")
                report.append("")

        return "\n".join(report)

    def generate_recommendations(self) -> str:
        """Generate optimization recommendations"""
        print("\n💡 Generating Recommendations...")

        recommendations = []
        recommendations.append("# ASEAGI Optimization Recommendations")
        recommendations.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        recommendations.append("="*70)

        # Recommendation 1: Consolidate duplicate tables
        recommendations.append("\n## 1. 🗄️  Database Optimization\n")

        # Check for similar tables
        table_names = list(self.tables_info.keys())
        similar_tables = []
        for i, t1 in enumerate(table_names):
            for t2 in table_names[i+1:]:
                if self._tables_similar(t1, t2):
                    similar_tables.append((t1, t2))

        if similar_tables:
            recommendations.append("### ⚠️  Potential Table Consolidation Opportunities:\n")
            for t1, t2 in similar_tables:
                recommendations.append(f"- **{t1}** and **{t2}** may have overlapping purposes")
                recommendations.append(f"  - Consider: Merge into single table or create clear separation")
        else:
            recommendations.append("✅ No obvious table consolidation needed\n")

        # Recommendation 2: Dashboard optimization
        recommendations.append("\n## 2. 📊 Dashboard Optimization\n")

        # Check for dashboards accessing same tables
        table_to_dashboards = {}
        for dash in self.dashboards:
            for table in dash['tables_accessed']:
                if table not in table_to_dashboards:
                    table_to_dashboards[table] = []
                table_to_dashboards[table].append(dash['name'])

        recommendations.append("### Dashboard-Table Access Patterns:\n")
        for table, dashboards in sorted(table_to_dashboards.items()):
            if len(dashboards) > 1:
                recommendations.append(f"- **{table}** accessed by {len(dashboards)} dashboards:")
                for dash in dashboards:
                    recommendations.append(f"  - {dash}")
                recommendations.append(f"  - 💡 Consider: Create shared data layer or unified dashboard")
                recommendations.append("")

        # Recommendation 3: Ingestion consolidation
        recommendations.append("\n## 3. 📥 Ingestion Pipeline Optimization\n")

        bot_scripts = [s for s in self.python_scripts if s['script_type'] == 'Telegram Bot']
        if len(bot_scripts) > 1:
            recommendations.append(f"### ⚠️  Multiple Ingestion Bots Detected ({len(bot_scripts)}):\n")
            for bot in bot_scripts:
                recommendations.append(f"- **{bot['name']}**")
                recommendations.append(f"  - Tables: {', '.join(bot['tables_accessed'])}")
            recommendations.append("\n💡 **Recommendation:**")
            recommendations.append("- Create unified ingestion orchestrator")
            recommendations.append("- Use bulk_document_ingestion.py as central processor")
            recommendations.append("- Bots become thin clients that route to orchestrator")
        else:
            recommendations.append("✅ Single ingestion pipeline detected\n")

        # Recommendation 4: Missing relationships
        recommendations.append("\n## 4. 🔗 Missing Relationships\n")

        # Check for tables with no relationships
        tables_with_relations = set()
        for rel in self.relationships:
            tables_with_relations.add(rel['from_table'])
            tables_with_relations.add(rel['to_table'])

        isolated_tables = set(self.tables_info.keys()) - tables_with_relations
        if isolated_tables:
            recommendations.append("### ⚠️  Isolated Tables (No Relationships):\n")
            for table in sorted(isolated_tables):
                recommendations.append(f"- **{table}**")
                recommendations.append(f"  - 💡 Consider: Add foreign keys or document isolation reason")
        else:
            recommendations.append("✅ All tables have relationships\n")

        # Recommendation 5: Workflow optimization
        recommendations.append("\n## 5. 🔄 Workflow Optimization\n")

        recommendations.append("### Recommended Unified Workflow:\n")
        recommendations.append("""
```
1. Document Ingestion (All Sources)
   ├── Telegram Bot (Phone uploads)
   ├── Bulk Processor (Folder scans)
   └── Cloud Sync (Google Drive, etc.)
              ↓
2. Central Processing Pipeline
   ├── Duplicate Detection (MD5 hash)
   ├── OCR Processing (Tesseract + Claude)
   ├── Metadata Extraction
   └── Quality Validation
              ↓
3. Database Storage (Supabase)
   ├── legal_documents (primary)
   ├── document_metadata (extended)
   └── processing_logs (audit)
              ↓
4. Real-time Dashboards
   ├── Master Dashboard (overview)
   ├── Timeline Dashboard (events)
   └── Bulk Ingestion Monitor (progress)
```
""")

        return "\n".join(recommendations)

    def _tables_similar(self, t1: str, t2: str) -> bool:
        """Check if two tables have similar purposes"""
        # Simple similarity check based on name
        similarity_keywords = [
            ('document', 'doc'),
            ('upload', 'ingestion'),
            ('event', 'timeline'),
            ('log', 'audit')
        ]

        for kw1, kw2 in similarity_keywords:
            if (kw1 in t1 and kw2 in t2) or (kw2 in t1 and kw1 in t2):
                return True

        return False

    # ========================================================================
    # EXPORT
    # ========================================================================

    def export_json(self, filename: str = "infrastructure_analysis.json"):
        """Export analysis as JSON"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'tables': self.tables_info,
            'relationships': self.relationships,
            'dashboards': self.dashboards,
            'python_scripts': self.python_scripts,
            'orchestration_patterns': self.orchestration_patterns
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

        print(f"\n💾 Exported to {filename}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main analysis"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  ASEAGI Global Infrastructure Analyzer                       ║
║  Comprehensive analysis of all existing infrastructure       ║
╚═══════════════════════════════════════════════════════════════╝
""")

    try:
        analyzer = GlobalInfrastructureAnalyzer()

        # Run all analyses
        analyzer.analyze_all_tables()
        analyzer.analyze_relationships()
        analyzer.analyze_dashboards()
        analyzer.analyze_python_scripts()
        analyzer.analyze_orchestration()

        # Generate reports
        infra_map = analyzer.generate_infrastructure_map()
        recommendations = analyzer.generate_recommendations()

        # Save reports
        with open('INFRASTRUCTURE_MAP.md', 'w', encoding='utf-8') as f:
            f.write(infra_map)
        print("\n📄 Saved: INFRASTRUCTURE_MAP.md")

        with open('OPTIMIZATION_RECOMMENDATIONS.md', 'w', encoding='utf-8') as f:
            f.write(recommendations)
        print("📄 Saved: OPTIMIZATION_RECOMMENDATIONS.md")

        # Export JSON
        analyzer.export_json()

        print("\n✅ Analysis Complete!")
        print("\nGenerated Files:")
        print("  1. INFRASTRUCTURE_MAP.md - Complete infrastructure map")
        print("  2. OPTIMIZATION_RECOMMENDATIONS.md - Optimization recommendations")
        print("  3. infrastructure_analysis.json - Raw data export")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
