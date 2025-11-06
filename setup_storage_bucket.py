#!/usr/bin/env python3
"""
Setup Supabase Storage Bucket for Document Storage
Creates 'documents' bucket with proper public access policies
"""

import sys
from pathlib import Path

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

try:
    from supabase import create_client
except ImportError:
    print("❌ Please install: pip install supabase")
    sys.exit(1)

try:
    import toml
except ImportError:
    print("❌ Please install: pip install toml")
    sys.exit(1)


def main():
    """Setup storage bucket."""

    # Load credentials
    secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
    if not secrets_path.exists():
        print(f"❌ secrets.toml not found at: {secrets_path}")
        sys.exit(1)

    secrets = toml.load(secrets_path)
    SUPABASE_URL = secrets.get('SUPABASE_URL')
    SUPABASE_KEY = secrets.get('SUPABASE_KEY')

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in secrets.toml")
        sys.exit(1)

    print(f"\n✅ Connecting to Supabase: {SUPABASE_URL}\n")

    # Initialize client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Bucket configuration
    bucket_name = "documents"

    print(f"🪣 Setting up '{bucket_name}' bucket...\n")

    try:
        # Try to create bucket (will fail if already exists)
        supabase.storage.create_bucket(
            bucket_name,
            options={
                "public": True,  # Public read access for URLs
                "fileSizeLimit": 52428800,  # 50MB limit
                "allowedMimeTypes": [
                    "image/jpeg",
                    "image/jpg",
                    "image/png",
                    "image/gif",
                    "application/pdf"
                ]
            }
        )
        print(f"✅ Created '{bucket_name}' bucket successfully!")

    except Exception as e:
        error_msg = str(e).lower()
        if 'already exists' in error_msg or 'duplicate' in error_msg:
            print(f"✅ Bucket '{bucket_name}' already exists - that's OK!")
        else:
            print(f"⚠️ Error creating bucket: {e}")
            print(f"   This might be OK if the bucket already exists.")

    # Test bucket access
    print(f"\n📋 Testing bucket access...")

    try:
        buckets = supabase.storage.list_buckets()

        # Find our bucket
        our_bucket = None
        for bucket in buckets:
            if bucket.name == bucket_name:
                our_bucket = bucket
                break

        if our_bucket:
            print(f"✅ Bucket '{bucket_name}' is accessible!")
            print(f"   • Public: {our_bucket.public}")
            print(f"   • ID: {our_bucket.id}")
        else:
            print(f"⚠️ Bucket '{bucket_name}' not found in list")
            print(f"   Available buckets: {[b.name for b in buckets]}")

    except Exception as e:
        print(f"⚠️ Could not list buckets: {e}")

    # Test folder structure
    print(f"\n📁 Folder structure will be:")
    print(f"   {bucket_name}/")
    print(f"   ├── originals/    (Full resolution images)")
    print(f"   └── thumbnails/   (200x200 thumbnails)")

    print(f"\n✅ Storage setup complete!")
    print(f"\n🔗 Your documents will be accessible at:")
    print(f"   {SUPABASE_URL}/storage/v1/object/public/{bucket_name}/...")

    print(f"\n💡 Next steps:")
    print(f"   1. Test the bot: python telegram_document_bot_enhanced.py")
    print(f"   2. Send an image from your phone to @ASIAGI_bot")
    print(f"   3. Images will be stored in Supabase Storage automatically")


if __name__ == '__main__':
    main()
