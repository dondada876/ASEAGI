# ASEAGI Automated Backup System

**For Ashe - Protecting Critical Legal Documentation** ⚖️

This backup system ensures your critical legal documents and code are protected with automated, timestamped backups.

---

## 🚀 Quick Start

### 1. Set Up Automated Backups (One-Time)

```bash
cd /home/user/ASEAGI/backup-system
chmod +x setup-cron.sh
./setup-cron.sh
```

This will:
- Make all scripts executable
- Set up daily automated backups
- Configure backup rotation (keeps last 30 backups)

### 2. Run Manual Backup (Anytime)

```bash
./backup.sh
```

### 3. Restore from Backup (If Needed)

```bash
# List available backups
./restore.sh list

# Restore latest backup
./restore.sh latest

# Restore specific backup
./restore.sh /home/user/ASEAGI-backups/ASEAGI-backup-20251105-143022.tar.gz
```

---

## 📂 What Gets Backed Up

- All source code
- All documentation (including the new docs/legal-scoring-system/)
- Database files
- Configuration files
- Git repository (excluding large object files)

**Excluded for efficiency:**
- node_modules
- __pycache__
- .pyc files
- .git/objects (large binary objects)

---

## 📍 Backup Location

All backups are stored in:
```
/home/user/ASEAGI-backups/
```

Structure:
```
ASEAGI-backups/
├── ASEAGI-backup-20251105-143022.tar.gz
├── ASEAGI-backup-20251106-020000.tar.gz
├── ASEAGI-backup-20251107-020000.tar.gz
├── ...
├── ASEAGI-latest.tar.gz (symlink to most recent)
├── backup.log (operation log)
└── backup-cron.log (cron execution log)
```

---

## ⚙️ Configuration

Edit `backup.sh` to customize:

```bash
MAX_BACKUPS=30        # Number of backups to keep (default: 30)
BACKUP_DIR="..."      # Where to store backups
```

---

## 📅 Backup Schedules

### Recommended Schedule Options:

1. **Daily at 2:00 AM** (recommended for most users)
   - Runs during off-hours
   - Daily protection
   - Minimal disruption

2. **Daily at 9:00 PM**
   - Before end of day
   - Good for active development

3. **Every 12 hours**
   - More frequent protection
   - 2x daily coverage

4. **Every 6 hours**
   - Maximum protection
   - For critical active development

---

## 🔄 Backup Rotation

The system automatically maintains the last **30 backups** (configurable).

- Older backups are automatically deleted
- Prevents disk space issues
- 30 daily backups = 1 month of history

---

## 🛡️ Protection Strategy

This backup system is part of your **3-2-1 backup strategy**:

1. ✅ **Original data** - /home/user/ASEAGI
2. ✅ **Local backup** - /home/user/ASEAGI-backups (this system)
3. ✅ **Git/GitHub** - Remote version control
4. 🎯 **Recommended:** Add cloud backup (Google Drive, Dropbox, etc.)

---

## 📊 Monitoring Backups

### Check backup status:
```bash
ls -lht ~/ASEAGI-backups/ASEAGI-backup-*.tar.gz | head -10
```

### View backup log:
```bash
tail -f ~/ASEAGI-backups/backup.log
```

### View cron execution log:
```bash
tail -f ~/ASEAGI-backups/backup-cron.log
```

### Check cron jobs:
```bash
crontab -l
```

---

## 🔧 Manual Operations

### Run backup immediately:
```bash
cd /home/user/ASEAGI/backup-system
./backup.sh
```

### List all backups:
```bash
./restore.sh list
```

### Check latest backup size:
```bash
du -h ~/ASEAGI-backups/ASEAGI-latest.tar.gz
```

### Extract backup to specific location:
```bash
tar -xzf ~/ASEAGI-backups/ASEAGI-latest.tar.gz -C /path/to/restore/
```

---

## ⚠️ Important Notes

### For Critical Legal Work:

1. **Before Major Changes:**
   ```bash
   ./backup.sh  # Run manual backup
   ```

2. **Before Court Deadlines:**
   - Verify latest backup exists
   - Consider creating additional backup to external drive

3. **After Significant Progress:**
   - Run manual backup
   - Consider pushing to Git immediately

### Security:

- Backups contain all your data
- Keep backup directory secure
- Consider encrypting sensitive backups
- Don't delete old backups before major court events

---

## 🆘 Emergency Recovery

### If original directory is lost/corrupted:

```bash
# 1. Restore latest backup
cd /home/user/ASEAGI/backup-system
./restore.sh latest

# 2. Verify restored files
cd ~/ASEAGI-restored
ls -la

# 3. Replace original (if verified)
mv /home/user/ASEAGI /home/user/ASEAGI-corrupted
mv ~/ASEAGI-restored /home/user/ASEAGI

# 4. Verify git status
cd /home/user/ASEAGI
git status
```

---

## 📞 Troubleshooting

### Cron job not running?

Check cron is running:
```bash
systemctl status cron  # or 'crond' on some systems
```

Check cron logs:
```bash
tail -f ~/ASEAGI-backups/backup-cron.log
```

### Backup fails?

Check permissions:
```bash
ls -l /home/user/ASEAGI/backup-system/backup.sh
# Should show: -rwxr-xr-x (executable)
```

Check disk space:
```bash
df -h ~
```

### Need to remove automated backups?

```bash
crontab -e
# Delete the line containing 'backup.sh'
# Save and exit
```

---

## 🎯 Best Practices

1. **Test restore** at least once to verify backups work
2. **Monitor logs** periodically to ensure backups are running
3. **Keep multiple** backup locations (local + cloud + git)
4. **Before major changes**, run manual backup
5. **After critical work**, verify backup succeeded
6. **Document restoration** steps for team members

---

## 📁 Additional Backup Options

### Copy to External Drive:

```bash
cp ~/ASEAGI-backups/ASEAGI-latest.tar.gz /media/external-drive/
```

### Sync to Cloud (Example with rclone):

```bash
# Install rclone first: https://rclone.org/
rclone copy ~/ASEAGI-backups remote:ASEAGI-backups
```

### Create Encrypted Backup:

```bash
gpg -c ~/ASEAGI-backups/ASEAGI-latest.tar.gz
# Creates: ASEAGI-latest.tar.gz.gpg (encrypted)
```

---

## 📝 Maintenance

### Monthly Tasks:

1. Verify backups are running (check logs)
2. Test a restore operation
3. Review disk space usage
4. Consider archiving old backups to external storage

---

## 🎓 Understanding the Scripts

### backup.sh
- Creates compressed backup with timestamp
- Rotates old backups automatically
- Logs all operations
- Creates 'latest' symlink for convenience

### restore.sh
- Lists available backups
- Safely restores to separate directory
- Prevents accidental overwrites

### setup-cron.sh
- Configures automated scheduling
- Multiple schedule options
- Handles existing cron jobs

---

**Mission:** Ensure no critical legal documentation is ever lost.
**Purpose:** Protect the tools that protect children.

*"When children speak, truth must roar louder than lies."* ⚖️

---

**Last Updated:** November 2025
**Version:** 1.0
