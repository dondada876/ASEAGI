#!/bin/bash
#
# ASEAGI Restore Script
# Restores from backup with safety checks
#

set -e

BACKUP_DIR="$HOME/ASEAGI-backups"
RESTORE_TO="$HOME/ASEAGI-restored"

# Function to list available backups
list_backups() {
    echo "Available backups:"
    echo "=================="
    ls -lht "$BACKUP_DIR"/ASEAGI-backup-*.tar.gz 2>/dev/null | nl -w2 -s'. ' || {
        echo "No backups found in $BACKUP_DIR"
        exit 1
    }
    echo ""
    echo "Latest: $BACKUP_DIR/ASEAGI-latest.tar.gz"
    echo ""
}

# Show usage if no argument
if [ $# -eq 0 ]; then
    echo "ASEAGI Restore Script"
    echo "====================="
    echo ""
    list_backups
    echo "Usage:"
    echo "  $0 latest              - Restore from latest backup"
    echo "  $0 <backup-file>       - Restore from specific backup file"
    echo "  $0 list                - List all available backups"
    echo ""
    echo "Examples:"
    echo "  $0 latest"
    echo "  $0 $BACKUP_DIR/ASEAGI-backup-20251105-143022.tar.gz"
    exit 0
fi

# List command
if [ "$1" == "list" ]; then
    list_backups
    exit 0
fi

# Determine backup file
if [ "$1" == "latest" ]; then
    BACKUP_FILE="$BACKUP_DIR/ASEAGI-latest.tar.gz"
else
    BACKUP_FILE="$1"
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "ASEAGI Restore"
echo "=============="
echo "Backup file: $BACKUP_FILE"
echo "Restore to: $RESTORE_TO"
echo ""

# Safety check
if [ -d "$RESTORE_TO" ]; then
    echo "WARNING: Restore directory already exists: $RESTORE_TO"
    read -p "Remove and continue? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "Restore cancelled."
        exit 0
    fi
    rm -rf "$RESTORE_TO"
fi

# Create restore directory
mkdir -p "$(dirname "$RESTORE_TO")"

# Extract backup
echo "Extracting backup..."
tar -xzf "$BACKUP_FILE" -C "$(dirname "$RESTORE_TO")"

# Rename to restore directory
mv "$(dirname "$RESTORE_TO")/ASEAGI" "$RESTORE_TO" 2>/dev/null || true

echo ""
echo "✓ Restore completed successfully!"
echo ""
echo "Restored to: $RESTORE_TO"
echo ""
echo "Next steps:"
echo "1. Verify the restored files: cd $RESTORE_TO"
echo "2. If everything looks good, you can replace the original:"
echo "   mv /home/user/ASEAGI /home/user/ASEAGI-old-backup"
echo "   mv $RESTORE_TO /home/user/ASEAGI"
echo ""
