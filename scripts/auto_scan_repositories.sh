#!/bin/bash
################################################################################
# Repository Sentinel - Automatic Scanner
################################################################################
# Automatically scans repositories and updates the inventory database
#
# Usage:
#   ./auto_scan_repositories.sh
#
# To run automatically with cron:
#   crontab -e
#   Add line: 0 2 * * * /home/user/ASEAGI/scripts/auto_scan_repositories.sh
#
# This will run daily at 2:00 AM
################################################################################

# Set strict error handling
set -euo pipefail

# Logging
LOG_FILE="/home/user/ASEAGI/logs/repository_scanner.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "======================================"
log "Repository Sentinel Auto Scanner START"
log "======================================"

# Load environment variables
if [ -f "/home/user/ASEAGI/.env" ]; then
    source "/home/user/ASEAGI/.env"
    log "✓ Environment variables loaded"
else
    log "⚠ Warning: .env file not found"
fi

# List of repositories to scan
REPOS=(
    "/home/user/ASEAGI"
    # Add more repository paths here
    # "/path/to/other/repo"
)

# Scan each repository
TOTAL_SCANNED=0
TOTAL_FAILED=0

for repo in "${REPOS[@]}"; do
    log "Scanning: $repo"

    if [ -d "$repo" ]; then
        if python3 /home/user/ASEAGI/scanners/repository_scanner.py "$repo" --scan-type incremental >> "$LOG_FILE" 2>&1; then
            log "✅ Successfully scanned: $repo"
            ((TOTAL_SCANNED++))
        else
            log "❌ Failed to scan: $repo"
            ((TOTAL_FAILED++))
        fi
    else
        log "⚠ Repository not found: $repo"
        ((TOTAL_FAILED++))
    fi

    # Small delay between scans
    sleep 2
done

log "======================================"
log "Repository Sentinel Auto Scanner END"
log "Scanned: $TOTAL_SCANNED | Failed: $TOTAL_FAILED"
log "======================================"

# Optional: Send notification (if Telegram bot configured)
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
    MESSAGE="📊 Repository Sentinel Scan Complete%0A%0A✅ Scanned: $TOTAL_SCANNED repos%0A❌ Failed: $TOTAL_FAILED repos%0A⏰ Time: $(date '+%Y-%m-%d %H:%M')"

    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=${MESSAGE}" \
        > /dev/null

    log "✓ Telegram notification sent"
fi

exit 0
