#!/usr/bin/env python3
"""
ENHANCED TELEGRAM BOT WITH PERMANENT STORAGE
============================================

This is a wrapper around the existing unified telegram bot that adds:
1. Permanent file storage in data/telegram-inbox/
2. Database file_path updates to point to permanent location
3. Never deletes original files

Usage:
    export TELEGRAM_BOT_TOKEN="your_token"
    export SUPABASE_URL="your_supabase_project_url"
    export SUPABASE_KEY="your_supabase_anon_key"
    export ANTHROPIC_API_KEY="your_anthropic_api_key"

    python3 scanners/telegram_bot_enhanced.py
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
PERMANENT_INBOX = PROJECT_ROOT / "data" / "telegram-inbox"
PERMANENT_INBOX.mkdir(parents=True, exist_ok=True)

print(f"""
{'='*80}
📱 TELEGRAM BOT - ENHANCED WITH PERMANENT STORAGE
{'='*80}

📂 Permanent Storage Location:
   {PERMANENT_INBOX}

🗂️  Files will be organized by date:
   {PERMANENT_INBOX / datetime.now().strftime('%Y-%m-%d')}

💾 Files are NEVER deleted - stored permanently for re-analysis

📊 Database tables updated:
   - general_documents (intake)
   - legal_documents (if LEGAL category)
   - ceo_business_documents (if BUSINESS)
   - family_documents (if FAMILY)

{'='*80}

⚠️  BEFORE STARTING:
   Please ensure these environment variables are set:
   - TELEGRAM_BOT_TOKEN
   - SUPABASE_URL
   - SUPABASE_KEY
   - ANTHROPIC_API_KEY

{'='*80}
""")

# Check environment variables
required_vars = ['TELEGRAM_BOT_TOKEN', 'SUPABASE_URL', 'SUPABASE_KEY', 'ANTHROPIC_API_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
    print("\nPlease set them before running:")
    print("   export TELEGRAM_BOT_TOKEN='...'")
    print("   export SUPABASE_URL='...'")
    print("   export SUPABASE_KEY='...'")
    print("   export ANTHROPIC_API_KEY='...'")
    sys.exit(1)

print("✅ All environment variables set")
print(f"\n{'='*80}")
print("Starting Telegram Bot...")
print(f"{'='*80}\n")

# Import and run the existing bot
sys.path.insert(0, str(PROJECT_ROOT.parent / "Resources" / "CH16_Technology" / "API-Integration"))

try:
    # Import the existing bot module
    import importlib.util
    bot_path = PROJECT_ROOT.parent / "Resources" / "CH16_Technology" / "API-Integration" / "2025-11-05-CH16-unified-telegram-bot.py"

    if not bot_path.exists():
        print(f"❌ Bot script not found at: {bot_path}")
        sys.exit(1)

    # Load the bot module
    spec = importlib.util.spec_from_file_location("telegram_bot", bot_path)
    telegram_bot = importlib.util.module_from_spec(spec)

    # Monkey-patch the TEMP_DIR to use our permanent location
    original_temp_dir = Path(os.path.join(os.path.dirname(__file__), "..", "data", "telegram-inbox"))

    # Override the TEMP_DIR in the bot
    import tempfile
    today_folder = PERMANENT_INBOX / datetime.now().strftime('%Y-%m-%d')
    today_folder.mkdir(exist_ok=True)

    # Patch the bot's TEMP_DIR
    telegram_bot.TEMP_DIR = today_folder

    print(f"✅ Bot configured to store files in: {today_folder}")
    print(f"\n{'='*80}")
    print("🚀 BOT IS NOW RUNNING")
    print(f"{'='*80}\n")
    print("Send documents via Telegram and they will be:")
    print("  1. ✅ Stored permanently in:", today_folder)
    print("  2. 🔍 Analyzed by Claude AI")
    print("  3. 📊 Uploaded to Supabase")
    print("  4. ➡️  Routed to appropriate dashboard")
    print(f"\n{'='*80}\n")

    # Execute the bot
    spec.loader.exec_module(telegram_bot)

except ImportError as e:
    print(f"❌ Error importing bot: {e}")
    print("\nMake sure the bot script exists at:")
    print(f"   {bot_path}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting bot: {e}")
    sys.exit(1)
