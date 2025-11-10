#!/usr/bin/env python3
"""
Database Schema Validator
Prevents schema mismatch issues by validating all queries against actual Supabase schema
"""
import os
import sys
from pathlib import Path
from supabase import create_client
import re
import json
from datetime import datetime

class SchemaValidator:
    """Validates database queries against actual Supabase schema"""

    def __init__(self):
        self.supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_KEY")
        )
        self.schema_cache = {}
        self.errors = []
        self.warnings = []

    def fetch_table_schema(self, table_name: str) -> dict:
        """Fetch actual schema for a table from Supabase"""
        if table_name in self.schema_cache:
            return self.schema_cache[table_name]

        try:
            # Get table columns by querying with limit 0
            result = self.supabase.table(table_name).select("*").limit(0).execute()

            # Also get a sample row to see actual data structure
            sample = self.supabase.table(table_name).select("*").limit(1).execute()

            columns = []
            if sample.data and len(sample.data) > 0:
                columns = list(sample.data[0].keys())

            schema = {
                "table": table_name,
                "columns": columns,
                "fetched_at": datetime.utcnow().isoformat()
            }

            self.schema_cache[table_name] = schema
            return schema

        except Exception as e:
            self.errors.append(f"Failed to fetch schema for {table_name}: {e}")
            return {"table": table_name, "columns": [], "error": str(e)}

    def validate_query_columns(self, table_name: str, queried_columns: list) -> dict:
        """Validate that queried columns exist in table schema"""
        schema = self.fetch_table_schema(table_name)
        actual_columns = schema.get("columns", [])

        missing_columns = []
        valid_columns = []

        for col in queried_columns:
            if col == "*":
                valid_columns.append(col)
                continue

            if col not in actual_columns:
                missing_columns.append(col)
            else:
                valid_columns.append(col)

        return {
            "table": table_name,
            "queried": queried_columns,
            "valid": valid_columns,
            "missing": missing_columns,
            "actual_schema": actual_columns
        }

    def scan_python_file(self, file_path: str) -> list:
        """Scan a Python file for Supabase queries and validate them"""
        issues = []

        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        # Find all .table('...').select(...) patterns
        table_pattern = r'\.table\(["\'](\w+)["\']\)'
        select_pattern = r'\.select\(["\']([^"\']+)["\']\)'

        table_matches = re.finditer(table_pattern, content)

        for table_match in table_matches:
            table_name = table_match.group(1)

            # Find the corresponding select after this table
            search_start = table_match.end()
            remaining = content[search_start:search_start+500]

            select_match = re.search(select_pattern, remaining)

            if select_match:
                select_columns_str = select_match.group(1)

                # Parse columns
                if select_columns_str.strip() == "*":
                    continue  # SELECT * is always valid

                # Split by comma and clean
                columns = [c.strip() for c in select_columns_str.split(',')]

                # Validate
                validation = self.validate_query_columns(table_name, columns)

                if validation['missing']:
                    # Find line number
                    line_num = content[:table_match.start()].count('\n') + 1

                    issues.append({
                        "file": file_path,
                        "line": line_num,
                        "table": table_name,
                        "queried_columns": columns,
                        "missing_columns": validation['missing'],
                        "actual_columns": validation['actual_schema'],
                        "severity": "ERROR"
                    })

        # Also check .get() calls on query results
        get_pattern = r'\.get\(["\'](\w+)["\']\)'

        return issues

    def scan_directory(self, directory: str, extensions: list = ['.py']) -> dict:
        """Scan all files in a directory for schema mismatches"""
        all_issues = []
        files_scanned = 0

        for ext in extensions:
            for file_path in Path(directory).rglob(f'*{ext}'):
                if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                    continue

                try:
                    issues = self.scan_python_file(str(file_path))
                    all_issues.extend(issues)
                    files_scanned += 1
                except Exception as e:
                    self.warnings.append(f"Failed to scan {file_path}: {e}")

        return {
            "files_scanned": files_scanned,
            "issues_found": len(all_issues),
            "issues": all_issues,
            "errors": self.errors,
            "warnings": self.warnings
        }

    def generate_schema_docs(self, output_file: str = "database/SCHEMA.md"):
        """Generate documentation for all database tables"""
        tables = [
            "legal_documents",
            "legal_violations",
            "court_events",
            "bugs",
            "incidents"
        ]

        docs = ["# Database Schema Reference\n"]
        docs.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        docs.append("**Purpose:** Prevent schema mismatch issues by documenting actual table structures\n\n")

        for table in tables:
            schema = self.fetch_table_schema(table)

            docs.append(f"## Table: `{table}`\n")

            if schema.get('error'):
                docs.append(f"**Error:** {schema['error']}\n\n")
                continue

            docs.append("### Columns:\n")
            for col in schema['columns']:
                docs.append(f"- `{col}`\n")

            docs.append(f"\n### Example Query:\n")
            docs.append(f"```python\n")
            docs.append(f"result = supabase.table('{table}').select('*').execute()\n")
            docs.append(f"# Access columns:\n")
            for col in schema['columns'][:5]:  # Show first 5
                docs.append(f"data['{col}']\n")
            docs.append(f"```\n\n")

        # Write to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(''.join(docs))

        return output_file

def main():
    """Run schema validation"""
    print("=" * 80)
    print("ASEAGI Database Schema Validator")
    print("=" * 80)
    print()

    validator = SchemaValidator()

    # 1. Generate schema documentation
    print("📝 Generating schema documentation...")
    doc_file = validator.generate_schema_docs()
    print(f"   ✅ Created: {doc_file}")
    print()

    # 2. Scan codebase for issues
    print("🔍 Scanning codebase for schema mismatches...")
    results = validator.scan_directory(".", extensions=['.py'])
    print(f"   Scanned: {results['files_scanned']} files")
    print(f"   Issues: {results['issues_found']}")
    print()

    # 3. Report issues
    if results['issues']:
        print("❌ SCHEMA MISMATCH ISSUES FOUND:")
        print()

        for i, issue in enumerate(results['issues'], 1):
            print(f"{i}. {issue['file']}:{issue['line']}")
            print(f"   Table: {issue['table']}")
            print(f"   Missing columns: {', '.join(issue['missing_columns'])}")
            print(f"   Available columns: {', '.join(issue['actual_columns'][:10])}")
            print()

        return 1  # Exit with error code
    else:
        print("✅ No schema mismatch issues found!")
        print()

    # 4. Show warnings
    if results['warnings']:
        print("⚠️  WARNINGS:")
        for warning in results['warnings']:
            print(f"   {warning}")
        print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
