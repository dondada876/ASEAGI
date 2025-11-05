#!/bin/bash
#
# Setup automated daily backups using cron
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/backup.sh"

echo "ASEAGI Automated Backup Setup"
echo "=============================="
echo ""

# Make scripts executable
chmod +x "$BACKUP_SCRIPT"
chmod +x "$SCRIPT_DIR/restore.sh"

echo "✓ Scripts made executable"
echo ""

# Check if cron is available
if ! command -v crontab &> /dev/null; then
    echo "WARNING: crontab not found. Manual scheduling required."
    echo ""
    echo "To run backup manually:"
    echo "  $BACKUP_SCRIPT"
    exit 1
fi

echo "Choose backup schedule:"
echo "1. Daily at 2:00 AM (recommended)"
echo "2. Daily at 9:00 PM"
echo "3. Every 12 hours"
echo "4. Every 6 hours"
echo "5. Custom"
echo ""
read -p "Select option (1-5): " SCHEDULE_OPTION

case $SCHEDULE_OPTION in
    1)
        CRON_TIME="0 2 * * *"
        DESCRIPTION="Daily at 2:00 AM"
        ;;
    2)
        CRON_TIME="0 21 * * *"
        DESCRIPTION="Daily at 9:00 PM"
        ;;
    3)
        CRON_TIME="0 */12 * * *"
        DESCRIPTION="Every 12 hours"
        ;;
    4)
        CRON_TIME="0 */6 * * *"
        DESCRIPTION="Every 6 hours"
        ;;
    5)
        echo "Enter custom cron schedule (e.g., '0 3 * * *' for 3 AM daily):"
        read -p "Cron schedule: " CRON_TIME
        DESCRIPTION="Custom schedule: $CRON_TIME"
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

# Create cron job
CRON_JOB="$CRON_TIME $BACKUP_SCRIPT >> $HOME/ASEAGI-backups/backup-cron.log 2>&1"

# Check if job already exists
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo ""
    echo "Backup job already exists in crontab."
    read -p "Replace it? (yes/no): " REPLACE
    if [ "$REPLACE" == "yes" ]; then
        # Remove old job
        crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" | crontab -
        echo "Old job removed."
    else
        echo "Setup cancelled."
        exit 0
    fi
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "✓ Automated backup configured!"
echo ""
echo "Schedule: $DESCRIPTION"
echo "Cron job: $CRON_TIME"
echo "Backup directory: $HOME/ASEAGI-backups"
echo "Max backups kept: 30"
echo ""
echo "To view cron jobs: crontab -l"
echo "To remove this job: crontab -e (then delete the line)"
echo ""
echo "Current cron jobs:"
echo "=================="
crontab -l
echo ""
echo "To run backup immediately: $BACKUP_SCRIPT"
echo "To restore from backup: $SCRIPT_DIR/restore.sh"
echo ""
