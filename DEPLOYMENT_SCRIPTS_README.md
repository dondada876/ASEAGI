# Deployment Scripts

## Active Script

**Use this script for deployment:**
- `deploy-to-droplet.sh` (136 lines)
  - More comprehensive and up-to-date
  - Includes SSH connection testing
  - Handles all 6 dashboard ports (8501-8506)
  - Better error handling

## Deprecated Scripts

- `deploy_to_droplet.sh.deprecated` (106 lines)
  - Old version with underscore naming
  - Only handles 5 ports (outdated)
  - Kept for reference only
  - DO NOT USE

## Usage

```bash
chmod +x deploy-to-droplet.sh
./deploy-to-droplet.sh
```

## Notes

- Always use the hyphenated version (`deploy-to-droplet.sh`)
- The underscore version is deprecated as of Nov 19, 2025
- If you need to modify deployment, edit only `deploy-to-droplet.sh`

---
**Last Updated:** November 19, 2025
