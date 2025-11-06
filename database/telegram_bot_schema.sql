-- ============================================================================
-- ASEAGI Database Schema for Telegram Bot
-- Case: In re Ashe B., J24-00478
-- ============================================================================
--
-- This SQL creates all tables needed for the Telegram bot to function.
-- Run this in your Supabase SQL Editor.
--
-- Tables Created:
--   1. communications - Text messages, emails, calls
--   2. events - Case timeline events
--   3. action_items - Pending tasks and deadlines
--   4. violations - Legal violations detected
--   5. hearings - Court hearings
--   6. document_journal - Case documents
--
-- For Ashe. For Justice. For All Children. 🛡️
-- ============================================================================

-- ============================================================================
-- 1. COMMUNICATIONS TABLE
-- Stores all communications (texts, emails, calls)
-- ============================================================================

CREATE TABLE IF NOT EXISTS communications (
    communication_id SERIAL PRIMARY KEY,
    sender VARCHAR(255) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    communication_type VARCHAR(50) DEFAULT 'text', -- text, email, call
    sent_date TIMESTAMP NOT NULL,
    content TEXT NOT NULL,
    truthfulness_score DECIMAL(3,2), -- 0.00 to 1.00
    contains_contradiction BOOLEAN DEFAULT FALSE,
    contradiction_details JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for faster searches
CREATE INDEX IF NOT EXISTS idx_communications_sender ON communications(sender);
CREATE INDEX IF NOT EXISTS idx_communications_date ON communications(sent_date DESC);
CREATE INDEX IF NOT EXISTS idx_communications_content ON communications USING GIN (to_tsvector('english', content));

-- ============================================================================
-- 2. EVENTS TABLE
-- Case timeline events
-- ============================================================================

CREATE TABLE IF NOT EXISTS events (
    event_id SERIAL PRIMARY KEY,
    event_date TIMESTAMP NOT NULL,
    event_type VARCHAR(100) NOT NULL, -- hearing, filing, incident, communication, etc.
    title VARCHAR(500) NOT NULL,
    description TEXT,
    parties_involved JSONB DEFAULT '[]'::jsonb, -- Array of party names
    related_documents JSONB DEFAULT '[]'::jsonb, -- Array of document IDs
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for timeline queries
CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date DESC);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);

-- ============================================================================
-- 3. ACTION ITEMS TABLE
-- Pending tasks and deadlines
-- ============================================================================

CREATE TABLE IF NOT EXISTS action_items (
    action_id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium', -- urgent, high, medium, low
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, cancelled
    due_date DATE,
    assigned_to VARCHAR(255),
    related_hearings JSONB DEFAULT '[]'::jsonb, -- Array of hearing IDs
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Index for action queries
CREATE INDEX IF NOT EXISTS idx_action_items_status ON action_items(status);
CREATE INDEX IF NOT EXISTS idx_action_items_priority ON action_items(priority);
CREATE INDEX IF NOT EXISTS idx_action_items_due_date ON action_items(due_date);

-- ============================================================================
-- 4. VIOLATIONS TABLE
-- Legal violations detected
-- ============================================================================

CREATE TABLE IF NOT EXISTS violations (
    violation_id SERIAL PRIMARY KEY,
    violation_type VARCHAR(100) NOT NULL, -- perjury, fraud, due_process, etc.
    severity VARCHAR(20) DEFAULT 'medium', -- critical, high, medium, low
    description TEXT NOT NULL,
    evidence JSONB DEFAULT '[]'::jsonb, -- Array of evidence items
    related_documents JSONB DEFAULT '[]'::jsonb, -- Array of document IDs
    detected_date TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'active', -- active, resolved, disputed
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for violation queries
CREATE INDEX IF NOT EXISTS idx_violations_severity ON violations(severity);
CREATE INDEX IF NOT EXISTS idx_violations_type ON violations(violation_type);
CREATE INDEX IF NOT EXISTS idx_violations_date ON violations(detected_date DESC);

-- ============================================================================
-- 5. HEARINGS TABLE
-- Court hearings
-- ============================================================================

CREATE TABLE IF NOT EXISTS hearings (
    hearing_id SERIAL PRIMARY KEY,
    hearing_date TIMESTAMP NOT NULL,
    hearing_type VARCHAR(100) NOT NULL, -- detention, review, trial, etc.
    judge_name VARCHAR(255),
    location VARCHAR(500),
    outcome VARCHAR(100), -- pending, continued, ruled, etc.
    notes TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for hearing queries
CREATE INDEX IF NOT EXISTS idx_hearings_date ON hearings(hearing_date);
CREATE INDEX IF NOT EXISTS idx_hearings_type ON hearings(hearing_type);

-- ============================================================================
-- 6. DOCUMENT JOURNAL TABLE
-- Case documents
-- ============================================================================

CREATE TABLE IF NOT EXISTS document_journal (
    journal_id SERIAL PRIMARY KEY,
    original_filename VARCHAR(500) NOT NULL,
    normalized_filename VARCHAR(500),
    document_type VARCHAR(100), -- court_order, motion, evidence, etc.
    date_logged TIMESTAMP DEFAULT NOW(),
    file_path VARCHAR(1000),
    file_size_bytes BIGINT,
    summary TEXT,
    ai_confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for document searches
CREATE INDEX IF NOT EXISTS idx_documents_filename ON document_journal(original_filename);
CREATE INDEX IF NOT EXISTS idx_documents_type ON document_journal(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_date ON document_journal(date_logged DESC);

-- ============================================================================
-- SAMPLE DATA - In re Ashe B., J24-00478
-- ============================================================================

-- Sample Communications
INSERT INTO communications (sender, recipient, communication_type, sent_date, content, truthfulness_score, contains_contradiction) VALUES
('Mother (Shantae Bucknor)', 'Social Worker (Bonnie Turner)', 'text', '2024-01-15 10:30:00', 'I am ready to pick up Ashe at any time. I have been compliant with all court orders.', 0.85, false),
('Social Worker (Bonnie Turner)', 'Mother (Shantae Bucknor)', 'text', '2024-01-15 14:20:00', 'You cannot pick up Ashe until the next hearing. Court order requires supervision.', 0.65, true),
('Father (Don Bucknor)', 'CPS Case Manager', 'email', '2024-02-01 09:15:00', 'Requesting copy of Cal OES 2-925 form showing mother was notified of placement. This form appears to be missing from case file.', 0.95, false);

-- Sample Events
INSERT INTO events (event_date, event_type, title, description, parties_involved) VALUES
('2024-01-05 14:00:00', 'hearing', 'Initial Detention Hearing', 'Court ordered child detained pending investigation. Mother present, father absent.', '["Judge", "Mother", "Social Worker"]'::jsonb),
('2024-02-12 10:00:00', 'hearing', 'Jurisdiction/Disposition Hearing', 'Court found jurisdiction. Mother ordered services. Father still not properly notified.', '["Judge", "Mother", "County Counsel", "Social Worker"]'::jsonb),
('2024-03-01 00:00:00', 'incident', 'Denial of Visitation', 'Mother denied scheduled visitation without explanation or court order.', '["Mother", "Social Worker"]'::jsonb);

-- Sample Action Items
INSERT INTO action_items (title, description, priority, status, due_date) VALUES
('File Motion for Reconsideration', 'Challenge jurisdiction findings based on missing Cal OES 2-925 notice to mother', 'urgent', 'pending', '2024-11-15'),
('Request Missing Documents', 'Obtain copy of initial detention report and all Cal OES forms', 'high', 'pending', '2024-11-10'),
('Prepare for Next Hearing', 'Review case file, prepare witness questions, draft arguments', 'high', 'pending', '2024-11-20'),
('File Complaint Against Social Worker', 'Document pattern of deception and false statements', 'medium', 'pending', '2024-11-30');

-- Sample Violations
INSERT INTO violations (violation_type, severity, description, detected_date) VALUES
('due_process', 'critical', 'Mother (Shantae Bucknor) was never properly notified via Cal OES 2-925 form about child''s placement. This violates WIC 319(b) requirements.', '2024-10-15 00:00:00'),
('perjury', 'critical', 'Social worker Bonnie Turner testified under oath that mother was notified, but Cal OES 2-925 form is missing from case file and mother denies receiving notice.', '2024-10-20 00:00:00'),
('fraud', 'high', 'Social worker claimed mother failed to maintain contact, but text message records show mother consistently reached out and was denied access.', '2024-10-25 00:00:00'),
('denial_of_visitation', 'high', 'Mother denied court-ordered visitation without legal justification or court order authorizing denial.', '2024-03-01 00:00:00');

-- Sample Hearings
INSERT INTO hearings (hearing_date, hearing_type, judge_name, outcome, notes) VALUES
('2024-01-05 14:00:00', 'detention', 'Judge Smith', 'detained', 'Child detained pending investigation. Father not present - alleged improper notice.'),
('2024-02-12 10:00:00', 'jurisdiction_disposition', 'Judge Smith', 'jurisdiction_found', 'Jurisdiction sustained. Questions raised about Cal OES 2-925 notice to mother.'),
('2024-11-25 09:00:00', 'review', 'Judge Smith', 'pending', 'Upcoming 6-month review hearing. Motion for reconsideration pending.');

-- Sample Documents
INSERT INTO document_journal (original_filename, document_type, date_logged, summary, ai_confidence_score) VALUES
('detention_report_2024-01-05.pdf', 'court_order', '2024-01-05', 'Initial detention report alleging neglect. Contains unverified claims.', 0.75),
('jurisdiction_findings_2024-02-12.pdf', 'court_order', '2024-02-12', 'Court findings sustaining jurisdiction under WIC 300(b). Due process concerns noted.', 0.85),
('text_messages_mother_sw.pdf', 'evidence', '2024-10-15', 'Text message thread between mother and social worker showing contradictions in social worker testimony.', 0.95),
('motion_reconsideration.pdf', 'motion', '2024-10-28', 'Motion challenging jurisdiction based on lack of Cal OES 2-925 notice to mother.', 0.90);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - Optional but recommended
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE communications ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE violations ENABLE ROW LEVEL SECURITY;
ALTER TABLE hearings ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_journal ENABLE ROW LEVEL SECURITY;

-- Create policy to allow service role full access
CREATE POLICY "Allow service role full access" ON communications FOR ALL USING (true);
CREATE POLICY "Allow service role full access" ON events FOR ALL USING (true);
CREATE POLICY "Allow service role full access" ON action_items FOR ALL USING (true);
CREATE POLICY "Allow service role full access" ON violations FOR ALL USING (true);
CREATE POLICY "Allow service role full access" ON hearings FOR ALL USING (true);
CREATE POLICY "Allow service role full access" ON document_journal FOR ALL USING (true);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Run these after creating tables to verify everything works:

-- SELECT COUNT(*) FROM communications; -- Should return 3
-- SELECT COUNT(*) FROM events; -- Should return 3
-- SELECT COUNT(*) FROM action_items; -- Should return 4
-- SELECT COUNT(*) FROM violations; -- Should return 4
-- SELECT COUNT(*) FROM hearings; -- Should return 3
-- SELECT COUNT(*) FROM document_journal; -- Should return 4

-- ============================================================================
-- SUCCESS!
-- ============================================================================
--
-- After running this script, your Telegram bot should work perfectly:
--   ✅ /search - Search communications
--   ✅ /timeline - Show case events
--   ✅ /actions - Pending action items
--   ✅ /violations - Legal violations
--   ✅ /hearing - Court hearings
--   ✅ /report - Daily summary
--
-- For Ashe. For Justice. For All Children. 🛡️
-- ============================================================================
