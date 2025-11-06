"""
Fix secrets handling in all dashboard files
"""
import re
import os

# List of files to update
files_to_update = [
    'supabase_dashboard.py',
    'court_events_dashboard.py',
    'legal_intelligence_dashboard.py',
    'ceo_global_dashboard.py',
    'error_log_uploader.py',
]

# Old pattern to find
old_pattern = re.compile(
    r"url = st\.secrets\.get\('SUPABASE_URL'\) if hasattr\(st, 'secrets'\) else os\.environ\.get\('SUPABASE_URL'(, '[^']+')?\)\s*\n\s*key = st\.secrets\.get\('SUPABASE_KEY'\) if hasattr\(st, 'secrets'\) else os\.environ\.get\('SUPABASE_KEY'(, '[^']+')?\)",
    re.MULTILINE
)

def fix_file(filename):
    """Fix secrets handling in a single file"""
    if not os.path.exists(filename):
        print(f"⚠️  File not found: {filename}")
        return False

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already fixed
    if 'st.secrets["SUPABASE_URL"]' in content:
        print(f"✅ Already fixed: {filename}")
        return False

    # Check if needs fixing
    if "st.secrets.get('SUPABASE_URL')" not in content:
        print(f"⚠️  No secrets pattern found: {filename}")
        return False

    # Find the pattern
    match = old_pattern.search(content)
    if not match:
        print(f"⚠️  Pattern not matched: {filename}")
        return False

    # Extract defaults if present
    url_default = match.group(1) if match.group(1) else ", 'https://jvjlhxodmbkodzmggwpu.supabase.co'"
    key_default = match.group(2) if match.group(2) else ", 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c'"

    # Clean up defaults (remove leading comma and space)
    url_default_clean = url_default[2:] if url_default.startswith(', ') else url_default
    key_default_clean = key_default[2:] if key_default.startswith(', ') else key_default

    # New pattern
    new_code = f"""try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except (KeyError, FileNotFoundError):
        url = os.environ.get('SUPABASE_URL'{url_default})
        key = os.environ.get('SUPABASE_KEY'{key_default})"""

    # Replace
    new_content = old_pattern.sub(new_code, content)

    # Write back
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Fixed: {filename}")
    return True

# Main
print("Fixing secrets handling in dashboard files...\n")

fixed_count = 0
for filename in files_to_update:
    if fix_file(filename):
        fixed_count += 1

print(f"\n📊 Summary: Fixed {fixed_count} files")
