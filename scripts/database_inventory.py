#!/usr/bin/env python3
"""
Supabase Database Inventory & Health Check
Generates complete picture of all tables, schemas, and health metrics
"""

import os
from datetime import datetime
from supabase import create_client
from typing import Dict, List, Any
import json

class SupabaseDatabaseInventory:
    """Complete Supabase database inventory and health check"""

    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.inventory = {
            'timestamp': datetime.now().isoformat(),
            'databases': [],
            'schemas': [],
            'tables': [],
            'health': {},
            'statistics': {}
        }

    def get_all_tables(self) -> List[Dict]:
        """Get all tables from information_schema"""
        query = """
        SELECT
            table_schema,
            table_name,
            table_type
        FROM information_schema.tables
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name;
        """

        result = self.supabase.rpc('exec_sql', {'sql': query}).execute()
        return result.data if result.data else []

    def get_table_columns(self, schema: str, table: str) -> List[Dict]:
        """Get all columns for a specific table"""
        query = f"""
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = '{schema}'
        AND table_name = '{table}'
        ORDER BY ordinal_position;
        """

        result = self.supabase.rpc('exec_sql', {'sql': query}).execute()
        return result.data if result.data else []

    def get_table_row_count(self, schema: str, table: str) -> int:
        """Get row count for a table"""
        try:
            # For public schema tables, we can query directly
            if schema == 'public':
                result = self.supabase.table(table).select('*', count='exact').limit(1).execute()
                return result.count if hasattr(result, 'count') else 0
        except Exception as e:
            print(f"  Warning: Could not count rows in {schema}.{table}: {e}")
            return 0
        return 0

    def get_table_last_modified(self, schema: str, table: str) -> str:
        """Get last modified timestamp if table has updated_at or created_at"""
        try:
            if schema == 'public':
                # Try updated_at first
                result = self.supabase.table(table)\
                    .select('updated_at')\
                    .order('updated_at', desc=True)\
                    .limit(1)\
                    .execute()

                if result.data and len(result.data) > 0:
                    return result.data[0].get('updated_at', 'Unknown')

                # Try created_at
                result = self.supabase.table(table)\
                    .select('created_at')\
                    .order('created_at', desc=True)\
                    .limit(1)\
                    .execute()

                if result.data and len(result.data) > 0:
                    return result.data[0].get('created_at', 'Unknown')
        except:
            pass

        return 'Unknown'

    def analyze_table(self, schema: str, table: str) -> Dict[str, Any]:
        """Complete analysis of a single table"""
        print(f"  Analyzing {schema}.{table}...")

        columns = self.get_table_columns(schema, table)
        row_count = self.get_table_row_count(schema, table)
        last_modified = self.get_table_last_modified(schema, table)

        # Check for common timestamp columns
        has_created_at = any(col['column_name'] == 'created_at' for col in columns)
        has_updated_at = any(col['column_name'] == 'updated_at' for col in columns)
        has_timestamps = has_created_at or has_updated_at

        # Check for primary key
        has_id = any(col['column_name'] in ['id', 'uuid'] for col in columns)

        return {
            'schema': schema,
            'table': table,
            'columns': columns,
            'column_count': len(columns),
            'row_count': row_count,
            'last_modified': last_modified,
            'has_timestamps': has_timestamps,
            'has_created_at': has_created_at,
            'has_updated_at': has_updated_at,
            'has_primary_key': has_id,
            'status': 'healthy' if row_count >= 0 else 'error'
        }

    def run_health_checks(self) -> Dict[str, Any]:
        """Run health checks on database"""
        health = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }

        # Check connection
        try:
            self.supabase.table('legal_documents').select('id').limit(1).execute()
            health['checks']['connection'] = {'status': 'ok', 'message': 'Database connection successful'}
        except Exception as e:
            health['checks']['connection'] = {'status': 'error', 'message': str(e)}
            health['overall_status'] = 'error'

        # Check key tables exist
        key_tables = [
            'legal_documents',
            'court_events',
            'legal_violations',
            'bugs',
            'error_logs'
        ]

        for table in key_tables:
            try:
                result = self.supabase.table(table).select('*', count='exact').limit(1).execute()
                health['checks'][f'table_{table}'] = {
                    'status': 'ok',
                    'row_count': result.count if hasattr(result, 'count') else 0
                }
            except Exception as e:
                health['checks'][f'table_{table}'] = {
                    'status': 'error',
                    'message': str(e)
                }

        return health

    def generate_statistics(self, tables: List[Dict]) -> Dict[str, Any]:
        """Generate overall statistics"""
        total_rows = sum(t['row_count'] for t in tables)
        total_columns = sum(t['column_count'] for t in tables)

        tables_with_timestamps = sum(1 for t in tables if t['has_timestamps'])
        tables_with_data = sum(1 for t in tables if t['row_count'] > 0)

        return {
            'total_tables': len(tables),
            'total_schemas': len(set(t['schema'] for t in tables)),
            'total_rows': total_rows,
            'total_columns': total_columns,
            'tables_with_timestamps': tables_with_timestamps,
            'tables_with_data': tables_with_data,
            'empty_tables': len(tables) - tables_with_data,
            'largest_table': max(tables, key=lambda t: t['row_count']) if tables else None,
            'most_columns': max(tables, key=lambda t: t['column_count']) if tables else None
        }

    def run_full_inventory(self) -> Dict[str, Any]:
        """Run complete database inventory"""
        print("\n" + "="*60)
        print("🔍 SUPABASE DATABASE INVENTORY")
        print("="*60)
        print(f"Timestamp: {self.inventory['timestamp']}")
        print(f"Database: {self.supabase_url}")
        print("")

        # Get all tables
        print("📋 Fetching all tables...")
        all_tables = self.get_all_tables()
        schemas = list(set(t['table_schema'] for t in all_tables))

        print(f"Found {len(all_tables)} tables across {len(schemas)} schemas")
        print(f"Schemas: {', '.join(schemas)}")
        print("")

        # Analyze each table
        print("📊 Analyzing tables...")
        table_analyses = []
        for table_info in all_tables:
            schema = table_info['table_schema']
            table = table_info['table_name']
            analysis = self.analyze_table(schema, table)
            table_analyses.append(analysis)

        print("")

        # Run health checks
        print("🏥 Running health checks...")
        health = self.run_health_checks()
        print("")

        # Generate statistics
        print("📈 Generating statistics...")
        stats = self.generate_statistics(table_analyses)

        # Compile full inventory
        self.inventory['schemas'] = schemas
        self.inventory['tables'] = table_analyses
        self.inventory['health'] = health
        self.inventory['statistics'] = stats

        return self.inventory

    def print_summary(self):
        """Print human-readable summary"""
        stats = self.inventory['statistics']
        health = self.inventory['health']

        print("\n" + "="*60)
        print("📊 DATABASE SUMMARY")
        print("="*60)
        print(f"Total Schemas: {stats['total_schemas']}")
        print(f"Total Tables: {stats['total_tables']}")
        print(f"Total Rows: {stats['total_rows']:,}")
        print(f"Total Columns: {stats['total_columns']}")
        print(f"Tables with Data: {stats['tables_with_data']}")
        print(f"Empty Tables: {stats['empty_tables']}")
        print("")

        if stats['largest_table']:
            lt = stats['largest_table']
            print(f"Largest Table: {lt['table']} ({lt['row_count']:,} rows)")

        if stats['most_columns']:
            mc = stats['most_columns']
            print(f"Most Columns: {mc['table']} ({mc['column_count']} columns)")

        print("")
        print(f"Overall Health: {health['overall_status'].upper()}")
        print("")

        print("📋 TABLE DETAILS:")
        print("-" * 60)
        for table in self.inventory['tables']:
            status_icon = "✅" if table['status'] == 'healthy' else "❌"
            timestamp_icon = "🕒" if table['has_timestamps'] else "  "

            print(f"{status_icon} {timestamp_icon} {table['schema']}.{table['table']}")
            print(f"   Rows: {table['row_count']:,} | Columns: {table['column_count']}")
            print(f"   Last Modified: {table['last_modified']}")
            print("")

    def export_to_json(self, filename: str = 'database_inventory.json'):
        """Export inventory to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.inventory, f, indent=2, default=str)
        print(f"✅ Inventory exported to {filename}")

    def export_to_markdown(self, filename: str = 'DATABASE_INVENTORY.md'):
        """Export inventory to Markdown file"""
        stats = self.inventory['statistics']

        md = f"""# 📊 Supabase Database Inventory

**Generated:** {self.inventory['timestamp']}
**Database:** {self.supabase_url}

---

## 📈 Overview Statistics

- **Total Schemas:** {stats['total_schemas']}
- **Total Tables:** {stats['total_tables']}
- **Total Rows:** {stats['total_rows']:,}
- **Total Columns:** {stats['total_columns']}
- **Tables with Data:** {stats['tables_with_data']}
- **Empty Tables:** {stats['empty_tables']}

"""

        if stats['largest_table']:
            lt = stats['largest_table']
            md += f"**Largest Table:** `{lt['table']}` ({lt['row_count']:,} rows)\n\n"

        md += "---\n\n## 📋 All Tables\n\n"

        for table in self.inventory['tables']:
            status = "✅" if table['status'] == 'healthy' else "❌"
            timestamps = "🕒 Timestamped" if table['has_timestamps'] else ""

            md += f"### {status} `{table['schema']}.{table['table']}` {timestamps}\n\n"
            md += f"- **Rows:** {table['row_count']:,}\n"
            md += f"- **Columns:** {table['column_count']}\n"
            md += f"- **Last Modified:** {table['last_modified']}\n"
            md += f"- **Has Primary Key:** {'Yes' if table['has_primary_key'] else 'No'}\n"
            md += f"- **Has Timestamps:** {'Yes' if table['has_timestamps'] else 'No'}\n"

            if table['columns']:
                md += "\n**Columns:**\n"
                for col in table['columns'][:10]:  # Show first 10 columns
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    md += f"- `{col['column_name']}` - {col['data_type']} ({nullable})\n"

                if len(table['columns']) > 10:
                    md += f"- *... and {len(table['columns']) - 10} more columns*\n"

            md += "\n"

        md += "---\n\n## 🏥 Health Status\n\n"
        md += f"**Overall Status:** {self.inventory['health']['overall_status'].upper()}\n\n"

        for check_name, check_result in self.inventory['health']['checks'].items():
            status_icon = "✅" if check_result['status'] == 'ok' else "❌"
            md += f"{status_icon} **{check_name}:** {check_result.get('message', 'OK')}\n"

        with open(filename, 'w') as f:
            f.write(md)

        print(f"✅ Inventory exported to {filename}")


def main():
    """Run database inventory"""
    try:
        inventory = SupabaseDatabaseInventory()
        result = inventory.run_full_inventory()
        inventory.print_summary()

        # Export results
        inventory.export_to_json('database_inventory.json')
        inventory.export_to_markdown('DATABASE_INVENTORY.md')

        print("\n" + "="*60)
        print("✅ Database inventory complete!")
        print("="*60)

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    main()
