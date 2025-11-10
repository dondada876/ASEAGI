# ASEAGI WordPress Connector Plugin

**Version:** 1.0.0
**Purpose:** Public-facing legal case storytelling with privacy protection
**For Ashe. For Justice. For All Children.** 🛡️

## Overview

The ASEAGI WordPress Connector plugin bridges your private Supabase legal case management database with a public WordPress website, enabling transparent storytelling about your legal case while automatically protecting sensitive information.

### Key Features

✅ **Automatic Data Sync** - Pulls legal documents, court events, and resources from Supabase every 15 minutes
🔒 **Privacy Protection** - Comprehensive redaction of names, addresses, SSNs, case numbers, and sensitive data
📋 **Manual Approval Workflow** - Review all synced content before it goes public
📅 **Timeline Integration** - Works with Cool Timeline Pro to display chronological court events
🗓️ **Calendar Integration** - Syncs with EventON for upcoming court dates
📚 **Directory Integration** - Compatible with ListingPro for resource directories
📊 **Analytics & Monitoring** - Real-time sync status, statistics, and privacy audit logs
⚡ **PROJ344 Compatible** - Uses the same 0-1000 relevancy scoring system

---

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Supabase Setup](#supabase-setup)
4. [Usage](#usage)
5. [Premium Plugin Integration](#premium-plugin-integration)
6. [Privacy & Security](#privacy--security)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- WordPress 6.4+
- PHP 8.1+
- MySQL 8.0+
- SSL certificate (required for secure API calls)
- Active Supabase project with legal case data

### Step 1: Upload Plugin

1. Download the `aseagi-wp-connector` folder
2. Upload to `/wp-content/plugins/` directory
3. Or upload as ZIP file via WordPress Admin → Plugins → Add New → Upload Plugin

### Step 2: Activate Plugin

1. Go to WordPress Admin → Plugins
2. Find "ASEAGI WordPress Connector"
3. Click "Activate"

### Step 3: Configure Supabase Connection

1. Go to **ASEAGI → Settings** in WordPress admin
2. Enter your Supabase Project URL (e.g., `https://your-project.supabase.co`)
3. Enter your Supabase Service Role Key (⚠️ use `service_role` key, NOT `anon` key)
4. Click "Test Connection" to verify
5. Click "Save Settings"

✅ **Success!** The plugin will now start syncing data every 15 minutes.

---

## Configuration

### Settings Overview

Navigate to **WordPress Admin → ASEAGI → Settings**

#### Supabase Connection

| Setting | Description | Example |
|---------|-------------|---------|
| **Supabase Project URL** | Your Supabase project URL | `https://abcdefg.supabase.co` |
| **Supabase Service Key** | Service role key (keep secret!) | `eyJhbGciOi...` |

#### Sync Settings

| Setting | Description | Recommended |
|---------|-------------|-------------|
| **Enable Automatic Sync** | Sync every 15 minutes automatically | ✅ Enabled |
| **Relevancy Threshold** | Minimum score to sync (0-1000) | `700` |
| **Manual Approval Required** | Review content before publishing | ✅ Enabled |

**Relevancy Scoring (PROJ344):**
- **900-1000**: Smoking gun evidence (critical)
- **800-899**: High importance (strong evidence)
- **700-799**: Important (supporting evidence)
- **600-699**: Useful (background context)
- **0-599**: Reference only (not synced by default)

#### Privacy Settings

| Setting | Description | Example |
|---------|-------------|---------|
| **Mother's Name** | Real name to redact | `Jane Doe` → replaced with "Mother" |
| **Child's Name** | Real name to redact | `Ashe` → kept as "Ashe" (or use real name) |

---

## Supabase Setup

### Required Tables

Your Supabase database must have these tables:

#### 1. `court_events` Table

```sql
CREATE TABLE court_events (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    event_title TEXT NOT NULL,
    event_description TEXT,
    event_date DATE NOT NULL,
    event_type TEXT,
    relevancy_number INTEGER CHECK (relevancy_number BETWEEN 0 AND 1000),
    synced_to_wordpress BOOLEAN DEFAULT false,
    wordpress_post_id INTEGER
);
```

#### 2. `resources` Table

```sql
CREATE TABLE resources (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resource_name TEXT NOT NULL,
    description TEXT,
    resource_type TEXT CHECK (resource_type IN ('legal', 'support', 'government', 'community')),
    contact_info TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    website_url TEXT,
    location TEXT,
    cost TEXT,
    verified BOOLEAN DEFAULT false,
    verified_date DATE,
    public_safe BOOLEAN DEFAULT true,
    relevancy_score INTEGER CHECK (relevancy_score BETWEEN 0 AND 1000)
);
```

#### 3. `legal_documents` Table (Optional - for statistics)

```sql
CREATE TABLE legal_documents (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    document_title TEXT,
    document_type TEXT,
    relevancy_number INTEGER CHECK (relevancy_number BETWEEN 0 AND 1000),
    upload_date DATE,
    notes TEXT
);
```

### Supabase Security Setup

1. **Enable Row Level Security (RLS)**
   ```sql
   ALTER TABLE court_events ENABLE ROW LEVEL SECURITY;
   ALTER TABLE resources ENABLE ROW LEVEL SECURITY;
   ```

2. **Create Service Role Policy** (allows server-side access)
   ```sql
   CREATE POLICY "Service role can read all"
   ON court_events FOR SELECT
   TO service_role
   USING (true);
   ```

3. **Get Your Service Role Key**
   - Go to Supabase Dashboard → Settings → API
   - Copy the `service_role` key (NOT the `anon` key)
   - Keep this key secret - never commit to Git!

---

## Usage

### Dashboard Overview

Navigate to **WordPress Admin → ASEAGI**

The dashboard shows:
- **Total Synced Posts**: All content pulled from Supabase
- **Pending Approval**: Drafts awaiting manual review
- **Supabase Status**: Connection health
- **Last Sync**: Time since last automatic sync
- **Manual Sync Button**: Trigger immediate sync
- **Sync Results Table**: Detailed breakdown of last sync

### Manual Sync

1. Go to **ASEAGI → Dashboard**
2. Click **"🔄 Sync Now"** button
3. Wait for sync to complete (typically 10-30 seconds)
4. Review results in the dashboard

### Reviewing Synced Content

#### Timeline Events

1. Go to **WordPress Admin → Timeline Events**
2. Find posts with status "Draft"
3. Click post title to review
4. Check **Event Details** meta box for date, significance, icon
5. Review privacy-filtered content
6. Change **Approval Status** to "Approved"
7. Click **"Publish"** when ready to go live

#### Court Hearings

1. Go to **WordPress Admin → Court Hearings**
2. Review draft hearings
3. Verify hearing date, time, location (generalized)
4. Check hearing type and significance
5. Approve and publish

#### Resources

1. Go to **WordPress Admin → Resources**
2. Review contact information
3. Verify helpfulness score
4. Check verification status
5. Publish approved resources

### Privacy Logs

Monitor redaction activity:

1. Go to **ASEAGI → Privacy Logs**
2. View recent redactions with percentages
3. Check rejected content and reasons
4. Review pattern detection details

**What's Logged:**
- All redactions made (last 100)
- Rejected content (last 50)
- Redaction types (names, emails, phones, etc.)
- Timestamps for audit trail

---

## Premium Plugin Integration

### Cool Timeline Pro

**Purpose:** Display chronological court events on public pages

#### Setup

1. Install and activate **Cool Timeline Pro**
2. The plugin automatically uses the `timeline_event` custom post type
3. Configure timeline display:
   - Go to **Cool Timeline → Settings**
   - Select **Post Type**: "Timeline Events"
   - Choose **Layout**: Vertical (One Side)
   - Enable **Categories**: Court Hearings, Legal Victories, CPS Actions, etc.

#### Shortcode Usage

```
[cool-timeline layout="vertical" skin="default" show-posts="30" order="DESC" post-type="timeline_event"]
```

#### Category Colors

Timeline events are automatically categorized:
- 🔴 **Court Hearings** (Red)
- 🟢 **Legal Victories** (Green)
- 🟠 **CPS Actions** (Orange)
- 🔵 **Document Filings** (Blue)
- 🟣 **Milestones** (Purple)
- 🟢 **Evidence Discoveries** (Teal)

### EventON

**Purpose:** Display upcoming court dates in calendar format

#### Setup

1. Install and activate **EventON**
2. The plugin creates `court_hearing` custom post types compatible with EventON
3. Configure EventON settings:
   - Go to **EventON → Settings**
   - Enable custom post type integration
   - Map `court_hearing` → EventON events

#### Manual Event Creation (if needed)

Court hearings are synced automatically, but you can also manually create events:

1. Go to **EventON → Add Event**
2. Link to existing Court Hearing post
3. Set event date, time, location
4. Categorize by hearing type

### ListingPro

**Purpose:** Create resources directory for legal services and support

#### Setup

1. Install and activate **ListingPro** theme
2. The plugin uses `resource` custom post type
3. Configure ListingPro:
   - Go to **ListingPro → Settings**
   - Enable custom post type: "Resources"
   - Map taxonomy: "Resource Types"

#### Resource Categories

Automatically created:
- 🏛️ Legal Services
- 💬 Support Services
- 🏢 Government Agencies
- 📣 Advocacy Organizations
- 📖 Educational Resources
- 💰 Financial Assistance
- 🏠 Housing Assistance
- 🧠 Mental Health Services

---

## Privacy & Security

### Automatic Redaction

**What's Redacted:**
- ✅ Full names (replaced with [Name Redacted] or "Mother"/"Ashe")
- ✅ Email addresses
- ✅ Phone numbers (all formats)
- ✅ Street addresses
- ✅ SSN (Social Security Numbers)
- ✅ Case numbers and docket IDs
- ✅ Dates of birth
- ✅ Medical record numbers
- ✅ Driver's license numbers
- ✅ Bank account numbers
- ✅ Credit card numbers

**Context-Specific Filtering:**
- **Timeline Events**: Judge names, opposing counsel, courtroom numbers redacted
- **Court Hearings**: Specific locations generalized (e.g., "Berkeley Family Court")
- **Documents**: High-relevancy docs (900+) get extra cautious filtering

### Public Safety Checker

Content is rejected if:
- Relevancy score < threshold (default 700)
- More than 50% of content requires redaction
- Contains red flag keywords:
  - Medical diagnosis
  - Therapy session notes
  - School records
  - Psychiatric information
  - Substance abuse details
  - Sexual abuse specifics
  - Home addresses
  - Contact information

### Compliance

- **HIPAA**: Medical information automatically filtered
- **FERPA**: Educational records redacted
- **Privacy Best Practices**: All content filtered before publishing
- **Audit Trail**: Complete redaction logs for compliance

### Security Best Practices

1. ✅ **Use HTTPS** - Required for secure API communication
2. ✅ **Service Role Key** - Never use anon key for server-side operations
3. ✅ **Keep Keys Secret** - Never commit to Git or share publicly
4. ✅ **Enable RLS** - Row Level Security in Supabase
5. ✅ **Manual Review** - Always review high-sensitivity content before publishing
6. ✅ **Regular Audits** - Check privacy logs weekly

---

## Troubleshooting

### Connection Issues

**Problem:** "Supabase API Error" or connection test fails

**Solutions:**
1. Verify Supabase URL format: `https://[project-id].supabase.co`
2. Check you're using **service_role** key, not anon key
3. Ensure Supabase project is active (not paused)
4. Check WordPress server can reach Supabase (firewall rules)
5. Verify SSL certificate is valid

### No Content Syncing

**Problem:** Manual sync runs but no posts are created

**Solutions:**
1. Check relevancy threshold - try lowering to 600
2. Verify Supabase tables have data with `relevancy_number >= threshold`
3. Check privacy logs for rejected content
4. Ensure tables have required fields (event_title, event_date, etc.)
5. Review sync results table for error messages

### High Redaction Percentage

**Problem:** Content heavily redacted or entirely rejected

**Solutions:**
1. Review privacy logs to see what's being redacted
2. Check if specific names are configured in Privacy Settings
3. Consider whether content is too sensitive for public display
4. Manually edit content in Supabase to remove sensitive details before sync
5. Use more generalized language in source documents

### Sync Not Running Automatically

**Problem:** Manual sync works, but automatic sync doesn't run

**Solutions:**
1. Check **ASEAGI → Settings** - ensure "Enable Automatic Sync" is checked
2. Verify WP-Cron is working:
   ```bash
   wp cron event list
   ```
3. Check for `aseagi_sync_cron` in cron schedule
4. If using server cron, ensure WordPress cron is properly configured
5. Check PHP error logs for cron-related errors

### Permission Denied Errors

**Problem:** "Permission denied" when syncing

**Solutions:**
1. Verify WordPress user has `manage_options` capability
2. Check file permissions on plugin directory (should be 755)
3. Ensure Supabase RLS policies allow service_role access
4. Verify API key has not expired or been revoked

### EventON/ListingPro Not Integrating

**Problem:** Court hearings/resources not showing in premium plugins

**Solutions:**
1. Verify premium plugin is installed and activated
2. Check plugin version compatibility
3. Manually map custom post types in plugin settings
4. Clear WordPress cache and permalinks (Settings → Permalinks → Save Changes)
5. Check for conflicts with other plugins (disable temporarily to test)

---

## Support & Resources

### Documentation

- **WordPress Codex**: https://codex.wordpress.org/
- **Supabase Docs**: https://supabase.com/docs
- **Cool Timeline Pro**: https://cooltimeline.com/documentation/
- **EventON**: https://www.myeventon.com/documentation/
- **ListingPro**: https://listingprowp.com/documentation/

### Reporting Issues

If you encounter bugs or need help:

1. Check **ASEAGI → Dashboard** for error messages
2. Review **Privacy Logs** for redaction issues
3. Enable WordPress debug mode:
   ```php
   define('WP_DEBUG', true);
   define('WP_DEBUG_LOG', true);
   ```
4. Check `/wp-content/debug.log` for errors
5. Open an issue on the ASEAGI GitHub repository

### Contributing

We welcome contributions! This plugin is open source and part of the ASEAGI project.

**Repository**: https://github.com/dondada876/ASEAGI

---

## Changelog

### Version 1.0.0 (2025-11-10)

**Initial Release**

- ✅ Supabase REST API integration
- ✅ Automatic sync engine with WP-Cron
- ✅ Privacy filter with HIPAA/FERPA compliance
- ✅ Three custom post types (Timeline Events, Court Hearings, Resources)
- ✅ Admin dashboard with real-time statistics
- ✅ Settings page with connection testing
- ✅ Privacy logs and audit trail
- ✅ Manual approval workflow
- ✅ Cool Timeline Pro compatibility
- ✅ EventON calendar integration hooks
- ✅ ListingPro directory integration hooks

---

## License

MIT License

Copyright (c) 2025 ASEAGI Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

---

**For Ashe. For Justice. For All Children.** 🛡️
