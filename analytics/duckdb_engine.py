"""
DuckDB Analytics Engine for ASEAGI
Just-in-time analytics with background sync from Supabase
"""

import duckdb
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import threading
import time
import os
from dataclasses import dataclass


@dataclass
class SyncStatus:
    """Status of the last sync operation"""
    documents_synced: int
    cases_synced: int
    jurisdictions_synced: int
    sync_time: str
    success: bool
    error: Optional[str] = None


class DuckDBAnalyticsEngine:
    """Just-in-time analytics with DuckDB and Supabase sync"""

    def __init__(
        self,
        db_path: str = "analytics.duckdb",
        supabase_client=None,
        sync_interval_minutes: int = 5,
        auto_sync: bool = True
    ):
        """
        Initialize DuckDB analytics engine.

        Args:
            db_path: Path to DuckDB database file
            supabase_client: Initialized Supabase client
            sync_interval_minutes: How often to sync (0 to disable)
            auto_sync: Whether to start background sync automatically
        """
        self.db_path = db_path
        self.supabase = supabase_client
        self.conn = duckdb.connect(db_path)
        self.last_sync: Optional[datetime] = None
        self.sync_thread: Optional[threading.Thread] = None
        self._stop_sync = threading.Event()

        # Initialize schema
        self._init_schema()

        # Start background sync if enabled
        if auto_sync and sync_interval_minutes > 0 and supabase_client:
            self._start_background_sync(sync_interval_minutes)

    def _init_schema(self):
        """Initialize DuckDB schema optimized for analytics"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id VARCHAR PRIMARY KEY,
                case_id VARCHAR,
                jurisdiction_id VARCHAR,
                jurisdiction_code VARCHAR,
                case_number VARCHAR,
                document_type VARCHAR,
                date DATE,
                title VARCHAR,
                original_filename VARCHAR,
                summary TEXT,
                relevancy_number INTEGER,
                micro_number INTEGER,
                macro_number INTEGER,
                legal_number INTEGER,
                truth_score INTEGER,
                justice_score INTEGER,
                contains_false_statements BOOLEAN,
                key_quotes VARCHAR,
                fraud_indicators VARCHAR,
                perjury_indicators VARCHAR,
                api_cost_usd DOUBLE,
                processed_at TIMESTAMP,
                created_at TIMESTAMP,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS cases (
                id VARCHAR PRIMARY KEY,
                case_number VARCHAR UNIQUE,
                court_case_number VARCHAR,
                court_name VARCHAR,
                jurisdiction_id VARCHAR,
                jurisdiction_code VARCHAR,
                case_type VARCHAR,
                case_subtype VARCHAR,
                status VARCHAR,
                petitioner VARCHAR,
                respondent VARCHAR,
                truth_score INTEGER,
                justice_score INTEGER,
                legal_credit_score INTEGER,
                urgency_level INTEGER,
                filed_date DATE,
                next_hearing_date TIMESTAMP,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS jurisdictions (
                id VARCHAR PRIMARY KEY,
                code VARCHAR UNIQUE,
                name VARCHAR,
                country_code VARCHAR,
                subdivision_code VARCHAR,
                legal_system VARCHAR,
                timezone VARCHAR,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Indexes for common query patterns
            CREATE INDEX IF NOT EXISTS idx_docs_case ON documents(case_id);
            CREATE INDEX IF NOT EXISTS idx_docs_jurisdiction ON documents(jurisdiction_code);
            CREATE INDEX IF NOT EXISTS idx_docs_relevancy ON documents(relevancy_number);
            CREATE INDEX IF NOT EXISTS idx_docs_processed ON documents(processed_at);
            CREATE INDEX IF NOT EXISTS idx_docs_type ON documents(document_type);
            CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);
            CREATE INDEX IF NOT EXISTS idx_cases_hearing ON cases(next_hearing_date);
            CREATE INDEX IF NOT EXISTS idx_cases_jurisdiction ON cases(jurisdiction_code);
        """)

    def sync_from_supabase(self, full_sync: bool = False) -> SyncStatus:
        """
        Sync data from Supabase to DuckDB.

        Args:
            full_sync: If True, sync all data. If False, only recent changes.

        Returns:
            SyncStatus with sync results
        """
        if not self.supabase:
            return SyncStatus(0, 0, 0, datetime.now().isoformat(), False, "No Supabase client")

        try:
            docs_synced = 0
            cases_synced = 0
            jurisdictions_synced = 0

            # Determine sync window
            if full_sync:
                since = None
            else:
                since = self.last_sync or (datetime.now() - timedelta(hours=1))

            # Sync jurisdictions (always full - they rarely change)
            jurisdictions = self.supabase.table("jurisdictions").select("*").execute().data
            if jurisdictions:
                df = pd.DataFrame(jurisdictions)
                # Clear and reload
                self.conn.execute("DELETE FROM jurisdictions")
                self.conn.execute("INSERT INTO jurisdictions SELECT * FROM df")
                jurisdictions_synced = len(jurisdictions)

            # Sync cases
            case_query = self.supabase.table("cases").select(
                "id,case_number,court_case_number,court_name,jurisdiction_id,"
                "case_type,case_subtype,status,petitioner,respondent,"
                "truth_score,justice_score,legal_credit_score,urgency_level,"
                "filed_date,next_hearing_date,created_at,updated_at"
            )
            if since and not full_sync:
                case_query = case_query.gte("updated_at", since.isoformat())
            cases = case_query.execute().data

            if cases:
                df = pd.DataFrame(cases)
                # Add jurisdiction code via join
                if 'jurisdiction_id' in df.columns:
                    jur_df = pd.DataFrame(jurisdictions) if jurisdictions else pd.DataFrame()
                    if not jur_df.empty:
                        df = df.merge(
                            jur_df[['id', 'code']].rename(columns={'id': 'jurisdiction_id', 'code': 'jurisdiction_code'}),
                            on='jurisdiction_id',
                            how='left'
                        )

                # Convert JSON columns to strings
                for col in ['petitioner', 'respondent']:
                    if col in df.columns:
                        df[col] = df[col].apply(lambda x: str(x) if x else None)

                # Upsert cases
                for _, row in df.iterrows():
                    self.conn.execute("""
                        INSERT OR REPLACE INTO cases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, list(row))
                cases_synced = len(cases)

            # Sync documents
            doc_query = self.supabase.table("legal_documents").select(
                "id,case_id,jurisdiction_id,document_type,date,file_name,original_filename,"
                "summary,relevancy_number,micro_number,macro_number,legal_number,"
                "contains_false_statements,key_quotes,fraud_indicators,perjury_indicators,"
                "api_cost_usd,processed_at,created_at"
            )
            if since and not full_sync:
                doc_query = doc_query.gte("updated_at", since.isoformat())
            docs = doc_query.limit(10000).execute().data

            if docs:
                df = pd.DataFrame(docs)
                # Rename file_name to title if needed
                if 'file_name' in df.columns:
                    df['title'] = df['file_name']
                    df['original_filename'] = df.get('original_filename', df['file_name'])

                # Add case_number and jurisdiction_code via lookups
                cases_df = pd.DataFrame(cases) if cases else pd.DataFrame()
                jur_df = pd.DataFrame(jurisdictions) if jurisdictions else pd.DataFrame()

                if not cases_df.empty and 'case_id' in df.columns:
                    df = df.merge(
                        cases_df[['id', 'case_number']].rename(columns={'id': 'case_id'}),
                        on='case_id',
                        how='left'
                    )
                if not jur_df.empty and 'jurisdiction_id' in df.columns:
                    df = df.merge(
                        jur_df[['id', 'code']].rename(columns={'id': 'jurisdiction_id', 'code': 'jurisdiction_code'}),
                        on='jurisdiction_id',
                        how='left'
                    )

                # Add missing columns
                df['truth_score'] = df.get('truth_score', None)
                df['justice_score'] = df.get('justice_score', None)

                # Convert list columns to strings
                for col in ['key_quotes', 'fraud_indicators', 'perjury_indicators']:
                    if col in df.columns:
                        df[col] = df[col].apply(lambda x: str(x) if x else None)

                # Upsert documents
                self.conn.execute("DELETE FROM documents WHERE id IN (SELECT id FROM df)")
                self.conn.execute("INSERT INTO documents SELECT * FROM df")
                docs_synced = len(docs)

            self.last_sync = datetime.now()

            return SyncStatus(
                documents_synced=docs_synced,
                cases_synced=cases_synced,
                jurisdictions_synced=jurisdictions_synced,
                sync_time=self.last_sync.isoformat(),
                success=True
            )

        except Exception as e:
            return SyncStatus(0, 0, 0, datetime.now().isoformat(), False, str(e))

    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        return self.conn.execute(sql).fetchdf()

    def get_dashboard_stats(self, jurisdiction_filter: Optional[str] = None) -> Dict[str, Any]:
        """Get overall dashboard statistics"""
        where = f"WHERE jurisdiction_code = '{jurisdiction_filter}'" if jurisdiction_filter else ""

        result = self.query(f"""
            SELECT
                COUNT(*) as total_docs,
                COUNT(DISTINCT case_id) as total_cases,
                COALESCE(AVG(relevancy_number), 0) as avg_relevancy,
                COUNT(*) FILTER (WHERE relevancy_number >= 900) as smoking_guns,
                COUNT(*) FILTER (WHERE contains_false_statements = true) as perjury_docs,
                COALESCE(SUM(api_cost_usd), 0) as total_api_cost,
                COUNT(*) FILTER (WHERE processed_at >= CURRENT_DATE - INTERVAL '7 days') as new_this_week
            FROM documents
            {where}
        """)

        if result.empty:
            return {
                "total_docs": 0,
                "total_cases": 0,
                "avg_relevancy": 0,
                "smoking_guns": 0,
                "perjury_docs": 0,
                "total_api_cost": 0,
                "new_this_week": 0
            }

        return result.iloc[0].to_dict()

    def get_documents_by_jurisdiction(self) -> pd.DataFrame:
        """Get document counts by jurisdiction"""
        return self.query("""
            SELECT
                COALESCE(jurisdiction_code, 'Unknown') as jurisdiction_code,
                COUNT(*) as count
            FROM documents
            GROUP BY jurisdiction_code
            ORDER BY count DESC
        """)

    def get_score_distribution(self) -> pd.DataFrame:
        """Get document score distribution"""
        return self.query("""
            SELECT
                CASE
                    WHEN relevancy_number >= 900 THEN '900+ (Smoking Gun)'
                    WHEN relevancy_number >= 800 THEN '800-899 (Critical)'
                    WHEN relevancy_number >= 700 THEN '700-799 (Important)'
                    WHEN relevancy_number >= 600 THEN '600-699 (Useful)'
                    WHEN relevancy_number IS NOT NULL THEN 'Below 600'
                    ELSE 'Unscored'
                END as category,
                COUNT(*) as count
            FROM documents
            GROUP BY category
            ORDER BY
                CASE category
                    WHEN '900+ (Smoking Gun)' THEN 1
                    WHEN '800-899 (Critical)' THEN 2
                    WHEN '700-799 (Important)' THEN 3
                    WHEN '600-699 (Useful)' THEN 4
                    WHEN 'Below 600' THEN 5
                    ELSE 6
                END
        """)

    def get_processing_timeline(self, days: int = 30) -> pd.DataFrame:
        """Get document processing timeline"""
        return self.query(f"""
            SELECT
                DATE_TRUNC('day', processed_at) as date,
                COUNT(*) as documents,
                AVG(relevancy_number) as avg_score
            FROM documents
            WHERE processed_at >= CURRENT_DATE - INTERVAL '{days} days'
            GROUP BY date
            ORDER BY date
        """)

    def get_case_summary(self, case_id: str) -> Dict[str, Any]:
        """Get comprehensive case summary"""
        result = self.query(f"""
            SELECT
                c.case_number,
                c.court_case_number,
                c.case_type,
                c.status,
                c.truth_score,
                c.justice_score,
                c.legal_credit_score,
                c.jurisdiction_code as jurisdiction,
                COUNT(d.id) as total_documents,
                AVG(d.relevancy_number) as avg_relevancy,
                COUNT(d.id) FILTER (WHERE d.relevancy_number >= 900) as smoking_guns,
                COUNT(d.id) FILTER (WHERE d.contains_false_statements) as perjury_docs,
                SUM(d.api_cost_usd) as total_api_cost
            FROM cases c
            LEFT JOIN documents d ON d.case_id = c.id
            WHERE c.id = '{case_id}'
            GROUP BY c.id
        """)

        if result.empty:
            return {}
        return result.iloc[0].to_dict()

    def get_cross_jurisdiction_analysis(self) -> pd.DataFrame:
        """Analyze patterns across jurisdictions"""
        return self.query("""
            SELECT
                j.code as jurisdiction,
                j.country_code,
                COUNT(DISTINCT c.id) as cases,
                COUNT(d.id) as documents,
                AVG(d.relevancy_number) as avg_relevancy,
                AVG(c.truth_score) as avg_truth_score,
                AVG(c.justice_score) as avg_justice_score,
                COUNT(d.id) FILTER (WHERE d.relevancy_number >= 900) as smoking_guns,
                COUNT(d.id) FILTER (WHERE d.contains_false_statements) as perjury_docs
            FROM jurisdictions j
            LEFT JOIN cases c ON c.jurisdiction_code = j.code
            LEFT JOIN documents d ON d.case_id = c.id
            GROUP BY j.id, j.code, j.country_code
            ORDER BY documents DESC
        """)

    def get_smoking_guns(
        self,
        case_id: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        limit: int = 50
    ) -> pd.DataFrame:
        """Get smoking gun documents (relevancy >= 900)"""
        filters = ["relevancy_number >= 900"]
        if case_id:
            filters.append(f"case_id = '{case_id}'")
        if jurisdiction:
            filters.append(f"jurisdiction_code = '{jurisdiction}'")

        where = " AND ".join(filters)

        return self.query(f"""
            SELECT
                title,
                document_type,
                date,
                relevancy_number,
                summary,
                key_quotes,
                case_number,
                jurisdiction_code
            FROM documents
            WHERE {where}
            ORDER BY relevancy_number DESC
            LIMIT {limit}
        """)

    def get_perjury_evidence(
        self,
        case_id: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        limit: int = 50
    ) -> pd.DataFrame:
        """Get documents with perjury indicators"""
        filters = ["contains_false_statements = true"]
        if case_id:
            filters.append(f"case_id = '{case_id}'")
        if jurisdiction:
            filters.append(f"jurisdiction_code = '{jurisdiction}'")

        where = " AND ".join(filters)

        return self.query(f"""
            SELECT
                title,
                date,
                perjury_indicators,
                fraud_indicators,
                key_quotes,
                case_number,
                jurisdiction_code
            FROM documents
            WHERE {where}
            ORDER BY date DESC
            LIMIT {limit}
        """)

    def search_documents(
        self,
        query: str,
        case_id: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        doc_type: Optional[str] = None,
        min_score: int = 0,
        max_score: int = 1000,
        limit: int = 100
    ) -> pd.DataFrame:
        """Search documents with filters"""
        filters = [
            f"relevancy_number BETWEEN {min_score} AND {max_score}",
            f"(title ILIKE '%{query}%' OR summary ILIKE '%{query}%')"
        ]

        if case_id:
            filters.append(f"case_id = '{case_id}'")
        if jurisdiction:
            filters.append(f"jurisdiction_code = '{jurisdiction}'")
        if doc_type:
            filters.append(f"document_type = '{doc_type}'")

        where = " AND ".join(filters)

        return self.query(f"""
            SELECT
                id,
                title,
                original_filename,
                document_type,
                date,
                relevancy_number,
                micro_number,
                macro_number,
                legal_number,
                summary,
                case_number,
                jurisdiction_code,
                contains_false_statements
            FROM documents
            WHERE {where}
            ORDER BY relevancy_number DESC
            LIMIT {limit}
        """)

    def _start_background_sync(self, interval_minutes: int):
        """Start background sync thread"""
        def sync_job():
            while not self._stop_sync.is_set():
                try:
                    self.sync_from_supabase()
                except Exception as e:
                    print(f"Background sync error: {e}")
                self._stop_sync.wait(interval_minutes * 60)

        self.sync_thread = threading.Thread(target=sync_job, daemon=True)
        self.sync_thread.start()

    def stop_sync(self):
        """Stop background sync thread"""
        self._stop_sync.set()
        if self.sync_thread:
            self.sync_thread.join(timeout=5)

    def close(self):
        """Close database connection"""
        self.stop_sync()
        self.conn.close()


# Convenience function to create engine with Supabase
def create_analytics_engine(
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    db_path: str = "analytics.duckdb"
) -> DuckDBAnalyticsEngine:
    """
    Create analytics engine with Supabase connection.

    Args:
        supabase_url: Supabase URL (defaults to env var)
        supabase_key: Supabase API key (defaults to env var)
        db_path: Path to DuckDB database

    Returns:
        Configured DuckDBAnalyticsEngine
    """
    from supabase import create_client

    url = supabase_url or os.environ.get("SUPABASE_URL")
    key = supabase_key or os.environ.get("SUPABASE_KEY")

    if not url or not key:
        # Return engine without Supabase for local-only analytics
        return DuckDBAnalyticsEngine(db_path=db_path, supabase_client=None, auto_sync=False)

    supabase = create_client(url, key)
    return DuckDBAnalyticsEngine(db_path=db_path, supabase_client=supabase)
