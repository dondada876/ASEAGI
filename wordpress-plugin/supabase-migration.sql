-- ASEAGI WordPress Connector - Supabase Database Migration
-- Version: 1.0.0
-- Purpose: Create and configure tables for WordPress public storytelling integration
-- For Ashe. For Justice. For All Children. 🛡️

-- =============================================================================
-- CORE TABLES (Extend existing ASEAGI schema)
-- =============================================================================

-- Add WordPress sync fields to existing court_events table (if not present)
ALTER TABLE court_events
ADD COLUMN IF NOT EXISTS synced_to_wordpress BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS wordpress_post_id INTEGER,
ADD COLUMN IF NOT EXISTS public_safe BOOLEAN DEFAULT true;

-- Add WordPress sync fields to existing legal_documents table (if not present)
ALTER TABLE legal_documents
ADD COLUMN IF NOT EXISTS synced_to_wordpress BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS wordpress_post_id INTEGER,
ADD COLUMN IF NOT EXISTS public_safe BOOLEAN DEFAULT true;

-- =============================================================================
-- NEW TABLES FOR WORDPRESS INTEGRATION
-- =============================================================================

-- Resources Table (for ListingPro directory)
CREATE TABLE IF NOT EXISTS resources (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Basic Information
    resource_name TEXT NOT NULL,
    description TEXT,
    resource_type TEXT CHECK (resource_type IN (
        'legal',
        'support',
        'government',
        'community',
        'educational',
        'financial',
        'housing',
        'mental_health'
    )),

    -- Contact Information
    contact_info TEXT,
    contact_name TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    website_url TEXT,

    -- Location
    location TEXT, -- Generalized (e.g., "Berkeley, CA")
    address TEXT, -- More specific but still generalized

    -- Details
    cost TEXT, -- "Free", "Sliding scale", "$50/hour", etc.
    eligibility TEXT,
    hours TEXT,
    languages TEXT[],

    -- Verification
    verified BOOLEAN DEFAULT false,
    verified_date DATE,
    verified_by TEXT,

    -- Rating
    rating NUMERIC(2,1) CHECK (rating >= 0 AND rating <= 5),
    review_count INTEGER DEFAULT 0,

    -- Scoring
    relevancy_score INTEGER CHECK (relevancy_score BETWEEN 0 AND 1000),
    helpfulness_score INTEGER CHECK (helpfulness_score BETWEEN 0 AND 1000),

    -- Privacy & Sync
    public_safe BOOLEAN DEFAULT true,
    synced_to_wordpress BOOLEAN DEFAULT false,
    wordpress_post_id INTEGER,

    -- Metadata
    notes TEXT,
    tags TEXT[]
);

-- Public Timeline Events (filtered copy of court_events for public display)
CREATE TABLE IF NOT EXISTS public_timeline_events (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Event Details
    event_date DATE NOT NULL,
    event_title TEXT NOT NULL,
    event_description TEXT, -- Privacy filtered
    event_category TEXT CHECK (event_category IN (
        'court-hearings',
        'legal-victories',
        'cps-actions',
        'document-filings',
        'milestones',
        'evidence-discoveries'
    )),

    -- Significance
    significance_score INTEGER CHECK (significance_score BETWEEN 0 AND 1000),

    -- Display
    timeline_icon TEXT, -- Font Awesome class (e.g., "fa-gavel")
    display_order INTEGER,

    -- Source Tracking
    source_table TEXT, -- "court_events" or "legal_documents"
    source_id BIGINT,

    -- WordPress Sync
    synced_to_wordpress BOOLEAN DEFAULT false,
    wordpress_post_id INTEGER,

    -- Approval
    approval_status TEXT CHECK (approval_status IN ('pending', 'approved', 'rejected')),
    approved_at TIMESTAMPTZ,
    approved_by TEXT
);

-- Auto-Generated Blog Posts
CREATE TABLE IF NOT EXISTS auto_blog_posts (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Trigger Information
    trigger_type TEXT CHECK (trigger_type IN (
        'legal_victory',
        'court_update',
        'weekly_summary',
        'milestone',
        'smoking_gun'
    )),
    trigger_data JSONB, -- Store details about what triggered the post

    -- Post Content
    post_title TEXT NOT NULL,
    post_content TEXT, -- Generated blog post content
    post_excerpt TEXT,

    -- Metadata
    relevancy_score INTEGER CHECK (relevancy_score BETWEEN 0 AND 1000),
    tags TEXT[],

    -- WordPress Sync
    wordpress_post_id INTEGER,
    status TEXT CHECK (status IN ('draft', 'pending_review', 'published', 'rejected')),
    published_at TIMESTAMPTZ,

    -- Source Links
    source_documents BIGINT[], -- Array of legal_documents.id
    source_events BIGINT[] -- Array of court_events.id
);

-- Privacy Redaction Log (for compliance auditing)
CREATE TABLE IF NOT EXISTS privacy_redaction_log (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Content Information
    content_type TEXT, -- "timeline_event", "court_hearing", "resource", etc.
    content_id BIGINT,

    -- Redaction Details
    original_length INTEGER,
    filtered_length INTEGER,
    redaction_percentage NUMERIC(5,2),

    -- Patterns Detected
    patterns_found JSONB, -- {names: 3, emails: 1, phones: 2, etc.}

    -- Action Taken
    action TEXT CHECK (action IN ('redacted', 'rejected', 'approved')),
    rejection_reason TEXT,

    -- WordPress
    wordpress_post_id INTEGER
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Court Events
CREATE INDEX IF NOT EXISTS idx_court_events_wordpress_sync
ON court_events(synced_to_wordpress) WHERE synced_to_wordpress = false;

CREATE INDEX IF NOT EXISTS idx_court_events_public_safe
ON court_events(public_safe) WHERE public_safe = true;

CREATE INDEX IF NOT EXISTS idx_court_events_relevancy
ON court_events(relevancy_number) WHERE relevancy_number >= 700;

-- Resources
CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_resources_verified ON resources(verified) WHERE verified = true;
CREATE INDEX IF NOT EXISTS idx_resources_public_safe ON resources(public_safe) WHERE public_safe = true;
CREATE INDEX IF NOT EXISTS idx_resources_wordpress_sync ON resources(synced_to_wordpress);

-- Public Timeline Events
CREATE INDEX IF NOT EXISTS idx_timeline_events_date ON public_timeline_events(event_date DESC);
CREATE INDEX IF NOT EXISTS idx_timeline_events_category ON public_timeline_events(event_category);
CREATE INDEX IF NOT EXISTS idx_timeline_events_approval ON public_timeline_events(approval_status);
CREATE INDEX IF NOT EXISTS idx_timeline_events_source ON public_timeline_events(source_table, source_id);

-- Auto Blog Posts
CREATE INDEX IF NOT EXISTS idx_blog_posts_status ON auto_blog_posts(status);
CREATE INDEX IF NOT EXISTS idx_blog_posts_trigger_type ON auto_blog_posts(trigger_type);
CREATE INDEX IF NOT EXISTS idx_blog_posts_created ON auto_blog_posts(created_at DESC);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE court_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public_timeline_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE auto_blog_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE privacy_redaction_log ENABLE ROW LEVEL SECURITY;

-- Service Role Policies (for WordPress server-side access)
CREATE POLICY IF NOT EXISTS "Service role can read court_events"
ON court_events FOR SELECT
TO service_role
USING (true);

CREATE POLICY IF NOT EXISTS "Service role can update court_events"
ON court_events FOR UPDATE
TO service_role
USING (true);

CREATE POLICY IF NOT EXISTS "Service role can read resources"
ON resources FOR SELECT
TO service_role
USING (true);

CREATE POLICY IF NOT EXISTS "Service role can update resources"
ON resources FOR UPDATE
TO service_role
USING (true);

CREATE POLICY IF NOT EXISTS "Service role can manage timeline_events"
ON public_timeline_events FOR ALL
TO service_role
USING (true);

CREATE POLICY IF NOT EXISTS "Service role can manage blog_posts"
ON auto_blog_posts FOR ALL
TO service_role
USING (true);

CREATE POLICY IF NOT EXISTS "Service role can write privacy_logs"
ON privacy_redaction_log FOR INSERT
TO service_role
WITH CHECK (true);

-- Public Read Policies (for anonymous website visitors via anon key - optional)
-- Uncomment if you want to allow direct public database access (not recommended)
-- Recommend using WordPress as the public-facing layer instead

-- CREATE POLICY "Public can read approved timeline events"
-- ON public_timeline_events FOR SELECT
-- TO anon
-- USING (approval_status = 'approved' AND synced_to_wordpress = true);

-- CREATE POLICY "Public can read published blog posts"
-- ON auto_blog_posts FOR SELECT
-- TO anon
-- USING (status = 'published');

-- CREATE POLICY "Public can read verified resources"
-- ON resources FOR SELECT
-- TO anon
-- USING (verified = true AND public_safe = true);

-- =============================================================================
-- FUNCTIONS & TRIGGERS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for resources table
DROP TRIGGER IF EXISTS update_resources_updated_at ON resources;
CREATE TRIGGER update_resources_updated_at
    BEFORE UPDATE ON resources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to auto-create timeline events from court events (optional)
CREATE OR REPLACE FUNCTION auto_create_timeline_event()
RETURNS TRIGGER AS $$
BEGIN
    -- Only create timeline event if relevancy is high enough and public safe
    IF NEW.relevancy_number >= 700 AND NEW.public_safe = true THEN
        INSERT INTO public_timeline_events (
            event_date,
            event_title,
            event_description,
            event_category,
            significance_score,
            source_table,
            source_id,
            approval_status
        ) VALUES (
            NEW.event_date,
            NEW.event_title,
            NEW.event_description,
            'court-hearings', -- Default category, can be changed in WordPress
            NEW.relevancy_number,
            'court_events',
            NEW.id,
            'pending'
        );
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-create timeline events (optional - can be disabled)
-- DROP TRIGGER IF EXISTS create_timeline_from_court_event ON court_events;
-- CREATE TRIGGER create_timeline_from_court_event
--     AFTER INSERT ON court_events
--     FOR EACH ROW
--     EXECUTE FUNCTION auto_create_timeline_event();

-- =============================================================================
-- SAMPLE DATA (Optional - for testing)
-- =============================================================================

-- Sample Resources
INSERT INTO resources (
    resource_name,
    description,
    resource_type,
    contact_email,
    website_url,
    location,
    cost,
    verified,
    public_safe,
    relevancy_score
) VALUES
(
    'Bay Area Legal Aid',
    'Free legal services for low-income families in the Bay Area. Specializes in family law, housing, and public benefits.',
    'legal',
    'info@baylegal.org',
    'https://baylegal.org',
    'Oakland, CA',
    'Free',
    true,
    true,
    850
),
(
    'National Center for Youth Law',
    'Advocates for the rights of children in foster care and child welfare systems.',
    'advocacy',
    'info@youthlaw.org',
    'https://youthlaw.org',
    'Oakland, CA',
    'Free',
    true,
    true,
    900
)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Run these queries after migration to verify setup:

-- Check table creation
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

-- Check RLS is enabled
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Check policies
-- SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public' ORDER BY tablename;

-- Check indexes
-- SELECT tablename, indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename;

-- =============================================================================
-- NOTES
-- =============================================================================

/*
IMPORTANT:
1. Run this migration in Supabase SQL Editor
2. Get your service_role key from Supabase → Settings → API
3. Configure WordPress plugin with your Supabase URL and service_role key
4. Enable automatic sync in WordPress plugin settings
5. Review Privacy Logs regularly to ensure sensitive data is being redacted

SECURITY:
- NEVER use the anon key for WordPress plugin (server-side requires service_role)
- NEVER commit your service_role key to Git
- Always use HTTPS for WordPress site
- Enable manual approval for high-sensitivity content
- Review all drafted content before publishing

COMPLIANCE:
- Privacy redaction logs are stored for HIPAA/FERPA audit compliance
- All content is filtered before WordPress sync
- Manual approval workflow ensures human review
- Rejected content is logged with reasons

For support: https://github.com/dondada876/ASEAGI
*/
