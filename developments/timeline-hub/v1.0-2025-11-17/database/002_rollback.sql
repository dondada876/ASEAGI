-- ============================================================================
-- TIMELINE HUB - ROLLBACK/CLEANUP SCRIPT
-- ============================================================================
--
-- Purpose: Remove all timeline hub tables and data
-- Use Case: Testing, cleanup, fresh install
--
-- WARNING: This will DELETE ALL timeline data!
-- Make sure you have backups if needed.
--
-- ============================================================================

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS timeline_processing_queue CASCADE;
DROP TABLE IF EXISTS timeline_phases CASCADE;
DROP TABLE IF EXISTS timeline_relationships CASCADE;
DROP TABLE IF EXISTS timeline_communications CASCADE;
DROP TABLE IF EXISTS timeline_events CASCADE;
DROP TABLE IF EXISTS timeline_participants CASCADE;
DROP TABLE IF EXISTS timeline_schema_version CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS update_participant_stats(TEXT);
DROP FUNCTION IF EXISTS calculate_time_gap(TIMESTAMP, TIMESTAMP);

-- Verify cleanup
DO $$
BEGIN
    RAISE NOTICE 'Timeline Hub tables dropped successfully';
    RAISE NOTICE 'You can now run 001_create_schema.sql to reinstall';
END $$;
