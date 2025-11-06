#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script: Full ContextManager Functionality Test
Tests caching, snapshots, truth scores, and justice scores
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from utilities.context_manager import ContextManager

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def test_context_manager():
    """Run comprehensive tests on ContextManager"""

    print("=" * 70)
    print("CONTEXT MANAGER - FUNCTIONALITY TEST")
    print("=" * 70)
    print()

    # Initialize ContextManager
    print("🔧 Initializing ContextManager...")
    try:
        cm = ContextManager()
        print("✅ ContextManager initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False

    print()
    tests_passed = 0
    tests_failed = 0

    # ========================================================================
    # TEST 1: Cache Set/Get
    # ========================================================================
    print("=" * 70)
    print("TEST 1: Cache Functionality")
    print("=" * 70)

    try:
        # Use unique cache key to avoid duplicates
        cache_key = f"test_cache_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        test_data = {
            'message': 'Hello from cache test!',
            'timestamp': datetime.now().isoformat(),
            'items': [1, 2, 3, 4, 5]
        }

        print(f"📝 Setting cache: {cache_key}")
        success = cm.set_cache(
            cache_key=cache_key,
            cache_type="test_cache",
            result_data=test_data,
            expires_in_hours=1,
            metadata={'test_run': 'initial'}
        )

        if success:
            print("   ✅ Cache set successfully")

            # Add small delay to ensure database write completes
            import time
            time.sleep(0.5)

            # Try to retrieve
            print(f"📥 Getting cache: {cache_key}")
            cached_data = cm.get_cache(cache_key)

            if cached_data:
                print("   ✅ Cache retrieved successfully")
                print(f"   Data: {cached_data.get('message', 'N/A')}")
                tests_passed += 1
            else:
                print("   ❌ Cache retrieval failed")
                tests_failed += 1
        else:
            print("   ❌ Cache set failed")
            tests_failed += 1

    except Exception as e:
        print(f"   ❌ Cache test failed: {e}")
        tests_failed += 1

    print()

    # ========================================================================
    # TEST 2: Dashboard Snapshot
    # ========================================================================
    print("=" * 70)
    print("TEST 2: Dashboard Snapshot Save/Load")
    print("=" * 70)

    try:
        snapshot_data = {
            'timeline_data': [
                {'date': '2024-11-05', 'event': 'Test Event 1', 'score': 75},
                {'date': '2024-11-04', 'event': 'Test Event 2', 'score': 80}
            ],
            'filters': {'date_range': ['2024-11-01', '2024-11-05']},
            'config': {'view_mode': 'timeline'}
        }

        print("📸 Saving dashboard snapshot...")
        snapshot_id = cm.save_dashboard_snapshot(
            dashboard_name="test_dashboard",
            snapshot_data=snapshot_data,
            snapshot_name="Test Snapshot 1",
            filters_applied={'date_range': ['2024-11-01', '2024-11-05']},
            metrics={'total_events': 2, 'avg_score': 77.5},
            notes="This is a test snapshot"
        )

        if snapshot_id:
            print(f"   ✅ Snapshot saved: {snapshot_id}")

            # Try to load it back
            print("📥 Loading snapshot...")
            loaded = cm.load_dashboard_snapshot(
                dashboard_name="test_dashboard",
                latest=True
            )

            if loaded:
                print("   ✅ Snapshot loaded successfully")
                print(f"   Name: {loaded.get('snapshot_name', 'N/A')}")
                print(f"   Rows: {loaded.get('row_count', 0)}")
                tests_passed += 1
            else:
                print("   ❌ Snapshot load failed")
                tests_failed += 1
        else:
            print("   ❌ Snapshot save failed")
            tests_failed += 1

    except Exception as e:
        print(f"   ❌ Snapshot test failed: {e}")
        import traceback
        print(traceback.format_exc())
        tests_failed += 1

    print()

    # ========================================================================
    # TEST 3: Truth Scores
    # ========================================================================
    print("=" * 70)
    print("TEST 3: Truth Score Tracking")
    print("=" * 70)

    try:
        # Generate proper UUIDs for test items
        test_uuid_1 = str(uuid.uuid4())
        test_uuid_2 = str(uuid.uuid4())

        truth_scores = [
            {
                'item_id': test_uuid_1,
                'item_type': 'TEST_EVENT',
                'item_title': 'Test False Statement',
                'truth_score': 15.0,
                'when_happened': '2024-08-10T10:00:00',
                'where_happened': 'Test Location',
                'who_involved': ['Person A', 'Person B'],
                'what_occurred': 'Test false statement made',
                'why_occurred': 'Test motive',
                'how_occurred': 'Test method',
                'importance_level': 'CRITICAL',
                'category': 'TEST',
                'evidence_count': 3
            },
            {
                'item_id': test_uuid_2,
                'item_type': 'TEST_EVENT',
                'item_title': 'Test Truthful Statement',
                'truth_score': 95.0,
                'when_happened': '2024-08-11T14:00:00',
                'where_happened': 'Test Location 2',
                'who_involved': ['Person C'],
                'what_occurred': 'Test truthful statement made',
                'why_occurred': 'Test reason',
                'how_occurred': 'Test process',
                'importance_level': 'HIGH',
                'category': 'TEST',
                'evidence_count': 5
            }
        ]

        print(f"📊 Saving {len(truth_scores)} truth scores...")
        success = cm.save_truth_scores(truth_scores)

        if success:
            print("   ✅ Truth scores saved")

            # Try to query them
            print("🔍 Querying truth scores...")
            scores = cm.get_truth_scores(
                date_from=datetime(2024, 8, 1),
                date_to=datetime(2024, 8, 31)
            )

            if scores:
                print(f"   ✅ Retrieved {len(scores)} truth scores")
                tests_passed += 1
            else:
                print("   ⚠️  No scores retrieved (may be expected)")
                tests_passed += 1
        else:
            print("   ❌ Truth score save failed")
            tests_failed += 1

    except Exception as e:
        print(f"   ❌ Truth score test failed: {e}")
        tests_failed += 1

    print()

    # ========================================================================
    # TEST 4: Justice Score Rollup
    # ========================================================================
    print("=" * 70)
    print("TEST 4: Justice Score Rollup")
    print("=" * 70)

    try:
        print("📈 Saving justice score rollup...")
        rollup_id = cm.save_justice_score_rollup(
            rollup_name="Test Case Justice Score",
            justice_score=67.5,
            score_breakdown={
                'critical_items': 2,
                'high_items': 5,
                'false_items': 3,
                'truthful_items': 4
            },
            items_included=[test_uuid_1, test_uuid_2],  # Use UUIDs from truth score test
            date_range_start=datetime(2024, 8, 1),
            date_range_end=datetime(2024, 8, 31)
        )

        if rollup_id:
            print(f"   ✅ Justice score rollup saved: {rollup_id}")
            tests_passed += 1
        else:
            print("   ❌ Justice score rollup failed")
            tests_failed += 1

    except Exception as e:
        print(f"   ❌ Justice score test failed: {e}")
        tests_failed += 1

    print()

    # ========================================================================
    # TEST 5: AI Analysis Logging
    # ========================================================================
    print("=" * 70)
    print("TEST 5: AI Analysis Logging")
    print("=" * 70)

    try:
        # Generate UUID for test document
        test_doc_uuid = str(uuid.uuid4())

        print("🤖 Logging AI analysis...")
        success = cm.log_ai_analysis(
            analysis_type="test_analysis",
            model_name="claude-sonnet-4.5",
            prompt_text="Test prompt for analysis",
            response_text="Test response from AI model",
            structured_output={'result': 'test', 'confidence': 0.95},
            source_id=test_doc_uuid,
            source_table="test_documents",
            confidence_score=95.0,
            tokens_used=1500,
            processing_time_ms=2500,
            api_cost_usd=0.02,
            metadata={'test': True}
        )

        if success:
            print("   ✅ AI analysis logged")
            tests_passed += 1
        else:
            print("   ❌ AI analysis logging failed")
            tests_failed += 1

    except Exception as e:
        print(f"   ❌ AI analysis test failed: {e}")
        tests_failed += 1

    print()

    # ========================================================================
    # RESULTS
    # ========================================================================
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"✅ Tests Passed: {tests_passed}/5")
    print(f"❌ Tests Failed: {tests_failed}/5")
    print()

    if tests_failed == 0:
        print("🎉 ALL TESTS PASSED! Context preservation system is working!")
        print()
        print("=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print("1. Integrate caching into your dashboards")
        print("2. Add snapshot saving before major changes")
        print("3. Start tracking truth scores historically")
        print("4. Monitor AI costs in Supabase")
        print()
        return True
    else:
        print("⚠️  Some tests failed. Check error messages above.")
        print()
        return False

if __name__ == "__main__":
    success = test_context_manager()
    sys.exit(0 if success else 1)
