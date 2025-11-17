# DEVELOPMENT POLICY & VERSIONING GUIDE
## ASEAGI Project - File Organization and Version Control

**Created:** November 17, 2025
**Purpose:** Establish naming conventions, versioning standards, and file organization for new developments
**Status:** OFFICIAL POLICY - All developers must follow

---

## 🚨 CRITICAL PROBLEM

**Issue:** New features/tools are being added directly to production directories without versioning, risking:
- Overwrites of critical files
- Loss of working versions
- No rollback capability
- Confusion about "current" vs "development" versions

**Example Recent Issue:**
- Criminal complaint analysis system added directly to:
  - `database/criminal_complaint_schema.py`
  - `scanners/criminal_complaint_analyzer.py`
  - `dashboards/criminal_complaint_dashboard.py`
- **RISK:** If updated, no way to preserve original working version

---

## ✅ SOLUTION: VERSIONED DEVELOPMENT STRUCTURE

### Directory Structure for New Developments

```
ASEAGI/
├─ developments/                    ← NEW: All new features go here
│  ├─ criminal-complaint/          ← Feature name
│  │  ├─ v1.0-2025-11-17/         ← Version + date
│  │  │  ├─ schema.py
│  │  │  ├─ analyzer.py
│  │  │  ├─ dashboard.py
│  │  │  ├─ guide.md
│  │  │  ├─ CHANGELOG.md
│  │  │  └─ VERSION.txt           ← Contains: "1.0"
│  │  ├─ v1.1-2025-11-20/         ← Next version
│  │  │  └─ [improved files]
│  │  ├─ current -> v1.0-2025-11-17/  ← Symlink to stable
│  │  └─ README.md                ← Feature overview
│  │
│  ├─ telegram-workflows/
│  │  ├─ v1.0-2025-11-06/
│  │  └─ current -> v1.0-2025-11-06/
│  │
│  └─ tiered-storage/
│     ├─ v1.0-2025-11-06/
│     └─ current -> v1.0-2025-11-06/
│
├─ scanners/                       ← STABLE: Only proven, production-ready code
│  ├─ batch_scan_documents.py
│  └─ query_legal_documents.py
│
├─ dashboards/                     ← STABLE: Only deployed dashboards
│  ├─ proj344_master_dashboard.py
│  └─ legal_intelligence_dashboard.py
│
└─ database/                       ← STABLE: Only production schemas
   └─ schema_types.py
```

---

## 📋 NAMING CONVENTIONS

### 1. Feature Directory Names

**Format:** `lowercase-with-dashes`

**Good:**
- `criminal-complaint`
- `telegram-workflows`
- `tiered-storage`
- `evidence-analyzer`

**Bad:**
- `CriminalComplaint` (capital letters)
- `criminal_complaint` (underscores)
- `cc-analysis` (unclear abbreviation)

### 2. Version Directory Names

**Format:** `vX.Y-YYYY-MM-DD`

**Examples:**
- `v1.0-2025-11-17` - Initial release
- `v1.1-2025-11-20` - Minor update
- `v2.0-2025-12-01` - Major rewrite

**Version Numbering:**
- `v1.0` - Initial working version
- `v1.1, v1.2, etc.` - Bug fixes, minor improvements
- `v2.0, v3.0, etc.` - Major rewrites, breaking changes

### 3. File Names

**Python Scripts:**
- `schema.py` (not `criminal_complaint_schema.py` - folder provides context)
- `analyzer.py` (not `criminal_complaint_analyzer.py`)
- `dashboard.py` (not `criminal_complaint_dashboard.py`)

**Documentation:**
- `README.md` - Feature overview
- `GUIDE.md` - User guide
- `CHANGELOG.md` - Version history
- `VERSION.txt` - Current version number

### 4. Commit Messages for Versioned Developments

**Format:**
```
[Feature Name] v1.0: Brief description

LOCATION: developments/feature-name/v1.0-YYYY-MM-DD/
VERSION: 1.0
STATUS: Development | Testing | Stable

Changes:
- Change 1
- Change 2

Testing: Describe testing done
```

---

## 🔄 DEVELOPMENT WORKFLOW

### Phase 1: New Feature Development

```bash
# 1. Create feature directory structure
mkdir -p developments/my-feature/v1.0-2025-11-17
cd developments/my-feature/v1.0-2025-11-17

# 2. Create VERSION.txt
echo "1.0" > VERSION.txt

# 3. Create README.md
cat > README.md <<EOF
# Feature Name

**Version:** 1.0
**Date:** 2025-11-17
**Status:** Development

## Description
What this feature does...

## Files
- schema.py - Data structures
- analyzer.py - Analysis engine
- dashboard.py - UI (if applicable)

## Usage
How to use it...
EOF

# 4. Develop your feature
# Create your files: schema.py, analyzer.py, etc.

# 5. Create CHANGELOG.md
cat > CHANGELOG.md <<EOF
# Changelog

## v1.0 - 2025-11-17

### Added
- Initial implementation
- Feature X
- Feature Y

### Testing
- Tested with 601 documents
- All tests passing
EOF

# 6. Create symlink to current version
cd ..
ln -s v1.0-2025-11-17 current

# 7. Commit
git add developments/my-feature/
git commit -m "[My Feature] v1.0: Initial implementation

LOCATION: developments/my-feature/v1.0-2025-11-17/
VERSION: 1.0
STATUS: Development"
```

### Phase 2: Testing & Iteration

```bash
# When making changes, create new version
mkdir -p developments/my-feature/v1.1-2025-11-20
cd developments/my-feature/v1.1-2025-11-20

# Copy from previous version
cp -r ../v1.0-2025-11-17/* .

# Update VERSION.txt
echo "1.1" > VERSION.txt

# Make your changes...

# Update CHANGELOG.md
cat >> CHANGELOG.md <<EOF

## v1.1 - 2025-11-20

### Fixed
- Bug in analyzer.py line 123
- Dashboard loading issue

### Changed
- Improved performance by 50%
EOF

# Update symlink
cd ..
rm current
ln -s v1.1-2025-11-20 current

# Commit
git commit -m "[My Feature] v1.1: Bug fixes and performance improvements

LOCATION: developments/my-feature/v1.1-2025-11-20/
VERSION: 1.1
STATUS: Testing"
```

### Phase 3: Production Promotion

```bash
# Only after thorough testing, promote to production
# Copy stable version to production directories

# Example: Promote dashboard to production
cp developments/my-feature/current/dashboard.py dashboards/my_feature_dashboard.py

# Mark as stable in README
echo "STATUS: Stable - Promoted to production" >> developments/my-feature/current/README.md

# Commit
git commit -m "[My Feature] v1.1: PROMOTED TO PRODUCTION

SOURCE: developments/my-feature/v1.1-2025-11-20/
PRODUCTION FILES:
  - dashboards/my_feature_dashboard.py

TESTING COMPLETED:
  - Unit tests passed
  - Integration tests passed
  - Manual testing completed
  - Reviewed by: [Name]"
```

---

## 📊 VERSION LIFECYCLE

```
Development → Testing → Staging → Production → Archive

developments/           Production Dirs         archive/
my-feature/            (dashboards/, scanners/) retired-features/
├─ v1.0/ (dev)    →    [Not promoted]      →   [Deleted]
├─ v1.1/ (test)   →    [Not promoted]      →   [Deleted]
├─ v1.2/ (test)   →    my_feature.py       →   [Keep in developments/]
├─ v2.0/ (dev)
└─ current -> v1.2/
```

### Version Status Labels

- **Development:** Actively being built, may have bugs
- **Testing:** Feature complete, undergoing testing
- **Staging:** Tested, ready for production
- **Stable:** In production, proven reliable
- **Deprecated:** Replaced by newer version
- **Archived:** Historical reference only

---

## 🗂️ WHERE TO PUT DIFFERENT FILE TYPES

### New Analysis Scripts
**Location:** `developments/[feature-name]/vX.Y-YYYY-MM-DD/`

**Example:**
```
developments/criminal-complaint/v1.0-2025-11-17/
├─ analyzer.py
├─ schema.py
└─ GUIDE.md
```

### New Dashboards
**Development:** `developments/[feature-name]/vX.Y-YYYY-MM-DD/dashboard.py`
**Production:** `dashboards/[feature]_dashboard.py` (only after testing)

### New Database Schemas
**Development:** `developments/[feature-name]/vX.Y-YYYY-MM-DD/schema.py`
**Production:** `database/schema_types.py` (add to existing) OR `database/[feature]_schema.py`

### Documentation
**Feature Docs:** `developments/[feature-name]/GUIDE.md`
**Project Docs:** `docs/[TOPIC].md`
**Root Docs:** Only for project-wide guides (README.md, CLAUDE.md, etc.)

### Workflow Configurations
**Development:** `developments/[feature-name]/vX.Y-YYYY-MM-DD/workflow.json`
**Production:** `n8n-workflows/` (only after testing)

---

## 🔒 PROTECTION RULES

### 1. Never Overwrite Production Files

**Rule:** Production directories (`dashboards/`, `scanners/`, `database/`) only get NEW files or REVIEWED updates.

**Process:**
```bash
# ❌ DON'T: Overwrite existing file
cp developments/my-feature/current/analyzer.py scanners/batch_scan_documents.py

# ✅ DO: Create new file with version
cp developments/my-feature/current/analyzer.py scanners/batch_scan_documents_v2.py

# Or rename old one first
mv scanners/batch_scan_documents.py scanners/batch_scan_documents_v1_backup.py
cp developments/my-feature/current/analyzer.py scanners/batch_scan_documents.py
```

### 2. Always Keep Previous Version

**Rule:** Before replacing ANY production file, commit current version to git.

```bash
# Check current status
git status

# Commit existing version first
git add scanners/my_script.py
git commit -m "Backup v1.0 before updating to v2.0"

# Now safe to update
cp developments/my-feature/current/my_script.py scanners/my_script.py
```

### 3. Document All Promotions

**Rule:** Every promotion to production requires:
- Version number in commit message
- Source location documented
- Testing evidence provided
- Reviewer approval (if team)

---

## 📝 EXAMPLE: Criminal Complaint System (CORRECTED)

### Current Problem

Files placed directly in production:
```
❌ database/criminal_complaint_schema.py
❌ scanners/criminal_complaint_analyzer.py
❌ dashboards/criminal_complaint_dashboard.py
❌ CRIMINAL_COMPLAINT_ANALYSIS_GUIDE.md
```

### Correct Structure

```
✅ developments/criminal-complaint/v1.0-2025-11-17/
   ├─ VERSION.txt                    (contains "1.0")
   ├─ README.md                      (feature overview)
   ├─ CHANGELOG.md                   (version history)
   ├─ GUIDE.md                       (user guide, moved from root)
   ├─ schema.py                      (from database/)
   ├─ analyzer.py                    (from scanners/)
   └─ dashboard.py                   (from dashboards/)

✅ developments/criminal-complaint/current -> v1.0-2025-11-17/
```

---

## 🛠️ MIGRATION SCRIPT

### Move Existing Files to Versioned Structure

```bash
#!/bin/bash
# migrate_to_versioned_structure.sh

FEATURE_NAME="criminal-complaint"
VERSION="v1.0"
DATE="2025-11-17"

# Create directory structure
mkdir -p "developments/${FEATURE_NAME}/${VERSION}-${DATE}"
cd "developments/${FEATURE_NAME}/${VERSION}-${DATE}"

# Move files from production directories
mv ../../../database/criminal_complaint_schema.py ./schema.py
mv ../../../scanners/criminal_complaint_analyzer.py ./analyzer.py
mv ../../../dashboards/criminal_complaint_dashboard.py ./dashboard.py
mv ../../../CRIMINAL_COMPLAINT_ANALYSIS_GUIDE.md ./GUIDE.md

# Create VERSION.txt
echo "1.0" > VERSION.txt

# Create README.md
cat > README.md <<'EOF'
# Criminal Complaint Evidence Analysis System

**Version:** 1.0
**Date:** 2025-11-17
**Status:** Testing

## Description
Complete system to query all 601+ documents against perjury claims.

## Files
- schema.py - Defines 5 false statements with scoring algorithms
- analyzer.py - Analysis engine with master report generator
- dashboard.py - Real-time visual analysis (port 8506)
- GUIDE.md - Complete user documentation

## Usage
```bash
# Run analysis
python3 -m developments.criminal-complaint.current.analyzer

# Launch dashboard
streamlit run developments/criminal-complaint/current/dashboard.py --server.port 8506
```
EOF

# Create CHANGELOG.md
cat > CHANGELOG.md <<'EOF'
# Changelog

## v1.0 - 2025-11-17

### Added
- Initial implementation
- 5 false statement definitions with keywords
- Correlation scoring (0-999)
- Prosecutability assessment (0-100)
- Master report generator
- Real-time dashboard
- Complete user guide

### Testing
- Tested with 601 documents
- All 5 claims analyzed successfully
- Dashboard functional on port 8506
EOF

# Create symlink
cd ..
ln -s "${VERSION}-${DATE}" current

echo "✅ Migration complete!"
echo "   Location: developments/${FEATURE_NAME}/${VERSION}-${DATE}/"
echo "   Current: developments/${FEATURE_NAME}/current/"
```

---

## 📋 CHECKLIST: Adding New Feature

```markdown
## New Feature Checklist

### Setup
- [ ] Create feature directory: `developments/[feature-name]/`
- [ ] Create version directory: `v1.0-YYYY-MM-DD/`
- [ ] Create VERSION.txt with version number
- [ ] Create README.md with feature overview
- [ ] Create CHANGELOG.md

### Development
- [ ] Write code in version directory
- [ ] Test thoroughly
- [ ] Document in GUIDE.md or README.md
- [ ] Update CHANGELOG.md with changes

### Version Control
- [ ] Create symlink: `current -> v1.0-YYYY-MM-DD/`
- [ ] Commit with proper message format
- [ ] Tag version in git: `git tag feature-name-v1.0`

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Documentation reviewed

### Production (Only if approved)
- [ ] Copy to production directories
- [ ] Update production documentation
- [ ] Mark as "Stable" in README.md
- [ ] Commit with promotion message
```

---

## 🚀 BENEFITS OF THIS SYSTEM

### 1. No Overwrites
- Every version preserved
- Can always roll back
- Safe to experiment

### 2. Clear History
- See evolution of feature
- Understand why changes made
- Learn from past versions

### 3. Easy Testing
- Test new version without affecting production
- Compare versions side-by-side
- Switch between versions with symlink

### 4. Team Collaboration
- Clear ownership of versions
- Easy code review
- Avoid merge conflicts

### 5. Professional Organization
- Matches industry standards
- Easy for new developers to understand
- Scalable as project grows

---

## 📚 RELATED DOCUMENTS

- `docs/GIT_WORKFLOW_BEST_PRACTICES.md` - Git operations and branch management
- `docs/BRANCH_PROTECTION_SETUP.md` - Protecting critical files
- `.github/CODEOWNERS` - File ownership rules
- `CLAUDE.md` - Project overview and architecture

---

## ❓ FAQ

**Q: Do I always need to create a new version for small changes?**
A: No. For bug fixes in development, you can update the current version. Create new versions for:
- Significant feature additions
- Breaking changes
- Before promoting to production

**Q: What if I just want to experiment?**
A: Create a `vX.Y-experimental-YYYY-MM-DD/` directory. Mark it clearly in README.

**Q: Can I delete old versions?**
A: Only after:
- Newer version is stable
- No one is using old version
- You've archived it in git history
- At least 30 days have passed

**Q: What about quick scripts/utilities?**
A: One-off scripts can go in `scripts/` without versioning. But if it becomes important, migrate to `developments/`.

---

## 🎯 ACTION REQUIRED

### Immediate: Migrate Criminal Complaint System

Run the migration script to move files to proper structure:

```bash
bash scripts/migrate_criminal_complaint_to_versioned.sh
```

### Going Forward: All New Features

Use `developments/` structure for ALL new features:
- Evidence analyzers
- New dashboards
- Workflow integrations
- Database schemas
- Automation scripts

---

**Document Version:** 1.0
**Last Updated:** November 17, 2025
**Maintained By:** Development Team
**Status:** OFFICIAL POLICY

---

**Questions?** Create an issue or discuss in team meetings.
**Violations?** Will result in code review rejection.

**Remember: Version everything. Preserve history. Never overwrite production.**
