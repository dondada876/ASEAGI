#!/usr/bin/env python3
"""
Test Telegram bot connection
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import toml
from pathlib import Path

# Load bot token
secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
secrets = toml.load(secrets_path)
bot_token = secrets.get('TELEGRAM_BOT_TOKEN')

print("=" * 60)
print("TELEGRAM BOT CONNECTION TEST")
print("=" * 60)
print(f"\nBot Token: {bot_token[:20]}...{bot_token[-10:]}")

# Test 1: Check if token is valid format
if ':' in bot_token and len(bot_token) > 30:
    print("Token format: OK")
else:
    print("Token format: INVALID")
    sys.exit(1)

# Test 2: Try to get bot info from Telegram API
try:
    import requests

    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            bot_info = data.get('result', {})
            print(f"\nBot Connection: SUCCESS")
            print(f"Bot Username: @{bot_info.get('username')}")
            print(f"Bot Name: {bot_info.get('first_name')}")
            print(f"Bot ID: {bot_info.get('id')}")
            print(f"Can Read Messages: {bot_info.get('can_read_all_group_messages', False)}")
        else:
            print(f"\nBot Connection: FAILED")
            print(f"Error: {data.get('description')}")
            sys.exit(1)
    else:
        print(f"\nBot Connection: FAILED")
        print(f"HTTP Status: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)

except Exception as e:
    print(f"\nError testing connection: {e}")
    sys.exit(1)

# Test 3: Check for pending updates
try:
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        updates = data.get('result', [])

        print(f"\nPending Updates: {len(updates)}")

        if updates:
            print("\nMost Recent Messages:")
            for update in updates[-5:]:  # Show last 5 updates
                if 'message' in update:
                    msg = update['message']
                    user = msg.get('from', {})
                    text = msg.get('text', msg.get('caption', '[No text]'))
                    print(f"  - From {user.get('first_name', 'Unknown')}: {text[:50]}")
        else:
            print("\nNo pending messages found.")
            print("This could mean:")
            print("  1. Bot hasn't received any messages yet")
            print("  2. Another bot instance already consumed the updates")

except Exception as e:
    print(f"\nError checking updates: {e}")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print("\n1. Open Telegram and search for: @" + bot_info.get('username', 'your_bot'))
print("2. Send /start to the bot")
print("3. Run this test again to see if message appears")
print("\nIf bot still doesn't respond:")
print("- Make sure you're messaging the correct bot username")
print("- Try stopping and restarting the bot script")
print()
