# Branch Protection Setup Guide

**Created:** 2025-11-10
**Purpose:** Configure GitHub branch protection rules to prevent production file deletions
**Related:** BUG-00366, docs/GIT_WORKFLOW_BEST_PRACTICES.md

---

## Overview

This guide walks through setting up branch protection rules on GitHub to prevent accidental file deletions and enforce code review requirements.

**Time Required:** 5-10 minutes
**Prerequisites:** Admin access to the GitHub repository

---

## Why Branch Protection?

After the incident documented in BUG-00366, where 9 production files were accidentally deleted during a branch operation, we're implementing multi-layer protection:

1. **GitHub Actions** - Automated file existence checks ✅ (Already implemented)
2. **CODEOWNERS** - Mandatory code review for critical files ✅ (Already implemented)
3. **Branch Protection Rules** - Enforce checks before merging ⏳ (This guide)

---

## Step-by-Step Setup

### Step 1: Navigate to Branch Protection Settings

1. Go to your GitHub repository: https://github.com/dondada876/ASEAGI
2. Click **Settings** (top menu bar)
3. In the left sidebar, click **Branches** (under "Code and automation")
4. Under "Branch protection rules", click **Add rule** or **Add branch protection rule**

### Step 2: Configure Main Branch Protection

#### Basic Settings

1. **Branch name pattern:** `main`
   - This will protect your main branch

2. **Require a pull request before merging:** ✅ Checked
   - **Required approvals:** 1 (minimum)
   - ✅ **Dismiss stale pull request approvals when new commits are pushed**
   - ✅ **Require review from Code Owners** (enforces CODEOWNERS file)

3. **Require status checks to pass before merging:** ✅ Checked
   - ✅ **Require branches to be up to date before merging**
   - **Status checks that are required:**
     - Search for and select: `Verify Critical Files Exist` (from critical-files-check workflow)
     - If not available yet, merge PR #3 first, then come back to add it

4. **Require conversation resolution before merging:** ✅ Checked
   - Ensures all PR comments are resolved

5. **Require signed commits:** ⬜ Optional
   - Recommended for security, but not required

6. **Require linear history:** ⬜ Optional
   - Can be enabled to enforce clean git history

7. **Include administrators:** ✅ Checked
   - **Important:** Applies rules to admins too (prevents bypass)

8. **Allow force pushes:** ⬜ Unchecked (default)
   - **Never allow force pushes to main**

9. **Allow deletions:** ⬜ Unchecked (default)
   - **Never allow branch deletion**

#### Additional Settings (Optional but Recommended)

10. **Require deployments to succeed before merging:** ⬜ Optional
    - Enable if you have deployment workflows

11. **Lock branch:** ⬜ Not recommended
    - Would make branch read-only (too restrictive)

12. **Do not allow bypassing the above settings:** ✅ Checked
    - Prevents admin override (enforces rules strictly)

### Step 3: Save the Rule

1. Scroll to the bottom
2. Click **Create** (or **Save changes** if editing existing rule)
3. Confirm the settings are active

---

## Step 4: Test the Protection

After setting up branch protection, test that it works:

### Test 1: Verify PR Requirements

```bash
# Create test branch
git checkout -b test/branch-protection
echo "test" > test-file.txt
git add test-file.txt
git commit -m "Test: Verify branch protection"
git push origin test/branch-protection

# Try to merge without PR (should fail)
git checkout main
git merge test/branch-protection  # Should be blocked
```

**Expected result:** Cannot push directly to main, must create PR

### Test 2: Verify Status Checks

1. Create PR from test branch
2. Go to PR page on GitHub
3. Verify "Verify Critical Files Exist" check runs automatically
4. Verify check must pass before merge button becomes available

### Test 3: Verify Code Owner Review

1. Modify a file in CODEOWNERS (e.g., `scanners/telegram_bot_simple.py`)
2. Create PR
3. Verify PR requires review from @dondada876 before merging

---

## Additional Protection: Development Branch

For larger projects, also protect `develop` branch:

1. Add another branch protection rule
2. **Branch name pattern:** `develop`
3. Use similar settings as `main`, but with:
   - Required approvals: 1 (can be same or different)
   - Allow force pushes: Can be enabled for development flexibility
   - Include administrators: ⬜ Can be unchecked for development

---

## Branch Protection Rules Summary

Once configured, here's what will happen:

### ✅ What's Protected

1. **No Direct Pushes to Main**
   - All changes must go through PR
   - Cannot bypass with force push

2. **Mandatory Code Review**
   - At least 1 approval required
   - Code owners must approve changes to their files
   - Stale approvals dismissed on new commits

3. **Automated Checks Required**
   - Critical files existence check must pass
   - Python syntax validation must pass
   - File deletion warnings displayed

4. **Clean PR Process**
   - All conversations must be resolved
   - Branch must be up to date with main
   - No direct deletions allowed

### ⚠️ What Can Still Happen

Even with protection, these scenarios require vigilance:

1. **Approved Malicious PR**
   - If reviewer approves file deletion, it will merge
   - **Prevention:** Multiple reviewers, clear PR descriptions

2. **Force Push with Admin Override**
   - Admin can temporarily disable protection
   - **Prevention:** "Do not allow bypassing" setting

3. **Repository Settings Changes**
   - Admin can modify/remove protection rules
   - **Prevention:** Audit logs, team awareness

---

## Verification Checklist

After setup, verify all protections are active:

```bash
# Test checklist
□ Cannot push directly to main
□ PR required for all changes
□ Status checks run automatically
□ Code owner review required for critical files
□ Force push to main blocked
□ Branch deletion blocked
□ Admin included in rules (no bypass)
```

---

## Monitoring & Maintenance

### Regular Checks (Monthly)

1. **Review Branch Protection Settings**
   - Go to Settings → Branches
   - Verify all rules still active
   - Check for any changes/overrides

2. **Review CODEOWNERS File**
   - Ensure all critical files still listed
   - Update owners if team changes
   - Add new critical files as needed

3. **Review GitHub Actions Workflow**
   - Check `critical-files-check.yml` still runs
   - Verify it catches missing files
   - Update file list as needed

### After Major Changes

If you add new critical production files:

1. Update `.github/workflows/critical-files-check.yml`
   - Add new file to `CRITICAL_FILES` array

2. Update `.github/CODEOWNERS`
   - Add new file with owner

3. Test protection works for new files

---

## Troubleshooting

### Problem: Status Check Not Showing Up

**Solution:**
1. Merge PR #3 first (adds the workflow)
2. Wait for first workflow run to complete
3. Status check will appear in list after first run
4. Go back to branch protection settings and add it

### Problem: Cannot Enable "Require review from Code Owners"

**Solution:**
- Ensure `.github/CODEOWNERS` file exists in repository
- File must be in `.github/` or root directory
- At least one valid GitHub username in file
- Owner must have write access to repository

### Problem: Accidentally Deleted Protection Rule

**Solution:**
1. Check GitHub audit log: Settings → Audit log
2. Recreate rule using this guide
3. Document incident in bug tracker
4. Review who had access/what happened

### Problem: Need Emergency Override

**Only for true emergencies:**

1. Document reason in writing first
2. Temporarily disable specific check
3. Make critical change
4. Immediately re-enable protection
5. Create follow-up issue for proper fix
6. Log incident in bug tracker

---

## Additional Resources

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [CODEOWNERS Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [GitHub Actions Status Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)
- [Best Practices Guide](./GIT_WORKFLOW_BEST_PRACTICES.md) (Local)

---

## Quick Command Reference

```bash
# View current branch protection (gh CLI)
gh api repos/dondada876/ASEAGI/branches/main/protection

# List protected branches
gh api repos/dondada876/ASEAGI/branches --jq '.[].protection.enabled'

# View required status checks
gh api repos/dondada876/ASEAGI/branches/main/protection/required_status_checks

# Enable branch protection (example - prefer UI)
gh api -X PUT repos/dondada876/ASEAGI/branches/main/protection \
  -f required_pull_request_reviews='{"required_approving_review_count":1}' \
  -f enforce_admins='true'
```

---

## Summary

After completing this setup, your repository will have:

✅ **3-Layer Protection System:**
1. GitHub Actions (automated file checks)
2. CODEOWNERS (mandatory reviews)
3. Branch Protection (enforced workflows)

✅ **Prevents:**
- Direct pushes to main
- Unreviewed code changes
- File deletions without approval
- Bypassing checks with force push

✅ **Requires:**
- Pull requests for all changes
- Code owner approval for critical files
- Passing automated checks
- Conversation resolution

**Result:** Future incidents like BUG-00366 (file deletion) will be prevented by multiple safeguards.

---

**Setup Time:** ~10 minutes
**Maintenance:** Monthly review recommended
**Last Updated:** 2025-11-10

---

*Questions? See [GIT_WORKFLOW_BEST_PRACTICES.md](./GIT_WORKFLOW_BEST_PRACTICES.md) for more details.*
