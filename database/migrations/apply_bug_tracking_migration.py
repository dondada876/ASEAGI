#!/usr/bin/env python3
"""
Apply bug tracking columns migration to Supabase
This script adds the missing columns needed for automatic bug creation
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    import psycopg2
    from urllib.parse import urlparse
except ImportError:
    print("ERROR: psycopg2 not installed. Install with: pip install psycopg2-binary")
    sys.exit(1)

# Get Supabase connection details
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')  # Need the DB password, not API key

if not SUPABASE_DB_PASSWORD:
    print("=" * 80)
    print("SUPABASE DATABASE PASSWORD REQUIRED")
    print("=" * 80)
    print()
    print("This script needs direct database access to add columns.")
    print()
    print("Option 1: Run SQL manually in Supabase SQL Editor")
    print("-" * 80)
    print("1. Go to: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/sql")
    print("2. Click 'New query'")
    print("3. Copy and paste the SQL from:")
    print(f"   {Path(__file__).parent}/add_bug_tracking_columns.sql")
    print("4. Click 'Run' to execute")
    print()
    print("Option 2: Provide database password")
    print("-" * 80)
    print("1. Get your database password from:")
    print("   https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/settings/database")
    print("2. Run this script with:")
    print(f"   SUPABASE_DB_PASSWORD='your-password' python3 {Path(__file__).name}")
    print()
    print("=" * 80)

    # Show the SQL that needs to be run
    sql_file = Path(__file__).parent / "add_bug_tracking_columns.sql"
    if sql_file.exists():
        print("\nSQL TO RUN:")
        print("=" * 80)
        print(sql_file.read_text())
        print("=" * 80)

    sys.exit(1)

# Parse Supabase URL to get host
parsed = urlparse(SUPABASE_URL)
db_host = parsed.hostname.replace('jvjlhxodmbkodzmggwpu', 'db.jvjlhxodmbkodzmggwpu')

print("Connecting to Supabase database...")
print(f"Host: {db_host}")

try:
    # Connect to Supabase database
    conn = psycopg2.connect(
        host=db_host,
        database='postgres',
        user='postgres',
        password=SUPABASE_DB_PASSWORD,
        port=5432
    )

    cursor = conn.cursor()

    # Read SQL migration
    sql_file = Path(__file__).parent / "add_bug_tracking_columns.sql"
    sql = sql_file.read_text()

    print("\nExecuting migration...")
    print("-" * 80)

    # Execute migration
    cursor.execute(sql)
    conn.commit()

    print("✅ Migration executed successfully!")

    # Verify columns were added
    cursor.execute("""
        SELECT column_name, data_type, column_default
        FROM information_schema.columns
        WHERE table_name = 'bugs'
        AND column_name IN ('occurrence_count', 'first_occurred_at', 'last_occurred_at')
        ORDER BY column_name
    """)

    results = cursor.fetchall()

    if results:
        print("\n✅ Verified new columns:")
        for col_name, data_type, default_val in results:
            print(f"   - {col_name:20} {data_type:30} DEFAULT {default_val}")

    cursor.close()
    conn.close()

    print("\n" + "=" * 80)
    print("✅ BUG TRACKING MIGRATION COMPLETE")
    print("=" * 80)

except psycopg2.Error as e:
    print(f"\n❌ Database error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
