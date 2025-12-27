-- ============================================================================
-- Migration: 001_jurisdiction_agnostic_schema.sql
-- Purpose: Create jurisdiction-agnostic case management schema
-- Date: 2025-12-26
-- ============================================================================

-- ============================================================================
-- STEP 1: Create Jurisdictions Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS jurisdictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,        -- 'US-CA', 'US-NY', 'UK-ENG', 'CA-ON'
    name VARCHAR(255) NOT NULL,              -- 'California, United States'
    country_code CHAR(2) NOT NULL,           -- ISO 3166-1 alpha-2
    subdivision_code VARCHAR(10),            -- ISO 3166-2 subdivision
    legal_system VARCHAR(50),                -- 'common_law', 'civil_law', 'mixed'
    court_hierarchy JSONB,                   -- Nested court structure
    statute_codes JSONB,                     -- Available code systems
    filing_rules JSONB,                      -- Deadline rules per case type
    date_formats JSONB,                      -- {'filing': 'MM/DD/YYYY', 'display': 'MMMM D, YYYY'}
    timezone VARCHAR(50),                    -- 'America/Los_Angeles'
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for jurisdictions
CREATE INDEX IF NOT EXISTS idx_jurisdictions_country ON jurisdictions(country_code);
CREATE INDEX IF NOT EXISTS idx_jurisdictions_code ON jurisdictions(code);

-- ============================================================================
-- STEP 2: Create Cases Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number VARCHAR(50) UNIQUE,           -- Auto-generated: US-CA-2025-00001
    jurisdiction_id UUID REFERENCES jurisdictions(id),
    court_type VARCHAR(20),                   -- 'FAMILY', 'JUVENILE', 'CRIMINAL', 'APPELLATE', 'FEDERAL'
    court_case_number VARCHAR(100),           -- Official court number: J24-00478
    court_name VARCHAR(255),                  -- 'Santa Clara County Superior Court'
    case_type VARCHAR(50),                    -- Legacy: 'family', 'civil', 'criminal', 'probate'
    case_subtype VARCHAR(100),                -- 'custody', 'dependency', 'felony', 'habeas'
    status VARCHAR(30) DEFAULT 'active',      -- 'active', 'closed', 'appealed', 'stayed'

    -- Parties (JSONB for flexibility across jurisdictions)
    petitioner JSONB,                         -- {"name": "...", "type": "individual/entity"}
    respondent JSONB,
    children JSONB,                           -- Array of minor children involved
    attorneys JSONB,                          -- {"petitioner": [...], "respondent": [...]}

    -- Key Dates
    filed_date DATE,
    opened_date DATE DEFAULT CURRENT_DATE,    -- When added to system
    closed_date DATE,
    next_hearing_date TIMESTAMPTZ,

    -- Scoring (PROJ344 methodology)
    truth_score INTEGER DEFAULT 0,            -- 0-1000
    justice_score INTEGER DEFAULT 0,          -- 0-1000
    legal_credit_score INTEGER DEFAULT 0,     -- 0-850
    urgency_level INTEGER DEFAULT 5,          -- 1-10

    -- Metadata
    tags TEXT[],
    notes TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID
);

-- Indexes for cases
CREATE INDEX IF NOT EXISTS idx_cases_jurisdiction ON cases(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);
CREATE INDEX IF NOT EXISTS idx_cases_type ON cases(case_type);
CREATE INDEX IF NOT EXISTS idx_cases_court_number ON cases(court_case_number);
CREATE INDEX IF NOT EXISTS idx_cases_next_hearing ON cases(next_hearing_date) WHERE status = 'active';

-- ============================================================================
-- STEP 3: Auto-generate case numbers function
-- ============================================================================

CREATE OR REPLACE FUNCTION generate_case_number()
RETURNS TRIGGER AS $$
DECLARE
    jurisdiction_code VARCHAR(20);
    year_part VARCHAR(4);
    sequence_num INTEGER;
    new_case_number VARCHAR(50);
BEGIN
    -- Get jurisdiction code
    SELECT code INTO jurisdiction_code
    FROM jurisdictions WHERE id = NEW.jurisdiction_id;

    -- Get current year
    year_part := TO_CHAR(NOW(), 'YYYY');

    -- Get next sequence for this jurisdiction/year
    SELECT COALESCE(MAX(
        CAST(SPLIT_PART(case_number, '-', 4) AS INTEGER)
    ), 0) + 1 INTO sequence_num
    FROM cases
    WHERE jurisdiction_id = NEW.jurisdiction_id
    AND case_number LIKE jurisdiction_code || '-' || year_part || '-%';

    -- Generate case number: US-CA-2025-00001
    new_case_number := jurisdiction_code || '-' || year_part || '-' || LPAD(sequence_num::TEXT, 5, '0');
    NEW.case_number := new_case_number;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for auto-generating case numbers
DROP TRIGGER IF EXISTS trg_generate_case_number ON cases;
CREATE TRIGGER trg_generate_case_number
BEFORE INSERT ON cases
FOR EACH ROW
WHEN (NEW.case_number IS NULL)
EXECUTE FUNCTION generate_case_number();

-- ============================================================================
-- STEP 4: Add case_id and jurisdiction_id to legal_documents
-- ============================================================================

-- Add columns if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'legal_documents' AND column_name = 'case_id') THEN
        ALTER TABLE legal_documents ADD COLUMN case_id UUID REFERENCES cases(id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'legal_documents' AND column_name = 'jurisdiction_id') THEN
        ALTER TABLE legal_documents ADD COLUMN jurisdiction_id UUID REFERENCES jurisdictions(id);
    END IF;
END $$;

-- Create indexes for the new columns
CREATE INDEX IF NOT EXISTS idx_legal_documents_case ON legal_documents(case_id);
CREATE INDEX IF NOT EXISTS idx_legal_documents_jurisdiction ON legal_documents(jurisdiction_id);

-- ============================================================================
-- STEP 5: Insert initial jurisdictions (Geographic)
-- ============================================================================

INSERT INTO jurisdictions (code, name, country_code, subdivision_code, legal_system, court_hierarchy, statute_codes, filing_rules, timezone)
VALUES
-- California
('US-CA', 'California, United States', 'US', 'CA', 'common_law',
 '{"supreme": "Supreme Court of California", "appellate": "Court of Appeal", "trial": "Superior Court", "family": "Family Division", "juvenile": "Juvenile Division"}'::jsonb,
 '{"family": "Family Code", "welfare": "Welfare and Institutions Code", "civil": "Code of Civil Procedure", "penal": "Penal Code"}'::jsonb,
 '{"motion": {"days_before_hearing": 16, "opposition": 9, "reply": 5}, "ex_parte": {"notice": 24}}'::jsonb,
 'America/Los_Angeles'),

-- New York
('US-NY', 'New York, United States', 'US', 'NY', 'common_law',
 '{"supreme": "Court of Appeals", "appellate": "Appellate Division", "trial": "Supreme Court", "family": "Family Court", "juvenile": "Family Court"}'::jsonb,
 '{"domestic": "Domestic Relations Law", "family": "Family Court Act", "civil": "CPLR", "juvenile": "Family Court Act Article 3"}'::jsonb,
 '{"motion": {"days_before_hearing": 8, "opposition": 5, "reply": 2}}'::jsonb,
 'America/New_York'),

-- Texas
('US-TX', 'Texas, United States', 'US', 'TX', 'common_law',
 '{"supreme": "Supreme Court of Texas", "appellate": "Court of Appeals", "trial": "District Court", "family": "Family District Court", "juvenile": "Juvenile Court"}'::jsonb,
 '{"family": "Texas Family Code", "juvenile": "Texas Family Code Title 3", "civil": "Texas Civil Practice and Remedies Code"}'::jsonb,
 '{"motion": {"days_before_hearing": 21, "opposition": 7}}'::jsonb,
 'America/Chicago'),

-- Federal (US)
('US-FED', 'United States Federal Courts', 'US', NULL, 'common_law',
 '{"supreme": "Supreme Court of the United States", "appellate": "Circuit Courts of Appeals", "trial": "District Courts", "bankruptcy": "Bankruptcy Courts"}'::jsonb,
 '{"civil": "Federal Rules of Civil Procedure", "criminal": "Federal Rules of Criminal Procedure", "appellate": "Federal Rules of Appellate Procedure", "evidence": "Federal Rules of Evidence"}'::jsonb,
 '{"motion": {"days_before_hearing": 14, "opposition": 14, "reply": 7}}'::jsonb,
 'America/New_York')

ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- STEP 5B: Create Court Types Table (Subject Matter Jurisdiction)
-- ============================================================================

CREATE TABLE IF NOT EXISTS court_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,           -- 'FAMILY', 'JUVENILE', 'CRIMINAL', 'APPELLATE', 'FEDERAL'
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_court_type VARCHAR(20),              -- For appellate hierarchy
    case_subtypes JSONB,                        -- Array of valid case subtypes
    applicable_statutes JSONB,                  -- Key statutes per jurisdiction
    procedural_rules JSONB,                     -- Procedure rules reference
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert court types focused on user's needs
INSERT INTO court_types (code, name, description, parent_court_type, case_subtypes, applicable_statutes, procedural_rules)
VALUES
-- Family Court
('FAMILY', 'Family Court', 'Handles divorce, custody, support, domestic violence, paternity', NULL,
 '["custody", "divorce", "child_support", "spousal_support", "domestic_violence", "paternity", "adoption", "guardianship", "modification", "contempt"]'::jsonb,
 '{
   "US-CA": {"primary": "Family Code", "sections": ["3000-3465", "6200-6389", "7600-7730"]},
   "US-NY": {"primary": "Domestic Relations Law", "family_court_act": "Article 4-8"},
   "US-TX": {"primary": "Texas Family Code", "titles": [1, 2, 4, 5]}
 }'::jsonb,
 '{
   "US-CA": "California Rules of Court - Family Rules",
   "US-NY": "Uniform Rules for Family Court",
   "US-TX": "Texas Rules of Civil Procedure - Family Law"
 }'::jsonb),

-- Juvenile Court
('JUVENILE', 'Juvenile Court', 'Handles dependency, delinquency, status offenses, foster care', NULL,
 '["dependency", "delinquency", "status_offense", "foster_care", "termination_parental_rights", "emancipation", "truancy", "curfew", "runaway"]'::jsonb,
 '{
   "US-CA": {"primary": "Welfare and Institutions Code", "sections": ["200-304", "300-395", "450-465", "600-778", "601-607"]},
   "US-NY": {"primary": "Family Court Act", "articles": ["3", "7", "10"]},
   "US-TX": {"primary": "Texas Family Code Title 3", "chapters": ["51-61"]}
 }'::jsonb,
 '{
   "US-CA": "California Rules of Court - Juvenile Rules (5.500-5.906)",
   "US-NY": "Uniform Rules for Family Court - Juvenile Delinquency/Dependency",
   "US-TX": "Texas Juvenile Justice Code"
 }'::jsonb),

-- Criminal Court
('CRIMINAL', 'Criminal Court', 'Handles felonies, misdemeanors, infractions, sentencing', NULL,
 '["felony", "misdemeanor", "infraction", "probation_violation", "parole_violation", "sentencing", "plea", "trial", "preliminary_hearing", "grand_jury"]'::jsonb,
 '{
   "US-CA": {"primary": "Penal Code", "evidence": "Evidence Code", "procedure": "Penal Code Part 2"},
   "US-NY": {"primary": "Penal Law", "procedure": "Criminal Procedure Law"},
   "US-TX": {"primary": "Texas Penal Code", "procedure": "Texas Code of Criminal Procedure"},
   "US-FED": {"primary": "Title 18 USC", "procedure": "Federal Rules of Criminal Procedure"}
 }'::jsonb,
 '{
   "US-CA": "California Rules of Court - Criminal Rules",
   "US-NY": "Uniform Rules for Criminal Terms",
   "US-TX": "Texas Rules of Appellate Procedure",
   "US-FED": "Federal Rules of Criminal Procedure"
 }'::jsonb),

-- Appellate Court
('APPELLATE', 'Appellate Court', 'Reviews lower court decisions, constitutional issues, legal errors', 'CRIMINAL',
 '["direct_appeal", "interlocutory_appeal", "writ_habeas_corpus", "writ_mandamus", "writ_certiorari", "petition_review", "en_banc", "rehearing"]'::jsonb,
 '{
   "US-CA": {"primary": "Code of Civil Procedure 901-923", "rules": "California Rules of Court Title 8"},
   "US-NY": {"primary": "CPLR Article 55-57", "rules": "Appellate Division Rules"},
   "US-TX": {"primary": "Texas Rules of Appellate Procedure"},
   "US-FED": {"primary": "Federal Rules of Appellate Procedure", "circuits": "Circuit-specific rules"}
 }'::jsonb,
 '{
   "US-CA": "California Rules of Court - Appellate Rules (8.1-8.1125)",
   "US-NY": "Rules of Appellate Division",
   "US-TX": "Texas Rules of Appellate Procedure",
   "US-FED": "Federal Rules of Appellate Procedure + Circuit Rules"
 }'::jsonb),

-- Federal Court
('FEDERAL', 'Federal Court', 'Federal question jurisdiction, diversity, constitutional rights, civil rights', NULL,
 '["civil_rights", "constitutional", "federal_question", "diversity", "habeas_corpus", "1983_claim", "immigration", "bankruptcy", "patent", "antitrust"]'::jsonb,
 '{
   "US-FED": {
     "civil_rights": "42 USC 1983, 1985",
     "habeas": "28 USC 2241-2255",
     "civil": "Federal Rules of Civil Procedure",
     "jurisdiction": "28 USC 1331, 1332"
   }
 }'::jsonb,
 '{
   "US-FED": "Federal Rules of Civil Procedure + Local Rules"
 }'::jsonb)

ON CONFLICT (code) DO NOTHING;

-- Create index
CREATE INDEX IF NOT EXISTS idx_court_types_code ON court_types(code);

-- ============================================================================
-- STEP 6: Create initial case from existing J24-00478 data
-- ============================================================================

-- Insert the existing case
INSERT INTO cases (
    jurisdiction_id,
    court_type,
    court_case_number,
    court_name,
    case_type,
    case_subtype,
    status,
    petitioner,
    respondent,
    filed_date,
    notes
)
SELECT
    (SELECT id FROM jurisdictions WHERE code = 'US-CA'),
    'JUVENILE',  -- Dependency cases are in Juvenile Court
    'J24-00478',
    'Santa Clara County Superior Court - Juvenile Division',
    'juvenile',
    'dependency',
    'active',
    '{"name": "County of Santa Clara Department of Family and Children Services", "type": "entity", "role": "petitioner"}'::jsonb,
    '{"name": "Parents", "type": "individual", "role": "respondent"}'::jsonb,
    '2024-01-01',
    'In re Ashe Bucknor (J24-00478) - WIC 300 Dependency Proceeding - Migrated from legacy system'
WHERE NOT EXISTS (
    SELECT 1 FROM cases WHERE court_case_number = 'J24-00478'
);

-- Link existing documents to the case
UPDATE legal_documents
SET
    case_id = (SELECT id FROM cases WHERE court_case_number = 'J24-00478'),
    jurisdiction_id = (SELECT id FROM jurisdictions WHERE code = 'US-CA')
WHERE case_id IS NULL;

-- ============================================================================
-- STEP 7: Create updated_at trigger for all tables
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to jurisdictions
DROP TRIGGER IF EXISTS update_jurisdictions_updated_at ON jurisdictions;
CREATE TRIGGER update_jurisdictions_updated_at
BEFORE UPDATE ON jurisdictions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to cases
DROP TRIGGER IF EXISTS update_cases_updated_at ON cases;
CREATE TRIGGER update_cases_updated_at
BEFORE UPDATE ON cases
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- STEP 8: Create view for case dashboard
-- ============================================================================

CREATE OR REPLACE VIEW v_case_dashboard AS
SELECT
    c.id,
    c.case_number,
    c.court_case_number,
    c.court_name,
    c.case_type,
    c.case_subtype,
    c.status,
    c.petitioner,
    c.respondent,
    c.filed_date,
    c.next_hearing_date,
    c.truth_score,
    c.justice_score,
    c.legal_credit_score,
    c.urgency_level,
    c.tags,
    c.created_at,
    c.updated_at,
    j.code AS jurisdiction_code,
    j.name AS jurisdiction_name,
    j.country_code,
    j.timezone,
    COALESCE(doc_stats.document_count, 0) AS document_count,
    COALESCE(doc_stats.smoking_gun_count, 0) AS smoking_gun_count,
    COALESCE(doc_stats.avg_relevancy, 0) AS avg_relevancy,
    COALESCE(doc_stats.unprocessed_count, 0) AS unprocessed_count
FROM cases c
LEFT JOIN jurisdictions j ON c.jurisdiction_id = j.id
LEFT JOIN LATERAL (
    SELECT
        COUNT(*) AS document_count,
        COUNT(*) FILTER (WHERE relevancy_number >= 900) AS smoking_gun_count,
        AVG(relevancy_number) AS avg_relevancy,
        COUNT(*) FILTER (WHERE relevancy_number IS NULL) AS unprocessed_count
    FROM legal_documents d
    WHERE d.case_id = c.id
) doc_stats ON true;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Run these after migration to verify:
-- SELECT * FROM jurisdictions;
-- SELECT * FROM cases;
-- SELECT * FROM v_case_dashboard;
-- SELECT COUNT(*) FROM legal_documents WHERE case_id IS NOT NULL;
