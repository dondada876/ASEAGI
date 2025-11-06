#!/usr/bin/env python3
"""
Telegram Bot Startup Script with Diagnostics
This script ensures only one instance runs and provides helpful debug info
"""

import os
import sys
import signal
import psutil
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

print("=" * 70)
print("TELEGRAM BOT STARTUP - DIAGNOSTIC CHECK")
print("=" * 70)

# Check for existing bot processes
def check_existing_bots():
    """Check if telegram_document_bot.py is already running"""
    current_pid = os.getpid()
    bot_processes = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and 'telegram_document_bot.py' in ' '.join(cmdline):
                if proc.info['pid'] != current_pid:
                    bot_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return bot_processes

# Check for existing instances
existing_bots = check_existing_bots()

if existing_bots:
    print(f"\n⚠️  WARNING: Found {len(existing_bots)} existing bot instance(s) running!")
    print("\nExisting processes:")
    for proc in existing_bots:
        print(f"  - PID {proc.pid}: {' '.join(proc.cmdline())}")

    print("\n⚠️  IMPORTANT: Only ONE bot instance can run at a time!")
    print("Telegram API will reject multiple instances with 'Conflict' error.")

    response = input("\nDo you want to kill existing instances and start fresh? (y/n): ").strip().lower()

    if response == 'y':
        for proc in existing_bots:
            try:
                print(f"Killing process {proc.pid}...")
                proc.kill()
                proc.wait(timeout=5)
                print(f"✅ Killed process {proc.pid}")
            except Exception as e:
                print(f"❌ Error killing process {proc.pid}: {e}")
        print("\n✅ All existing bot instances terminated")
    else:
        print("\n❌ Cancelled. Please manually stop other instances before running bot.")
        sys.exit(1)

# Verify credentials
print("\n" + "=" * 70)
print("CHECKING CREDENTIALS")
print("=" * 70)

try:
    import toml
    secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'

    if not secrets_path.exists():
        print(f"\n❌ Secrets file not found: {secrets_path}")
        print("\nPlease create .streamlit/secrets.toml with:")
        print("  SUPABASE_URL = \"your_url\"")
        print("  SUPABASE_KEY = \"your_key\"")
        print("  TELEGRAM_BOT_TOKEN = \"your_token\"")
        sys.exit(1)

    secrets = toml.load(secrets_path)

    # Check each credential
    missing = []
    if not secrets.get('SUPABASE_URL'):
        missing.append('SUPABASE_URL')
    if not secrets.get('SUPABASE_KEY'):
        missing.append('SUPABASE_KEY')
    if not secrets.get('TELEGRAM_BOT_TOKEN'):
        missing.append('TELEGRAM_BOT_TOKEN')

    if missing:
        print(f"\n❌ Missing credentials in secrets.toml: {', '.join(missing)}")
        sys.exit(1)

    print("\n✅ All credentials found in secrets.toml")

    # Show partial token for verification
    token = secrets.get('TELEGRAM_BOT_TOKEN')
    print(f"   Bot Token: {token[:20]}...{token[-10:]}")

except Exception as e:
    print(f"\n❌ Error loading credentials: {e}")
    sys.exit(1)

# Test Telegram API connection
print("\n" + "=" * 70)
print("TESTING TELEGRAM API CONNECTION")
print("=" * 70)

try:
    import requests

    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            bot_info = data.get('result', {})
            print(f"\n✅ Bot connection successful!")
            print(f"   Bot Username: @{bot_info.get('username')}")
            print(f"   Bot Name: {bot_info.get('first_name')}")
            print(f"   Bot ID: {bot_info.get('id')}")
        else:
            print(f"\n❌ Bot connection failed: {data.get('description')}")
            sys.exit(1)
    else:
        print(f"\n❌ HTTP error {response.status_code}: {response.text}")
        sys.exit(1)

except Exception as e:
    print(f"\n❌ Error testing bot connection: {e}")
    sys.exit(1)

# All checks passed - start the bot
print("\n" + "=" * 70)
print("STARTING TELEGRAM BOT")
print("=" * 70)
print(f"\n📱 Your bot is ready at: @{bot_info.get('username')}")
print("\nTo use the bot:")
print("  1. Open Telegram on your phone")
print(f"  2. Search for: @{bot_info.get('username')}")
print("  3. Send: /start")
print("  4. Upload a document or photo")
print("\nPress Ctrl+C to stop the bot")
print("\n" + "=" * 70)

# Import and run the actual bot
try:
    # Import the main bot module
    import telegram_document_bot

    # Run the bot
    telegram_document_bot.main()

except KeyboardInterrupt:
    print("\n\n🛑 Bot stopped by user (Ctrl+C)")
    sys.exit(0)
except Exception as e:
    print(f"\n\n❌ Bot error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
