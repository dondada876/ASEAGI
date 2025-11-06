#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Manager for Supabase State Preservation
Handles saving/loading dashboard states, caching, and context preservation
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from supabase import create_client, Client
import pandas as pd

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

class ContextManager:
    """Manages context preservation and caching in Supabase"""

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize ContextManager

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
        """
        # Get credentials
        self.url = supabase_url or os.environ.get(
            'SUPABASE_URL',
            'https://jvjlhxodmbkodzmggwpu.supabase.co'
        )
        self.key = supabase_key or os.environ.get(
            'SUPABASE_KEY',
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c'
        )

        self.client: Client = create_client(self.url, self.key)

    # =========================================================================
    # CACHING METHODS
    # =========================================================================

    def get_cache(self, cache_key: str, cache_type: str = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached data

        Args:
            cache_key: Unique cache identifier
            cache_type: Optional type filter

        Returns:
            Cached result data or None if not found/expired
        """
        try:
            query = self.client.table('system_processing_cache')\
                .select('*')\
                .eq('cache_key', cache_key)

            if cache_type:
                query = query.eq('cache_type', cache_type)

            response = query.execute()

            # Check if we got any data
            if response.data and len(response.data) > 0:
                cache_entry = response.data[0]

                # Check expiration
                if cache_entry.get('expires_at'):
                    from datetime import timezone
                    expires_at_str = cache_entry['expires_at']
                    # Handle both with and without timezone
                    if 'Z' in expires_at_str or '+' in expires_at_str:
                        expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                        now = datetime.now(timezone.utc)
                    else:
                        expires_at = datetime.fromisoformat(expires_at_str)
                        now = datetime.now()

                    if now > expires_at:
                        return None

                # Increment hit count
                self._increment_cache_hit(cache_key)

                return cache_entry['result_data']

            return None

        except Exception as e:
            import traceback
            print(f"Cache retrieval error: {e}")
            print(traceback.format_exc())
            return None

    def set_cache(
        self,
        cache_key: str,
        cache_type: str,
        result_data: Dict[str, Any],
        input_params: Dict[str, Any] = None,
        expires_in_hours: int = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Store data in cache

        Args:
            cache_key: Unique cache identifier
            cache_type: Type of cache ('document_analysis', 'timeline_build', etc.)
            result_data: The data to cache
            input_params: Input parameters that generated this result
            expires_in_hours: Hours until expiration (None = never expires)
            metadata: Additional metadata

        Returns:
            True if successful
        """
        try:
            # Calculate input hash
            input_hash = self._hash_dict(input_params) if input_params else hashlib.sha256(b'').hexdigest()

            # Calculate expiration
            expires_at = None
            if expires_in_hours:
                from datetime import timezone
                expires_at = (datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)).isoformat()

            cache_data = {
                'cache_key': cache_key,
                'cache_type': cache_type,
                'input_hash': input_hash,
                'result_data': result_data,
                'metadata': metadata or {},
                'expires_at': expires_at,
                'hit_count': 0
            }

            # Upsert (insert or update)
            self.client.table('system_processing_cache')\
                .upsert(cache_data)\
                .execute()

            return True

        except Exception as e:
            print(f"Cache storage error: {e}")
            return False

    def _increment_cache_hit(self, cache_key: str):
        """Increment cache hit counter"""
        try:
            self.client.rpc('increment_cache_hit', {'p_cache_key': cache_key}).execute()
        except:
            pass  # Non-critical

    # =========================================================================
    # DASHBOARD SNAPSHOT METHODS
    # =========================================================================

    def save_dashboard_snapshot(
        self,
        dashboard_name: str,
        snapshot_data: Dict[str, Any],
        snapshot_name: str = None,
        filters_applied: Dict[str, Any] = None,
        metrics: Dict[str, Any] = None,
        auto_snapshot: bool = False,
        notes: str = None
    ) -> Optional[str]:
        """
        Save a complete dashboard state snapshot

        Args:
            dashboard_name: Name of the dashboard
            snapshot_data: Complete dashboard state
            snapshot_name: User-friendly name
            filters_applied: Active filters
            metrics: Summary metrics
            auto_snapshot: Whether this is an auto-generated snapshot
            notes: User notes

        Returns:
            Snapshot ID if successful
        """
        try:
            # Count rows in snapshot
            row_count = len(snapshot_data.get('data', []))

            snapshot = {
                'dashboard_name': dashboard_name,
                'snapshot_name': snapshot_name or f"{dashboard_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'snapshot_data': snapshot_data,
                'filters_applied': filters_applied or {},
                'metrics': metrics or {},
                'row_count': row_count,
                'is_auto_snapshot': auto_snapshot,
                'notes': notes
            }

            response = self.client.table('dashboard_snapshots')\
                .insert(snapshot)\
                .execute()

            if response.data:
                return response.data[0]['id']

            return None

        except Exception as e:
            print(f"Snapshot save error: {e}")
            return None

    def load_dashboard_snapshot(
        self,
        snapshot_id: str = None,
        dashboard_name: str = None,
        latest: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Load a dashboard snapshot

        Args:
            snapshot_id: Specific snapshot ID to load
            dashboard_name: Dashboard name (if loading latest)
            latest: Whether to load most recent snapshot

        Returns:
            Snapshot data or None
        """
        try:
            if snapshot_id:
                response = self.client.table('dashboard_snapshots')\
                    .select('*')\
                    .eq('id', snapshot_id)\
                    .single()\
                    .execute()
            elif dashboard_name and latest:
                response = self.client.table('dashboard_snapshots')\
                    .select('*')\
                    .eq('dashboard_name', dashboard_name)\
                    .order('snapshot_date', desc=True)\
                    .limit(1)\
                    .execute()

                if response.data:
                    response.data = response.data[0]
            else:
                return None

            return response.data if response.data else None

        except Exception as e:
            print(f"Snapshot load error: {e}")
            return None

    def list_snapshots(
        self,
        dashboard_name: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        List available snapshots

        Args:
            dashboard_name: Filter by dashboard name
            limit: Maximum number to return

        Returns:
            List of snapshot metadata
        """
        try:
            query = self.client.table('dashboard_snapshots')\
                .select('id, dashboard_name, snapshot_name, snapshot_date, row_count, is_auto_snapshot')

            if dashboard_name:
                query = query.eq('dashboard_name', dashboard_name)

            response = query.order('snapshot_date', desc=True)\
                .limit(limit)\
                .execute()

            return response.data if response.data else []

        except Exception as e:
            print(f"Snapshot list error: {e}")
            return []

    # =========================================================================
    # TRUTH SCORE METHODS
    # =========================================================================

    def save_truth_scores(
        self,
        truth_scores: List[Dict[str, Any]]
    ) -> bool:
        """
        Save truth scores to history

        Args:
            truth_scores: List of truth score records

        Returns:
            True if successful
        """
        try:
            self.client.table('truth_score_history')\
                .insert(truth_scores)\
                .execute()

            return True

        except Exception as e:
            print(f"Truth score save error: {e}")
            return False

    def get_truth_scores(
        self,
        item_id: str = None,
        item_type: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        min_score: float = None,
        max_score: float = None
    ) -> List[Dict[str, Any]]:
        """
        Query truth scores

        Args:
            item_id: Filter by item ID
            item_type: Filter by item type
            date_from: Start date
            date_to: End date
            min_score: Minimum truth score
            max_score: Maximum truth score

        Returns:
            List of truth score records
        """
        try:
            query = self.client.table('truth_score_history').select('*')

            if item_id:
                query = query.eq('item_id', item_id)
            if item_type:
                query = query.eq('item_type', item_type)
            if date_from:
                query = query.gte('when_happened', date_from.isoformat())
            if date_to:
                query = query.lte('when_happened', date_to.isoformat())
            if min_score is not None:
                query = query.gte('truth_score', min_score)
            if max_score is not None:
                query = query.lte('truth_score', max_score)

            response = query.order('calculated_at', desc=True).execute()

            return response.data if response.data else []

        except Exception as e:
            print(f"Truth score query error: {e}")
            return []

    # =========================================================================
    # JUSTICE SCORE METHODS
    # =========================================================================

    def save_justice_score_rollup(
        self,
        rollup_name: str,
        justice_score: float,
        score_breakdown: Dict[str, Any],
        items_included: List[str],
        date_range_start: datetime = None,
        date_range_end: datetime = None,
        filters_applied: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Save a justice score rollup

        Args:
            rollup_name: Name for this rollup
            justice_score: Overall justice score
            score_breakdown: Detailed breakdown
            items_included: List of item IDs included
            date_range_start: Start of date range
            date_range_end: End of date range
            filters_applied: Filters used

        Returns:
            Rollup ID if successful
        """
        try:
            rollup_data = {
                'rollup_name': rollup_name,
                'rollup_date': datetime.now().isoformat(),
                'justice_score': justice_score,
                'total_items': len(items_included),
                'score_breakdown': score_breakdown,
                'items_included': items_included,
                'date_range_start': date_range_start.isoformat() if date_range_start else None,
                'date_range_end': date_range_end.isoformat() if date_range_end else None,
                'filters_applied': filters_applied or {}
            }

            # Extract counts from breakdown
            rollup_data.update({
                'critical_items': score_breakdown.get('critical_items', 0),
                'high_items': score_breakdown.get('high_items', 0),
                'medium_items': score_breakdown.get('medium_items', 0),
                'low_items': score_breakdown.get('low_items', 0),
                'avg_truth_score': score_breakdown.get('avg_truth_score', 0),
                'truthful_items': score_breakdown.get('truthful_items', 0),
                'neutral_items': score_breakdown.get('neutral_items', 0),
                'false_items': score_breakdown.get('false_items', 0)
            })

            response = self.client.table('justice_score_rollups')\
                .insert(rollup_data)\
                .execute()

            if response.data:
                return response.data[0]['id']

            return None

        except Exception as e:
            print(f"Justice score save error: {e}")
            return None

    # =========================================================================
    # AI ANALYSIS TRACKING
    # =========================================================================

    def log_ai_analysis(
        self,
        analysis_type: str,
        model_name: str,
        prompt_text: str,
        response_text: str,
        structured_output: Dict[str, Any] = None,
        source_id: str = None,
        source_table: str = None,
        confidence_score: float = None,
        tokens_used: int = None,
        processing_time_ms: int = None,
        api_cost_usd: float = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Log an AI analysis result

        Args:
            analysis_type: Type of analysis
            model_name: AI model used
            prompt_text: Prompt sent to AI
            response_text: AI response
            structured_output: Parsed response
            source_id: Source record ID
            source_table: Source table name
            confidence_score: Confidence in result
            tokens_used: Token count
            processing_time_ms: Processing time
            api_cost_usd: API cost
            metadata: Additional metadata

        Returns:
            True if successful
        """
        try:
            analysis_data = {
                'analysis_type': analysis_type,
                'model_name': model_name,
                'prompt_text': prompt_text,
                'response_text': response_text,
                'structured_output': structured_output or {},
                'source_id': source_id,
                'source_table': source_table,
                'confidence_score': confidence_score,
                'tokens_used': tokens_used,
                'processing_time_ms': processing_time_ms,
                'api_cost_usd': api_cost_usd,
                'metadata': metadata or {}
            }

            self.client.table('ai_analysis_results')\
                .insert(analysis_data)\
                .execute()

            return True

        except Exception as e:
            print(f"AI analysis log error: {e}")
            return False

    # =========================================================================
    # PROCESSING JOBS
    # =========================================================================

    def create_processing_job(
        self,
        job_type: str,
        job_name: str,
        items_total: int
    ) -> Optional[str]:
        """
        Create a new processing job

        Args:
            job_type: Type of job
            job_name: Job name
            items_total: Total items to process

        Returns:
            Job ID if successful
        """
        try:
            job_data = {
                'job_type': job_type,
                'job_name': job_name,
                'status': 'pending',
                'items_total': items_total,
                'started_at': datetime.now().isoformat()
            }

            response = self.client.table('processing_jobs_log')\
                .insert(job_data)\
                .execute()

            if response.data:
                return response.data[0]['id']

            return None

        except Exception as e:
            print(f"Job creation error: {e}")
            return None

    def update_processing_job(
        self,
        job_id: str,
        status: str = None,
        items_processed: int = None,
        items_failed: int = None,
        progress_percentage: int = None,
        error_message: str = None,
        result_summary: Dict[str, Any] = None
    ) -> bool:
        """
        Update a processing job

        Args:
            job_id: Job ID
            status: New status
            items_processed: Number processed
            items_failed: Number failed
            progress_percentage: Progress percentage
            error_message: Error message if failed
            result_summary: Result summary

        Returns:
            True if successful
        """
        try:
            update_data = {'updated_at': datetime.now().isoformat()}

            if status:
                update_data['status'] = status
                if status == 'completed':
                    update_data['completed_at'] = datetime.now().isoformat()

            if items_processed is not None:
                update_data['items_processed'] = items_processed
            if items_failed is not None:
                update_data['items_failed'] = items_failed
            if progress_percentage is not None:
                update_data['progress_percentage'] = progress_percentage
            if error_message:
                update_data['error_message'] = error_message
            if result_summary:
                update_data['result_summary'] = result_summary

            self.client.table('processing_jobs_log')\
                .update(update_data)\
                .eq('id', job_id)\
                .execute()

            return True

        except Exception as e:
            print(f"Job update error: {e}")
            return False

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _hash_dict(self, data: Dict[str, Any]) -> str:
        """Create SHA256 hash of dictionary"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def clean_expired_caches(self) -> int:
        """Clean up expired cache entries"""
        try:
            response = self.client.rpc('clean_expired_cache').execute()
            return response.data if response.data else 0
        except Exception as e:
            print(f"Cache cleanup error: {e}")
            return 0


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize
    cm = ContextManager()

    print("Context Manager initialized")
    print(f"Connected to: {cm.url}")

    # Example: Save a cache entry
    print("\n1. Testing cache...")
    cache_key = "test_timeline_2024_11_05"
    result = cm.set_cache(
        cache_key=cache_key,
        cache_type="timeline_build",
        result_data={"events": 10, "documents": 50},
        expires_in_hours=24,
        metadata={"filters": {"date_range": "2024-01-01 to 2024-12-31"}}
    )
    print(f"Cache set: {result}")

    # Retrieve cache
    cached_data = cm.get_cache(cache_key)
    print(f"Cache retrieved: {cached_data}")

    # Example: List snapshots
    print("\n2. Listing recent snapshots...")
    snapshots = cm.list_snapshots(limit=5)
    print(f"Found {len(snapshots)} snapshots")
    for snap in snapshots:
        print(f"  - {snap['snapshot_name']} ({snap['dashboard_name']}) - {snap['row_count']} rows")

    print("\n✅ Context Manager ready for use!")
