"""
PROJ344 Bridge Module
Provides READ-ONLY access to PROJ344 systems

SAFETY FEATURES:
- Read-only queries (no INSERT, UPDATE, DELETE)
- Independent error handling (failures don't affect PROJ344)
- Shared Supabase connection (same credentials)
- No modifications to PROJ344 code or tables
"""
from supabase import create_client
from typing import List, Dict, Any, Optional
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PROJ344Bridge:
    """
    Safe bridge to PROJ344 legal document intelligence system
    """

    def __init__(self):
        """Initialize Supabase client with shared credentials"""
        try:
            self.supabase = create_client(
                os.environ['SUPABASE_URL'],
                os.environ['SUPABASE_KEY']
            )
            logger.info("✅ PROJ344 Bridge initialized")
        except KeyError as e:
            logger.error(f"❌ Missing environment variable: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to initialize PROJ344 Bridge: {e}")
            raise

    # ========================================================================
    # DOCUMENT QUERIES (legal_documents table)
    # ========================================================================

    async def get_smoking_guns(self, min_relevancy: int = 900) -> Dict[str, Any]:
        """
        Get smoking gun documents (high relevancy)

        Args:
            min_relevancy: Minimum relevancy score (default 900)

        Returns:
            Dict with 'data' key containing list of documents
        """
        try:
            logger.info(f"Querying smoking guns (relevancy >= {min_relevancy})")

            response = self.supabase.table('legal_documents')\
                .select('*')\
                .gte('relevancy_number', min_relevancy)\
                .order('relevancy_number', desc=True)\
                .execute()

            logger.info(f"Found {len(response.data)} smoking gun documents")
            return {
                "count": len(response.data),
                "data": response.data,
                "query": f"relevancy >= {min_relevancy}"
            }

        except Exception as e:
            logger.error(f"Error fetching smoking guns: {e}")
            return {"count": 0, "data": [], "error": str(e)}

    async def get_documents_by_score_range(
        self,
        min_score: int,
        max_score: int = 999
    ) -> Dict[str, Any]:
        """
        Get documents within a specific score range

        Args:
            min_score: Minimum relevancy score
            max_score: Maximum relevancy score (default 999)

        Returns:
            Dict with document data
        """
        try:
            logger.info(f"Querying documents (score {min_score}-{max_score})")

            response = self.supabase.table('legal_documents')\
                .select('*')\
                .gte('relevancy_number', min_score)\
                .lte('relevancy_number', max_score)\
                .order('relevancy_number', desc=True)\
                .execute()

            return {
                "count": len(response.data),
                "data": response.data,
                "score_range": {"min": min_score, "max": max_score}
            }

        except Exception as e:
            logger.error(f"Error fetching documents by score: {e}")
            return {"count": 0, "data": [], "error": str(e)}

    async def get_perjury_indicators(self) -> Dict[str, Any]:
        """
        Get documents with perjury indicators

        Returns:
            Dict with documents flagged for perjury
        """
        try:
            logger.info("Querying documents with perjury indicators")

            response = self.supabase.table('legal_documents')\
                .select('*')\
                .eq('contains_false_statements', True)\
                .order('relevancy_number', desc=True)\
                .execute()

            return {
                "count": len(response.data),
                "data": response.data,
                "indicator": "perjury"
            }

        except Exception as e:
            logger.error(f"Error fetching perjury indicators: {e}")
            return {"count": 0, "data": [], "error": str(e)}

    async def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific document by ID

        Args:
            doc_id: Document UUID

        Returns:
            Document data or None if not found
        """
        try:
            logger.info(f"Querying document ID: {doc_id}")

            response = self.supabase.table('legal_documents')\
                .select('*')\
                .eq('id', doc_id)\
                .execute()

            if response.data:
                return response.data[0]
            else:
                logger.warning(f"Document not found: {doc_id}")
                return None

        except Exception as e:
            logger.error(f"Error fetching document {doc_id}: {e}")
            return None

    async def search_documents(
        self,
        query: str,
        field: str = 'summary'
    ) -> Dict[str, Any]:
        """
        Search documents by text query

        Args:
            query: Search text
            field: Field to search in (summary, key_quotes, etc.)

        Returns:
            Dict with matching documents
        """
        try:
            logger.info(f"Searching documents: '{query}' in '{field}'")

            # Simple text search (can be enhanced with full-text search)
            response = self.supabase.table('legal_documents')\
                .select('*')\
                .ilike(field, f'%{query}%')\
                .order('relevancy_number', desc=True)\
                .execute()

            return {
                "count": len(response.data),
                "data": response.data,
                "query": query,
                "field": field
            }

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return {"count": 0, "data": [], "error": str(e)}

    # ========================================================================
    # VIOLATIONS QUERIES (legal_violations table)
    # ========================================================================

    async def get_violations(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get legal violations

        Args:
            category: Filter by violation category (optional)

        Returns:
            Dict with violations data
        """
        try:
            logger.info(f"Querying violations (category: {category or 'all'})")

            query = self.supabase.table('legal_violations').select('*')

            if category:
                query = query.eq('violation_category', category)

            response = query.order('severity_score', desc=True).execute()

            return {
                "count": len(response.data),
                "data": response.data,
                "category": category or "all"
            }

        except Exception as e:
            logger.error(f"Error fetching violations: {e}")
            return {"count": 0, "data": [], "error": str(e)}

    # ========================================================================
    # STATISTICS & SUMMARIES
    # ========================================================================

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get high-level statistics for dashboard display

        Returns:
            Dict with key metrics
        """
        try:
            logger.info("Generating dashboard statistics")

            # Total documents
            all_docs = self.supabase.table('legal_documents')\
                .select('id')\
                .execute()

            # Smoking guns
            smoking_guns = self.supabase.table('legal_documents')\
                .select('id')\
                .gte('relevancy_number', 900)\
                .execute()

            # Perjury indicators
            perjury_docs = self.supabase.table('legal_documents')\
                .select('id')\
                .eq('contains_false_statements', True)\
                .execute()

            # Violations
            violations = self.supabase.table('legal_violations')\
                .select('id')\
                .execute()

            return {
                "total_documents": len(all_docs.data),
                "smoking_guns": len(smoking_guns.data),
                "perjury_indicators": len(perjury_docs.data),
                "violations_detected": len(violations.data),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating statistics: {e}")
            return {
                "total_documents": 0,
                "smoking_guns": 0,
                "perjury_indicators": 0,
                "violations_detected": 0,
                "error": str(e)
            }

    async def get_recent_documents(
        self,
        limit: int = 10,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get recently processed documents

        Args:
            limit: Maximum number of documents to return
            days: Number of days to look back

        Returns:
            Dict with recent documents
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            logger.info(f"Querying recent documents (last {days} days, limit {limit})")

            response = self.supabase.table('legal_documents')\
                .select('*')\
                .gte('processed_at', cutoff_date)\
                .order('processed_at', desc=True)\
                .limit(limit)\
                .execute()

            return {
                "count": len(response.data),
                "data": response.data,
                "period_days": days,
                "limit": limit
            }

        except Exception as e:
            logger.error(f"Error fetching recent documents: {e}")
            return {"count": 0, "data": [], "error": str(e)}

    # ========================================================================
    # HEALTH CHECK
    # ========================================================================

    async def health_check(self) -> bool:
        """
        Check if PROJ344 bridge is healthy

        Returns:
            True if connection is working, False otherwise
        """
        try:
            # Simple query to verify connection
            self.supabase.table('legal_documents')\
                .select('id')\
                .limit(1)\
                .execute()

            logger.info("✅ PROJ344 Bridge health check passed")
            return True

        except Exception as e:
            logger.error(f"❌ PROJ344 Bridge health check failed: {e}")
            return False


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    """
    Test the PROJ344 Bridge module
    Requires SUPABASE_URL and SUPABASE_KEY environment variables
    """
    import asyncio

    async def test_bridge():
        bridge = PROJ344Bridge()

        # Test health check
        print("\n1. Health Check:")
        healthy = await bridge.health_check()
        print(f"   Status: {'✅ Healthy' if healthy else '❌ Unhealthy'}")

        # Test statistics
        print("\n2. Dashboard Statistics:")
        stats = await bridge.get_dashboard_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")

        # Test smoking guns query
        print("\n3. Smoking Guns (relevancy >= 900):")
        smoking_guns = await bridge.get_smoking_guns()
        print(f"   Found: {smoking_guns['count']} documents")

        # Test violations
        print("\n4. Legal Violations:")
        violations = await bridge.get_violations()
        print(f"   Found: {violations['count']} violations")

    # Run async test
    asyncio.run(test_bridge())
