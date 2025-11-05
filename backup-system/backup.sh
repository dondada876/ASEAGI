#!/bin/bash
#
# ASEAGI Automated Backup Script
# Creates timestamped backups with rotation
# For Ashe - Protecting critical legal documentation
#

set -e  # Exit on error

# Configuration
PROJECT_DIR="/home/user/ASEAGI"
BACKUP_DIR="$HOME/ASEAGI-backups"
MAX_BACKUPS=30  # Keep last 30 backups (1 month if daily)
LOG_FILE="$BACKUP_DIR/backup.log"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Timestamp for this backup
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="ASEAGI-backup-$TIMESTAMP"
BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME.tar.gz"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Starting ASEAGI backup..."
log "Backup name: $BACKUP_NAME"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    log "ERROR: Project directory not found: $PROJECT_DIR"
    exit 1
fi

# Create the backup
log "Creating compressed backup..."
cd "$(dirname "$PROJECT_DIR")"
tar -czf "$BACKUP_FILE" \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.git/objects' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    "$(basename "$PROJECT_DIR")" 2>&1 | tee -a "$LOG_FILE"

# Check if backup was created successfully
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "✓ Backup created successfully: $BACKUP_FILE ($BACKUP_SIZE)"
else
    log "✗ ERROR: Backup failed"
    exit 1
fi

# Rotate old backups (keep only last MAX_BACKUPS)
log "Rotating old backups (keeping last $MAX_BACKUPS)..."
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/ASEAGI-backup-*.tar.gz 2>/dev/null | wc -l)

if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    REMOVE_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
    log "Removing $REMOVE_COUNT old backup(s)..."
    ls -1t "$BACKUP_DIR"/ASEAGI-backup-*.tar.gz | tail -n "$REMOVE_COUNT" | xargs rm -f
    log "✓ Old backups removed"
fi

# Display current backup status
TOTAL_BACKUPS=$(ls -1 "$BACKUP_DIR"/ASEAGI-backup-*.tar.gz 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "Current status: $TOTAL_BACKUPS backups, total size: $TOTAL_SIZE"

# Create a 'latest' symlink for easy access
ln -sf "$BACKUP_FILE" "$BACKUP_DIR/ASEAGI-latest.tar.gz"
log "✓ Latest backup symlink created"

log "Backup completed successfully!"
log "=========================================="

# Display summary
echo ""
echo "📦 BACKUP SUMMARY"
echo "=================="
echo "Backup file: $BACKUP_FILE"
echo "Size: $BACKUP_SIZE"
echo "Total backups: $TOTAL_BACKUPS"
echo "Backup directory: $BACKUP_DIR"
echo ""
echo "To restore: tar -xzf $BACKUP_FILE"
echo ""
