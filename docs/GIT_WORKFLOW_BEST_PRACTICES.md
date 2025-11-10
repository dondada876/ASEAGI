# Git Workflow Best Practices

**Created:** 2025-11-10
**Purpose:** Document best practices to prevent production file deletions during branch operations
**Incident Reference:** BUG-00366 - Claude Code web deleted 9 production files during branch creation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Incident Summary](#incident-summary)
3. [Root Cause Analysis](#root-cause-analysis)
4. [Best Practices](#best-practices)
5. [Branch Management](#branch-management)
6. [Code Review Requirements](#code-review-requirements)
7. [Automated Protections](#automated-protections)
8. [Recovery Procedures](#recovery-procedures)
9. [Checklist for Branch Operations](#checklist-for-branch-operations)

---

## Executive Summary

On 2025-11-10, we discovered that Claude Code web interface deleted 9 production files during branch creation. This report documents the incident, root causes, and establishes best practices to prevent future occurrences.

**Key Takeaways:**
- ✅ Always verify branch contents before merging
- ✅ Compare web-created branches against main using `git diff`
- ✅ Protect critical production files with branch protection rules
- ✅ Implement automated file existence checks in CI/CD
- ✅ Require explicit documentation for all file deletions

---

## Incident Summary

### What Happened

During branch creation by Claude Code web interface (branch `claude/api-vs-web-clarification-011CUuqk9SwXoeKNSzwfQq68`), 9 critical production files were deleted from the codebase.

### Files Deleted

**Scanner Files (6):**
1. `scanners/telegram_bot_simple.py` - **CRITICAL**: Production Telegram bot
2. `scanners/telegram_bot_enhanced.py` - Alternative bot implementation
3. `scanners/ocr_telegram_documents.py` - OCR processing
4. `scanners/whatsapp_analyzer.py` - WhatsApp analysis
5. `scanners/upload_telegram_images.py` - Image upload utility
6. `scanners/check_ex_parte.py` - Ex parte checker

**Security Documentation (3):**
7. `database/security/create_security_bug_tickets.py` - Created 179 security bug tickets
8. `database/security/create_violations_display_bugs.py` - Created BUG-00362, BUG-00363
9. `database/security/SECURITY_ISSUES_REPORT.md` - Complete security audit report

### Impact

- **Severity:** HIGH
- **Production Downtime:** Yes (until recovery)
- **Data Loss:** No (files recovered from main branch)
- **System Impact:** Production Telegram bot offline
- **Duration:** Several hours until discovery and recovery

### Resolution

1. Created merge branch `merge/schema-prevention-with-production`
2. Restored all 9 files from main branch using `git checkout main -- <files>`
3. Committed restoration with detailed documentation (commit c8ed30a)
4. Created incident ticket BUG-00366
5. Created this best practices report

---

## Root Cause Analysis

### Possible Causes

1. **Merge Conflict Resolution**
   - Automated merge conflict handling may have removed files
   - Web interface may have chosen wrong conflict resolution strategy

2. **Branch Divergence**
   - Web interface may have used incorrect base branch
   - Files may have been on different branch path

3. **Git Operation Error**
   - Potential issue with `git checkout` or `git merge` operations
   - Missing file tracking during branch operations

4. **Missing File Validation**
   - No automated checks for unexpected file deletions
   - No alerts for production file removal

### Contributing Factors

1. **Lack of Branch Comparison**
   - Didn't compare web branch against main before accepting changes
   - No visual diff review of branch contents

2. **No Branch Protection**
   - Critical production files not protected from deletion
   - No review requirements for file deletions

3. **No CI/CD Validation**
   - No automated tests to verify expected files exist
   - No file inventory checks in pipeline

4. **Insufficient Documentation**
   - No requirement to document file deletions in commits
   - No review process for destructive changes

---

## Best Practices

### 1. Always Verify Branch Contents

**Before accepting any branch:**

```bash
# Fetch the branch
git fetch origin <branch-name>

# Check out the branch locally
git checkout <branch-name>

# Compare against main to see ALL changes
git diff main...<branch-name> --name-status

# Look for deletions (D flag)
git diff main...<branch-name> --name-status | grep "^D"

# Review the full diff
git diff main...<branch-name>
```

**Red Flags:**
- Any file deletions you didn't expect
- Missing critical production files
- Deletions of entire directories
- Changes to files you weren't working on

### 2. Document All File Deletions

**Every file deletion must:**
- Be explicitly mentioned in commit message
- Include reason for deletion
- Be reviewed by at least one other person
- Have a backup/recovery plan

**Example Commit Message:**
```
Remove deprecated authentication module

DELETED FILES:
- auth/deprecated_login.py
- auth/old_session_manager.py

REASON: Replaced with new OAuth2 implementation (PR #123)
MIGRATION: All users migrated to new auth system
BACKUP: Files archived in archive/auth-v1/
```

### 3. Use Git Hooks for Protection

**Pre-commit Hook Example:**

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Check for file deletions
DELETED_FILES=$(git diff --cached --name-status | grep "^D" | wc -l)

if [ $DELETED_FILES -gt 0 ]; then
    echo "⚠️  WARNING: This commit deletes files:"
    git diff --cached --name-status | grep "^D"
    echo ""
    read -p "Are you sure you want to delete these files? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "❌ Commit aborted"
        exit 1
    fi
fi
```

### 4. Branch Protection Rules

**Enable on GitHub:**

1. Navigate to Settings → Branches → Branch protection rules
2. Add rule for `main` branch:
   - ✅ Require pull request reviews before merging (minimum 1)
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

**For Critical Files:**

Use CODEOWNERS file (`.github/CODEOWNERS`):

```
# Critical production files require review
/scanners/*.py @team-lead @senior-dev
/database/security/*.py @security-team
/dashboards/*.py @frontend-team
```

---

## Branch Management

### Creating Branches

**DO:**
- ✅ Create branches from latest `main`
- ✅ Use descriptive branch names (`feature/add-user-auth`, `fix/telegram-bot-crash`)
- ✅ Keep branches short-lived (< 1 week)
- ✅ Sync frequently with `main` to avoid divergence

**DON'T:**
- ❌ Create branches from unknown states
- ❌ Let branches diverge too far from `main`
- ❌ Work on multiple unrelated features in one branch
- ❌ Delete files without explicit reason

### Before Merging

**Checklist:**

1. **Compare with main:**
   ```bash
   git diff main...your-branch --name-status
   ```

2. **Check for unexpected deletions:**
   ```bash
   git diff main...your-branch --name-status | grep "^D"
   ```

3. **Run tests:**
   ```bash
   pytest
   # or your test suite
   ```

4. **Verify all expected files exist:**
   ```bash
   # Example: Check that critical files are present
   test -f scanners/telegram_bot_simple.py || echo "❌ Telegram bot missing!"
   test -f database/security/create_security_bug_tickets.py || echo "❌ Security script missing!"
   ```

5. **Review the diff visually:**
   ```bash
   git diff main...your-branch | less
   ```

### Merging Strategies

**Option 1: Merge Commit (Recommended for production)**
```bash
git checkout main
git merge --no-ff your-branch -m "Merge: Add feature X"
```
- Creates explicit merge commit
- Preserves full history
- Easy to revert if needed

**Option 2: Rebase (For clean history)**
```bash
git checkout your-branch
git rebase main
git checkout main
git merge --ff-only your-branch
```
- Creates linear history
- Cleaner log
- ⚠️ Rewrites history (don't use on shared branches)

**Option 3: Squash Merge (For feature branches)**
```bash
git checkout main
git merge --squash your-branch
git commit -m "Feature: Add user authentication"
```
- Combines all commits into one
- Cleaner main branch
- ⚠️ Loses detailed commit history

---

## Code Review Requirements

### What to Review

1. **File Changes:**
   - Every added file
   - Every modified file
   - **Every deleted file** (most important)

2. **Commit Messages:**
   - Clear description of changes
   - Reason for deletions documented
   - References to issues/tickets

3. **Tests:**
   - New code has tests
   - Existing tests still pass
   - Deleted code has tests removed

4. **Documentation:**
   - README updated if needed
   - API docs updated
   - Comments added for complex code

### Review Checklist

```markdown
## Pull Request Review Checklist

- [ ] Code changes reviewed line by line
- [ ] All file deletions have documented reasons
- [ ] Tests pass locally
- [ ] No unexpected file removals
- [ ] Documentation updated
- [ ] No secrets or credentials in code
- [ ] Follows coding standards
- [ ] Performance implications considered
- [ ] Security implications reviewed
```

---

## Automated Protections

### 1. CI/CD File Existence Check

**GitHub Actions Example:**

Create `.github/workflows/file-existence-check.yml`:

```yaml
name: Critical Files Check

on: [push, pull_request]

jobs:
  check-files:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check critical files exist
        run: |
          MISSING=0

          # List of critical files
          CRITICAL_FILES=(
            "scanners/telegram_bot_simple.py"
            "scanners/telegram_bot_enhanced.py"
            "scanners/ocr_telegram_documents.py"
            "scanners/whatsapp_analyzer.py"
            "scanners/upload_telegram_images.py"
            "scanners/check_ex_parte.py"
            "database/security/create_security_bug_tickets.py"
            "database/security/create_violations_display_bugs.py"
            "database/security/SECURITY_ISSUES_REPORT.md"
          )

          for file in "${CRITICAL_FILES[@]}"; do
            if [ ! -f "$file" ]; then
              echo "❌ CRITICAL: File missing: $file"
              MISSING=$((MISSING+1))
            else
              echo "✅ File exists: $file"
            fi
          done

          if [ $MISSING -gt 0 ]; then
            echo "❌ $MISSING critical files are missing!"
            exit 1
          fi

          echo "✅ All critical files present"
```

### 2. Pre-commit Hooks

**Install pre-commit framework:**

```bash
pip install pre-commit
```

**Create `.pre-commit-config.yaml`:**

```yaml
repos:
  - repo: local
    hooks:
      - id: check-file-deletions
        name: Check file deletions
        entry: bash -c 'git diff --cached --name-status | grep "^D" && echo "⚠️  Files being deleted. Please document reason." && exit 1 || exit 0'
        language: system
        pass_filenames: false

      - id: check-critical-files
        name: Check critical files exist
        entry: bash -c 'test -f scanners/telegram_bot_simple.py || (echo "❌ telegram_bot_simple.py missing!" && exit 1)'
        language: system
        pass_filenames: false
```

**Install hooks:**

```bash
pre-commit install
```

### 3. Branch Protection Script

**Create `scripts/protect_critical_files.sh`:**

```bash
#!/bin/bash

# List of critical files that should never be deleted
CRITICAL_FILES=(
    "scanners/telegram_bot_simple.py"
    "scanners/telegram_bot_enhanced.py"
    "database/security/create_security_bug_tickets.py"
    "database/security/SECURITY_ISSUES_REPORT.md"
)

# Check if any critical files are missing
MISSING=0
for file in "${CRITICAL_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ CRITICAL FILE MISSING: $file"
        MISSING=$((MISSING+1))
    fi
done

if [ $MISSING -gt 0 ]; then
    echo ""
    echo "❌ $MISSING critical files are missing!"
    echo "This may indicate a merge error or accidental deletion."
    echo "Please restore these files before continuing."
    exit 1
fi

echo "✅ All critical files present"
```

---

## Recovery Procedures

### If Files Are Accidentally Deleted

**Step 1: Don't Panic**
- Files are still in git history
- Nothing is truly lost until you force-push

**Step 2: Identify What's Missing**

```bash
# See what files were deleted in last commit
git diff HEAD~1 HEAD --name-status | grep "^D"

# Or compare with main
git diff main...HEAD --name-status | grep "^D"
```

**Step 3: Restore from Git History**

**Option A: Restore specific files from main:**

```bash
git checkout main -- path/to/deleted/file.py
```

**Option B: Restore files from previous commit:**

```bash
git checkout HEAD~1 -- path/to/deleted/file.py
```

**Option C: Restore all deleted files:**

```bash
# Get list of deleted files
git diff HEAD~1 HEAD --name-status | grep "^D" | cut -f2 > /tmp/deleted_files.txt

# Restore each one
while read file; do
    git checkout HEAD~1 -- "$file"
done < /tmp/deleted_files.txt
```

**Step 4: Commit the Restoration**

```bash
git add .
git commit -m "Restore accidentally deleted production files

Files restored:
- scanners/telegram_bot_simple.py
- database/security/create_security_bug_tickets.py

Root cause: Accidental deletion during merge
Prevention: Added file existence checks to CI/CD"
```

**Step 5: Create Incident Ticket**

Document the incident in your bug tracker with:
- What files were deleted
- When it happened
- How it was discovered
- How it was recovered
- Prevention measures implemented

---

## Checklist for Branch Operations

### Before Creating a Branch

- [ ] I'm on the latest `main` branch
  ```bash
  git checkout main && git pull origin main
  ```

- [ ] I understand what changes I'm making
- [ ] I have a clear branch name planned

### While Working on Branch

- [ ] I'm only changing files related to my feature
- [ ] I'm not deleting files unless explicitly needed
- [ ] I'm documenting any file deletions in commits
- [ ] I'm testing changes locally

### Before Merging Branch

- [ ] I've compared my branch with main
  ```bash
  git diff main...my-branch --name-status
  ```

- [ ] I've reviewed all file deletions
  ```bash
  git diff main...my-branch --name-status | grep "^D"
  ```

- [ ] All tests pass
  ```bash
  pytest  # or your test command
  ```

- [ ] Critical files are present
  ```bash
  ./scripts/protect_critical_files.sh
  ```

- [ ] I've documented changes in commit messages
- [ ] Someone else has reviewed my code
- [ ] CI/CD checks are passing

### After Merging Branch

- [ ] I've verified the merge was successful
- [ ] I've checked that all expected files are present
  ```bash
  git checkout main
  ./scripts/protect_critical_files.sh
  ```

- [ ] I've deleted my feature branch
  ```bash
  git branch -d my-branch
  git push origin --delete my-branch
  ```

---

## Additional Resources

### Git Commands Reference

**See what changed in a branch:**
```bash
git diff main...feature-branch --name-status
```

**See deleted files:**
```bash
git diff main...feature-branch --name-status | grep "^D"
```

**Restore a deleted file:**
```bash
git checkout main -- path/to/file.py
```

**Compare two branches:**
```bash
git diff branch1..branch2
```

**See commit history:**
```bash
git log --oneline --graph --decorate --all
```

**Find when a file was deleted:**
```bash
git log --diff-filter=D --summary | grep filename
```

**Restore file from specific commit:**
```bash
git checkout <commit-hash> -- path/to/file
```

### GitHub Resources

- [About branch protections](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [About CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [About required status checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches#require-status-checks-before-merging)

---

## Lessons Learned

1. **Trust, but Verify**
   - Even automated systems can make mistakes
   - Always manually verify critical changes

2. **Automate Protection**
   - CI/CD checks catch issues before they hit production
   - Pre-commit hooks prevent local mistakes

3. **Document Everything**
   - Clear commit messages save hours of debugging
   - Incident reports prevent repeated mistakes

4. **Review Religiously**
   - Code review catches what automation misses
   - Two pairs of eyes are better than one

5. **Protect Critical Assets**
   - Not all files are equal
   - Identify and protect your most critical code

---

## Conclusion

The incident of 2025-11-10 (BUG-00366) taught us valuable lessons about git workflow and file management. By implementing these best practices, we can prevent similar incidents in the future.

**Key Principles:**

1. **Prevention:** Use automated checks and branch protection
2. **Verification:** Always review changes before merging
3. **Documentation:** Document all deletions and changes
4. **Recovery:** Know how to restore files from git history
5. **Learning:** Turn incidents into improvements

**Remember:** Every file deletion should be intentional, documented, and reviewed.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Related Incident:** BUG-00366
**Maintained By:** Development Team

---

**Questions or Suggestions?**

If you have questions about these best practices or suggestions for improvement, please:
1. Create an issue in the repository
2. Discuss in team meetings
3. Submit a pull request with improvements

**Stay vigilant. Protect your code. Document everything.**
