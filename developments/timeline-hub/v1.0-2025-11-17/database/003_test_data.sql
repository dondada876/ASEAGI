-- ============================================================================
-- TIMELINE HUB - TEST DATA SCRIPT
-- ============================================================================
--
-- Purpose: Insert sample data to verify timeline hub isolation
-- Use Case: Testing, demonstration, development
--
-- This script inserts realistic test data without requiring any external
-- tables (legal_documents, bugs, etc.) to prove complete isolation.
--
-- ============================================================================

-- ============================================================================
-- TEST DATA SET: August 2024 Custody Case Scenario
-- ============================================================================

-- Test Case: Mother-Father Text Message Exchange
-- Date Range: 2024-08-01 to 2024-08-07
-- Purpose: Demonstrate communication tracking and timeline building

-- ============================================================================
-- 1. INSERT TEST EVENTS
-- ============================================================================

-- Event 1: Good Cause Report Issued
INSERT INTO timeline_events (
    event_type,
    event_date,
    event_time,
    event_title,
    event_description,
    participants,
    sender,
    recipients,
    message_full_text,
    source_type,
    source_file_path,
    importance,
    keywords,
    case_number,
    created_by
) VALUES (
    'COURT_ORDER',
    '2024-08-07',
    '14:30:00',
    'Good Cause Report Issued',
    'Court issued Good Cause Report authorizing lawful retention of minor child due to safety concerns.',
    ARRAY['JUD', 'FAT', 'MOT', 'MIN'],
    NULL,
    NULL,
    NULL,
    'COURT_DOCUMENT',
    '/test/documents/good_cause_report_2024-08-07.pdf',
    950,  -- Smoking gun importance
    ARRAY['good cause', 'retention', 'lawful', 'safety'],
    'J24-00478',
    'test_data_script'
);

-- Event 2: Mother's Text Message After Report
INSERT INTO timeline_events (
    event_type,
    event_date,
    event_time,
    event_title,
    event_description,
    participants,
    sender,
    recipients,
    message_full_text,
    source_type,
    source_file_path,
    importance,
    keywords,
    case_number,
    created_by
) VALUES (
    'TEXT_MESSAGE',
    '2024-08-08',
    '09:15:23',
    'Text: Mother requests child return',
    'Mother sent text message demanding immediate return of child, claiming father is violating court orders.',
    ARRAY['MOT', 'FAT'],
    'MOT',
    ARRAY['FAT'],
    'You need to return Ashe immediately. You are violating the court order. I will call the police.',
    'SCREENSHOT',
    '/test/screenshots/text_2024-08-08_0915.jpg',
    850,
    ARRAY['violation', 'police', 'return', 'court order'],
    'J24-00478',
    'test_data_script'
);

-- Event 3: Father's Response
INSERT INTO timeline_events (
    event_type,
    event_date,
    event_time,
    event_title,
    event_description,
    participants,
    sender,
    recipients,
    message_full_text,
    source_type,
    source_file_path,
    importance,
    keywords,
    case_number,
    created_by
) VALUES (
    'TEXT_MESSAGE',
    '2024-08-08',
    '09:22:45',
    'Text: Father cites Good Cause Report',
    'Father responds citing the Good Cause Report issued yesterday as legal authority for retention.',
    ARRAY['FAT', 'MOT'],
    'FAT',
    ARRAY['MOT'],
    'The court issued a Good Cause Report yesterday authorizing me to keep Ashe for her safety. I am following the court order.',
    'SCREENSHOT',
    '/test/screenshots/text_2024-08-08_0922.jpg',
    900,
    ARRAY['good cause', 'safety', 'court order', 'legal'],
    'J24-00478',
    'test_data_script'
);

-- Event 4: Court Hearing Scheduled
INSERT INTO timeline_events (
    event_type,
    event_date,
    event_time,
    event_title,
    event_description,
    participants,
    sender,
    recipients,
    message_full_text,
    source_type,
    source_file_path,
    importance,
    keywords,
    case_number,
    created_by
) VALUES (
    'COURT_HEARING',
    '2024-08-12',
    '10:00:00',
    'Dependency Hearing - Detention Review',
    'Scheduled hearing to review detention and Good Cause Report. All parties ordered to appear.',
    ARRAY['JUD', 'FAT', 'MOT', 'MIN', 'ATT_FAT', 'ATT_MOT', 'ATT_MIN', 'CPS'],
    NULL,
    NULL,
    NULL,
    'COURT_CALENDAR',
    '/test/documents/hearing_notice_2024-08-12.pdf',
    975,
    ARRAY['hearing', 'detention', 'review', 'parties'],
    'J24-00478',
    'test_data_script'
);

-- Event 5: Declaration Filed by Mother
INSERT INTO timeline_events (
    event_type,
    event_date,
    event_time,
    event_title,
    event_description,
    participants,
    sender,
    recipients,
    message_full_text,
    source_type,
    source_file_path,
    importance,
    keywords,
    contains_false_statement,
    case_number,
    created_by
) VALUES (
    'DECLARATION_FILED',
    '2024-08-12',
    '08:30:00',
    'Mother files declaration claiming Jamaica flight plan',
    'Mother files sworn declaration claiming she was terrified father would take child to Jamaica, contradicting previous communications showing no such concern.',
    ARRAY['MOT', 'ATT_MOT'],
    'MOT',
    ARRAY['JUD'],
    'I was terrified that Don would use this Good Cause Report to take Ashe to Jamaica without my permission...',
    'COURT_FILING',
    '/test/documents/mothers_declaration_2024-08-12.pdf',
    990,  -- Critical - potential perjury
    ARRAY['jamaica', 'flight', 'terrified', 'false statement'],
    TRUE,  -- Flagged as containing false statement
    'J24-00478',
    'test_data_script'
);

-- ============================================================================
-- 2. INSERT TEST COMMUNICATIONS
-- ============================================================================

-- Communication 1: Text from Event 2
INSERT INTO timeline_communications (
    comm_type,
    comm_date,
    comm_time,
    sender,
    recipients,
    subject,
    message_body,
    thread_id,
    contains_admission,
    contains_threat,
    contains_false_statement,
    admission_text,
    source_screenshot_path,
    importance
) VALUES (
    'TEXT_MESSAGE',
    '2024-08-08',
    '09:15:23',
    'MOT',
    ARRAY['FAT'],
    NULL,
    'You need to return Ashe immediately. You are violating the court order. I will call the police.',
    'thread-2024-08-08-custody',
    FALSE,
    TRUE,  -- Threat to call police
    TRUE,  -- False claim of violation (Good Cause Report authorized retention)
    ARRAY['I will call the police'],
    '/test/screenshots/text_2024-08-08_0915.jpg',
    850
);

-- Communication 2: Text from Event 3
INSERT INTO timeline_communications (
    comm_type,
    comm_date,
    comm_time,
    sender,
    recipients,
    subject,
    message_body,
    thread_id,
    contains_admission,
    contains_threat,
    contains_false_statement,
    admission_text,
    source_screenshot_path,
    importance
) VALUES (
    'TEXT_MESSAGE',
    '2024-08-08',
    '09:22:45',
    'FAT',
    ARRAY['MOT'],
    NULL,
    'The court issued a Good Cause Report yesterday authorizing me to keep Ashe for her safety. I am following the court order.',
    'thread-2024-08-08-custody',
    FALSE,
    FALSE,
    FALSE,
    ARRAY[]::TEXT[],
    '/test/screenshots/text_2024-08-08_0922.jpg',
    900
);

-- Communication 3: Email from Mother to Attorney
INSERT INTO timeline_communications (
    comm_type,
    comm_date,
    comm_time,
    sender,
    recipients,
    subject,
    message_body,
    thread_id,
    contains_admission,
    contains_threat,
    contains_false_statement,
    admission_text,
    source_screenshot_path,
    importance
) VALUES (
    'EMAIL',
    '2024-08-09',
    '14:22:00',
    'MOT',
    ARRAY['ATT_MOT'],
    'Urgent: Don has Ashe',
    'My attorney - Don is refusing to return Ashe. He claims he has some "Good Cause Report" but I don''t believe it''s real. Can we file an emergency motion?',
    'email-thread-attorney-2024-08',
    TRUE,  -- Admission she was aware of Good Cause Report
    FALSE,
    FALSE,
    ARRAY['I don''t believe it''s real'],
    '/test/screenshots/email_2024-08-09.png',
    825
);

-- ============================================================================
-- 3. INSERT TEST RELATIONSHIPS
-- ============================================================================

-- Relationship 1: Good Cause Report → Father's Retention
INSERT INTO timeline_relationships (
    event_id_1,
    event_id_2,
    relationship_type,
    strength,
    description,
    legal_significance,
    created_by
)
SELECT
    (SELECT id FROM timeline_events WHERE event_title = 'Good Cause Report Issued'),
    (SELECT id FROM timeline_events WHERE event_title = 'Text: Father cites Good Cause Report'),
    'CAUSES',
    950,
    'Good Cause Report legally authorizes father''s retention of child, directly referenced in his text message response.',
    'Establishes legal basis for retention, contradicting mother''s claim of violation.',
    'test_data_script';

-- Relationship 2: Mother's Email → Declaration
INSERT INTO timeline_relationships (
    event_id_1,
    event_id_2,
    relationship_type,
    strength,
    description,
    legal_significance,
    created_by
)
SELECT
    (SELECT id FROM timeline_communications WHERE message_body LIKE '%Good Cause Report%' AND sender = 'MOT'),
    (SELECT id FROM timeline_events WHERE event_title LIKE '%Jamaica flight plan%'),
    'CONTRADICTS',
    975,
    'Mother''s email on Aug 9 shows awareness of Good Cause Report, contradicting her later sworn declaration claiming fear of Jamaica flight.',
    'Demonstrates prior knowledge, undermining credibility of Jamaica claim in sworn declaration.',
    'test_data_script';

-- Relationship 3: Timeline Gap Detection
INSERT INTO timeline_relationships (
    event_id_1,
    event_id_2,
    relationship_type,
    strength,
    description,
    legal_significance,
    created_by
)
SELECT
    (SELECT id FROM timeline_events WHERE event_title = 'Text: Mother requests child return'),
    (SELECT id FROM timeline_events WHERE event_title = 'Mother files declaration claiming Jamaica flight plan'),
    'TIMELINE_GAP',
    850,
    'No mentions of Jamaica concerns in communications from Aug 8-11, but suddenly appears in Aug 12 declaration.',
    'Absence of Jamaica concern in contemporaneous communications suggests fabrication.',
    'test_data_script';

-- ============================================================================
-- 4. INSERT TEST TIMELINE PHASES
-- ============================================================================

-- Phase 1: Pre-Detention Period
INSERT INTO timeline_phases (
    phase_name,
    phase_description,
    start_date,
    end_date,
    significance,
    key_events_count,
    created_by
)
SELECT
    'Pre-Detention - Normal Custody',
    'Period before Good Cause Report when child was with mother under existing custody order.',
    '2024-05-01',
    '2024-08-06',
    'Baseline period showing normal communication patterns and no Jamaica concerns.',
    COUNT(*)
FROM timeline_events
WHERE event_date < '2024-08-07',
'test_data_script';

-- Phase 2: Detention Period
INSERT INTO timeline_phases (
    phase_name,
    phase_description,
    start_date,
    end_date,
    significance,
    key_events_count,
    created_by
)
SELECT
    'Post-Good Cause Report - Lawful Detention',
    'Period after Good Cause Report when father lawfully retained child for safety.',
    '2024-08-07',
    '2024-08-12',
    'Critical period showing lawful retention and mother''s evolving narrative.',
    COUNT(*)
FROM timeline_events
WHERE event_date BETWEEN '2024-08-07' AND '2024-08-12',
'test_data_script';

-- ============================================================================
-- 5. VERIFICATION QUERIES
-- ============================================================================

-- Query 1: Verify events were inserted
DO $$
DECLARE
    event_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO event_count FROM timeline_events WHERE created_by = 'test_data_script';
    RAISE NOTICE 'Test Events Inserted: %', event_count;

    IF event_count = 5 THEN
        RAISE NOTICE '✅ All 5 test events inserted successfully';
    ELSE
        RAISE WARNING '⚠️ Expected 5 events, found %', event_count;
    END IF;
END $$;

-- Query 2: Verify communications were inserted
DO $$
DECLARE
    comm_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO comm_count FROM timeline_communications WHERE sender IN ('MOT', 'FAT');
    RAISE NOTICE 'Test Communications Inserted: %', comm_count;

    IF comm_count = 3 THEN
        RAISE NOTICE '✅ All 3 test communications inserted successfully';
    ELSE
        RAISE WARNING '⚠️ Expected 3 communications, found %', comm_count;
    END IF;
END $$;

-- Query 3: Verify relationships were created
DO $$
DECLARE
    rel_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO rel_count FROM timeline_relationships WHERE created_by = 'test_data_script';
    RAISE NOTICE 'Test Relationships Inserted: %', rel_count;

    IF rel_count = 3 THEN
        RAISE NOTICE '✅ All 3 test relationships inserted successfully';
    ELSE
        RAISE WARNING '⚠️ Expected 3 relationships, found %', rel_count;
    END IF;
END $$;

-- Query 4: Verify phases were created
DO $$
DECLARE
    phase_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO phase_count FROM timeline_phases WHERE created_by = 'test_data_script';
    RAISE NOTICE 'Test Phases Inserted: %', phase_count;

    IF phase_count = 2 THEN
        RAISE NOTICE '✅ All 2 test phases inserted successfully';
    ELSE
        RAISE WARNING '⚠️ Expected 2 phases, found %', phase_count;
    END IF;
END $$;

-- Final Success Message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '════════════════════════════════════════════════════════════';
    RAISE NOTICE '✅ TEST DATA INSERTION COMPLETE';
    RAISE NOTICE '════════════════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE 'You can now test timeline hub functionality with realistic data.';
    RAISE NOTICE '';
    RAISE NOTICE 'Next Steps:';
    RAISE NOTICE '  1. Run verification queries (004_verify_isolation.sql)';
    RAISE NOTICE '  2. Test timeline queries from README.md';
    RAISE NOTICE '  3. Launch Telegram bot to view timeline';
    RAISE NOTICE '  4. Test search functionality';
    RAISE NOTICE '';
END $$;
