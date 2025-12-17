#!/usr/bin/env python3
"""
Create Bug Ticket for Production File Deletion Event

Documents the incident where Claude Code web deleted 9 production files
from the codebase during branch creation, and the recovery process.
"""

import os
from datetime import datetime
from supabase import create_client

# Supabase connection
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_deletion_event_bug():
    """Create comprehensive bug ticket for file deletion incident"""

    bug_data = {
        'title': 'INCIDENT: Claude Code web deleted 9 production files during branch creation',
        'description': '''**Incident Summary:**
During branch creation by Claude Code web interface, 9 critical production files were deleted from the codebase. This incident was discovered on 2025-11-10 when comparing branch `claude/api-vs-web-clarification-011CUuqk9SwXoeKNSzwfQq68` against `main`.

**Timeline of Events:**

1. **Branch Creation**: Claude Code web created branch `claude/api-vs-web-clarification-011CUuqk9SwXoeKNSzwfQq68`
2. **Schema Prevention System Added**: Web interface added schema validation system (8 files)
3. **Production Files Deleted**: 9 production files were removed during this process
4. **Discovery**: 2025-11-10 - User requested verification of files on web branch
5. **Investigation**: Checked out branch and discovered missing production files
6. **Recovery**: Created merge branch `merge/schema-prevention-with-production` and restored all files from main

**Files Deleted (9 total):**

**Scanner Files (6):**
1. `scanners/telegram_bot_simple.py` - **CRITICAL**: Production Telegram bot with command handlers (/help, /violations, /search, /timeline, /actions, /deadline, /report)
2. `scanners/telegram_bot_enhanced.py` - Alternative bot implementation with advanced features
3. `scanners/ocr_telegram_documents.py` - OCR processing for Telegram document images
4. `scanners/whatsapp_analyzer.py` - WhatsApp message analysis tool
5. `scanners/upload_telegram_images.py` - Image upload utility for Telegram
6. `scanners/check_ex_parte.py` - Ex parte document checker

**Security Documentation (3):**
7. `database/security/create_security_bug_tickets.py` - Script that created 179 security bug tickets
8. `database/security/create_violations_display_bugs.py` - Script that created BUG-00362 and BUG-00363
9. `database/security/SECURITY_ISSUES_REPORT.md` - Complete security audit report (175+ issues documented)

**Impact Assessment:**

**Severity: HIGH**
- Production Telegram bot deleted (actively used for case management)
- Security documentation deleted (179 bug tickets referenced these files)
- Scanner utilities deleted (used for document processing)
- No data loss (files recovered from main branch)
- System was down until recovery completed

**Root Cause Analysis:**

The deletion appears to have occurred during branch creation by Claude Code web interface. Possible causes:
1. **Merge conflict resolution**: Files may have been removed during automated merge conflict handling
2. **Branch divergence**: Web interface may have chosen wrong base branch
3. **Git operation error**: Potential issue with git checkout/merge operations
4. **Missing file tracking**: Files may have been removed and not re-added

**Recovery Actions Taken:**

1. Created new merge branch: `merge/schema-prevention-with-production`
2. Restored all 9 files from main branch using `git checkout main -- <files>`
3. Committed restoration with detailed documentation
4. Created this bug ticket to document incident
5. Creating best practices report to prevent future incidents

**Recovery Commands:**
```bash
# Created merge branch
git checkout -b merge/schema-prevention-with-production

# Restored scanner files
git checkout main -- scanners/telegram_bot_simple.py
git checkout main -- scanners/telegram_bot_enhanced.py
git checkout main -- scanners/ocr_telegram_documents.py
git checkout main -- scanners/whatsapp_analyzer.py
git checkout main -- scanners/upload_telegram_images.py
git checkout main -- scanners/check_ex_parte.py

# Restored security documentation
git checkout main -- database/security/

# Committed restoration
git commit -m "Merge: Restore production files deleted from Claude web branch"
```

**Files Preserved from Web Branch:**

The schema prevention system files from Claude web branch were preserved:
- `database/schema_types.py` (3.9KB)
- `database/validate_schema.py` (8.5KB)
- `tests/test_database_schema.py` (8.0KB)
- `scripts/setup_prevention_system.sh` (2.9KB)
- `.pre-commit-config.yaml`
- `.github/workflows/schema-validation.yml`
- `SCHEMA_MISMATCH_PREVENTION.md`
- `DEPLOY_PREVENTION_SYSTEM.md`

**Prevention Measures:**

1. **Code Review Required**: All branch merges must be reviewed before merging to main
2. **Branch Comparison**: Before merging, run `git diff` to identify all changes
3. **File Deletion Alerts**: Create git hooks to alert on file deletions
4. **Backup Strategy**: Maintain regular backups of critical production files
5. **CI/CD Validation**: Add automated tests to verify all expected files exist
6. **Documentation**: All file deletions must be explicitly documented in commit messages

**Lessons Learned:**

1. Always verify branch contents before merging
2. Compare web-created branches against main to identify unexpected changes
3. Production files should be protected with branch protection rules
4. Critical files should have automated existence checks in CI/CD
5. File deletions should trigger review requirements

**Related Tickets:**
- BUG-00362: Telegram bot violations command displaying incorrect data
- BUG-00363: Streamlit dashboard Tab 3 violations display error
- BUG-00183 to BUG-00361: Security issues documented in deleted SECURITY_ISSUES_REPORT.md

**Resolution:**
✅ All files successfully restored
✅ Merge branch created with both schema prevention system and production files
✅ Incident documented in this bug ticket
⏳ Best practices report pending
⏳ Deployment to production pending

**Commit Hash:**
- Restoration commit: c8ed30a (merge/schema-prevention-with-production)
''',
        'bug_type': 'INCIDENT',
        'severity': 'high',
        'priority': 'urgent',
        'status': 'resolved',
        'tags': ['git', 'file-deletion', 'incident', 'recovery', 'claude-code-web', 'production'],
    }

    try:
        result = supabase.table('bugs').insert(bug_data).execute()
        bug_id = result.data[0]['id']
        bug_number = result.data[0]['bug_number']

        print(f"✅ Successfully created incident ticket: {bug_number}")
        print(f"   Bug ID: {bug_id}")
        print(f"   Title: {bug_data['title']}")
        print(f"   Severity: {bug_data['severity'].upper()}")
        print(f"   Status: {bug_data['status']}")
        print(f"\n📋 Incident Details:")
        print(f"   - 9 production files deleted")
        print(f"   - 6 scanner files (including production Telegram bot)")
        print(f"   - 3 security documentation files")
        print(f"   - All files successfully restored from main branch")
        print(f"\n🔗 View ticket in database:")
        print(f"   SELECT * FROM bugs WHERE bug_number = '{bug_number}';")

        return bug_number

    except Exception as e:
        print(f"❌ Error creating incident ticket: {e}")
        return None

if __name__ == "__main__":
    print("=" * 80)
    print("📝 CREATING INCIDENT TICKET: Production File Deletion Event")
    print("=" * 80)
    print()

    bug_number = create_deletion_event_bug()

    if bug_number:
        print()
        print("=" * 80)
        print("✅ INCIDENT TICKET CREATION COMPLETE")
        print("=" * 80)
        print()
        print(f"Ticket Number: {bug_number}")
        print()
        print("Next Steps:")
        print("1. Review incident ticket in Supabase")
        print("2. Create best practices report")
        print("3. Implement prevention measures")
        print("4. Deploy merged codebase to production")
    else:
        print()
        print("=" * 80)
        print("❌ INCIDENT TICKET CREATION FAILED")
        print("=" * 80)
