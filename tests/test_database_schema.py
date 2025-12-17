#!/usr/bin/env python3
"""
Automated tests for database schema validation
Prevents schema mismatch issues from being deployed
"""
import unittest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client

class TestDatabaseSchema(unittest.TestCase):
    """Test database schema matches code expectations"""

    @classmethod
    def setUpClass(cls):
        """Initialize Supabase client"""
        cls.supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_KEY")
        )

    def get_table_columns(self, table_name: str) -> list:
        """Get actual columns from a table"""
        result = self.supabase.table(table_name).select("*").limit(1).execute()
        if result.data and len(result.data) > 0:
            return list(result.data[0].keys())
        return []

    # LEGAL_VIOLATIONS TABLE TESTS
    def test_legal_violations_required_columns(self):
        """Verify legal_violations table has all required columns"""
        columns = self.get_table_columns("legal_violations")

        required = [
            "id",
            "violation_category",
            "violation_title",
            "violation_description",
            "perpetrator",
            "violation_date",
            "severity_score",
            "legal_basis",
            "evidence_summary",
            "document_id",
            "incident_id"
        ]

        for col in required:
            self.assertIn(col, columns,
                f"Missing required column '{col}' in legal_violations table")

    def test_legal_violations_no_deprecated_columns(self):
        """Verify legal_violations doesn't have deprecated column names"""
        columns = self.get_table_columns("legal_violations")

        deprecated = [
            "violation_type",  # Use violation_category instead
            "document_title",  # Use violation_title instead
            "severity"  # Use severity_score instead
        ]

        for col in deprecated:
            self.assertNotIn(col, columns,
                f"Found deprecated column '{col}' in legal_violations table. "
                f"Code should not use this column.")

    # LEGAL_DOCUMENTS TABLE TESTS
    def test_legal_documents_required_columns(self):
        """Verify legal_documents table has all required columns"""
        columns = self.get_table_columns("legal_documents")

        required = [
            "id",
            "file_name",
            "document_type",
            "category",
            "relevancy_number",
            "micro_number",
            "macro_number",
            "legal_number",
            "summary",
            "key_quotes",
            "fraud_indicators",
            "perjury_indicators",
            "contains_false_statements",
            "document_date",
            "processed_at",
            "docket_number"
        ]

        for col in required:
            self.assertIn(col, columns,
                f"Missing required column '{col}' in legal_documents table")

    # COURT_EVENTS TABLE TESTS
    def test_court_events_required_columns(self):
        """Verify court_events table has all required columns"""
        columns = self.get_table_columns("court_events")

        required = [
            "id",
            "event_date",
            "event_title",
            "event_description",
            "event_type",
            "judge_name"
        ]

        for col in required:
            self.assertIn(col, columns,
                f"Missing required column '{col}' in court_events table")

    # BUGS TABLE TESTS
    def test_bugs_required_columns(self):
        """Verify bugs table has all required columns"""
        columns = self.get_table_columns("bugs")

        required = [
            "id",
            "bug_number",
            "title",
            "description",
            "bug_type",
            "severity",
            "priority",
            "status",
            "component",
            "tags",
            "workspace_id",
            "created_at",
            "updated_at"
        ]

        for col in required:
            self.assertIn(col, columns,
                f"Missing required column '{col}' in bugs table")

    # INCIDENTS TABLE TESTS
    def test_incidents_required_columns(self):
        """Verify incidents table has all required columns"""
        columns = self.get_table_columns("incidents")

        required = [
            "id",
            "incident_date",
            "incident_title",
            "incident_description",
            "incident_category",
            "severity_level",
            "reported_by",
            "case_id"
        ]

        for col in required:
            self.assertIn(col, columns,
                f"Missing required column '{col}' in incidents table")

    # TELEGRAM BOT VALIDATION
    def test_telegram_bot_violations_query_matches_schema(self):
        """Verify Telegram bot violations command uses correct columns"""
        # This test ensures the bot code matches the actual schema
        bot_file = Path(__file__).parent.parent / "scanners" / "telegram_bot_simple.py"

        if not bot_file.exists():
            self.skipTest("Telegram bot file not found")

        with open(bot_file, 'r') as f:
            bot_code = f.read()

        # Check for correct column usage
        self.assertIn("violation_category", bot_code,
            "Telegram bot should use 'violation_category' not 'violation_type'")
        self.assertIn("violation_title", bot_code,
            "Telegram bot should use 'violation_title' not 'document_title'")
        self.assertIn("severity_score", bot_code,
            "Telegram bot should use 'severity_score' not 'severity'")

        # Check for deprecated column usage (should NOT be present)
        self.assertNotIn("violation_type", bot_code,
            "Telegram bot should not use deprecated 'violation_type' column")

    # STREAMLIT DASHBOARD VALIDATION
    def test_streamlit_violations_dashboard_queries_correct_table(self):
        """Verify Streamlit violations dashboard queries legal_violations table"""
        dashboard_file = Path(__file__).parent.parent / "dashboards" / "timeline_violations_dashboard.py"

        if not dashboard_file.exists():
            self.skipTest("Violations dashboard file not found")

        with open(dashboard_file, 'r') as f:
            dashboard_code = f.read()

        # Should query legal_violations table
        self.assertIn("legal_violations", dashboard_code,
            "Violations dashboard must query 'legal_violations' table")

        # Should use correct columns
        self.assertIn("violation_category", dashboard_code,
            "Dashboard should use 'violation_category'")
        self.assertIn("severity_score", dashboard_code,
            "Dashboard should use 'severity_score'")

class TestSchemaConsistency(unittest.TestCase):
    """Test that schema is consistent across all components"""

    @classmethod
    def setUpClass(cls):
        cls.supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_KEY")
        )

    def test_all_tables_accessible(self):
        """Verify all expected tables are accessible"""
        tables = [
            "legal_documents",
            "legal_violations",
            "court_events",
            "bugs",
            "incidents"
        ]

        for table in tables:
            with self.subTest(table=table):
                try:
                    result = self.supabase.table(table).select("*").limit(1).execute()
                    self.assertIsNotNone(result.data,
                        f"Table '{table}' should be accessible")
                except Exception as e:
                    self.fail(f"Failed to access table '{table}': {e}")

if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
