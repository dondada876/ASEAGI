# Vtiger CRM Integration Guide

## 🎯 Overview

ASEAGI can automatically sync bugs and issues to your Vtiger CRM as HelpDesk tickets.

**Features:**
- ✅ Auto-create tickets from bugs
- ✅ Sync bug status to Vtiger
- ✅ Update ticket details
- ✅ Query tickets from CRM
- ✅ Link bugs to cases/contacts

---

## 📋 Prerequisites

1. **Vtiger CRM Account**
   - Version 7.0+ recommended
   - Cloud or self-hosted

2. **API Access Key**
   - Must have admin or user with API access
   - Generate access key from Vtiger

3. **Network Access**
   - Your server must reach Vtiger URL
   - Ports 80/443 open

---

## 🔐 Getting Your Vtiger Credentials

### **Step 1: Get Your Vtiger URL**

Your Vtiger URL format:
```
Cloud: https://your-crm.od2.vtiger.com
Self-hosted: https://your-domain.com/vtigercrm
```

### **Step 2: Get Your Access Key**

1. Log into Vtiger
2. Click your profile (top right)
3. Go to "My Preferences"
4. Find "Webservice Access Key" section
5. Click "Show" or "Generate" if not created
6. Copy the access key (long alphanumeric string)

**Example Access Key:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### **Step 3: Note Your Username**

Usually your login email or username:
```
admin
your.email@company.com
```

---

## ⚙️ Configuration

### **Option 1: Using .env File** ⭐ **Recommended**

Edit `/root/phase0_bug_tracker/.env` (on droplet) or `~/ASEAGI/.env` (locally):

```bash
# Vtiger CRM Integration
VTIGER_ENABLED=true
VTIGER_URL=https://your-crm.od2.vtiger.com
VTIGER_USERNAME=admin
VTIGER_ACCESS_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### **Option 2: Environment Variables**

```bash
export VTIGER_ENABLED=true
export VTIGER_URL="https://your-crm.od2.vtiger.com"
export VTIGER_USERNAME="admin"
export VTIGER_ACCESS_KEY="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

### **Option 3: Docker Compose**

Already configured! Just set .env and restart:

```bash
docker compose down
docker compose up -d
```

---

## 🧪 Testing the Connection

### **On Droplet:**

```bash
ssh root@137.184.1.91
cd /root/phase0_bug_tracker
python3 scripts/test_vtiger_connection.py
```

### **Locally:**

```bash
cd ~/ASEAGI
python3 scripts/test_vtiger_connection.py
```

### **Expected Output (Success):**

```
🧪 VTIGER CONNECTION TEST SCRIPT
======================================================================

============================================================
🔌 VTIGER CONNECTION TEST
============================================================

📋 Configuration:
   Enabled: True
   URL: https://your-crm.od2.vtiger.com
   Username: admin
   Access Key: ********************

🔐 Testing authentication...
🔐 Getting challenge token from https://your-crm.od2.vtiger.com...
🔑 Logging in as admin...
✅ Authenticated successfully!
   Session: 1a2b3c4d5e6f7g8h
   User ID: 19x1

🔍 Testing query...
✅ Query successful! Found 0 ticket(s)

============================================================
✅ VTIGER CONNECTION TEST PASSED
============================================================

🎉 All tests passed!

You can now:
  1. Create tickets from bugs automatically
  2. Sync bug status to Vtiger
  3. Query tickets from your CRM
```

---

## 🐛 Using Vtiger Integration

### **Automatic Ticket Creation**

When a bug is created, it automatically creates a Vtiger ticket:

```python
from core.bug_tracker import BugTracker

tracker = BugTracker()

# This will auto-create a Vtiger ticket if enabled
bug_id = tracker.create_bug(
    title="Document Scanner Error",
    description="Scanner fails on PDF files",
    severity="high",
    priority="high",
    component="document_scanner"
)
```

### **Manual Ticket Creation**

```python
from integrations.vtiger_sync import VtigerIntegration

vtiger = VtigerIntegration()

if vtiger.authenticate():
    bug = {
        'title': 'API Error on Document Upload',
        'description': 'Getting 500 error when uploading files',
        'severity': 'high',
        'priority': 'urgent',
        'status': 'open',
        'category': 'Bug'
    }

    ticket_id = vtiger.create_ticket(bug)
    print(f"Created ticket: {ticket_id}")
```

### **Query Tickets**

```python
vtiger = VtigerIntegration()

if vtiger.authenticate():
    # Get recent tickets
    query = "SELECT * FROM HelpDesk ORDER BY createdtime DESC LIMIT 10;"
    tickets = vtiger.query_tickets(query)

    for ticket in tickets:
        print(f"{ticket['ticket_no']}: {ticket['ticket_title']}")
```

### **Update Ticket**

```python
vtiger = VtigerIntegration()

if vtiger.authenticate():
    updates = {
        'ticketstatus': 'Closed',
        'solution': 'Fixed in version 2.1.0'
    }

    success = vtiger.update_ticket('17x123', updates)
```

---

## 📊 Status Mapping

ASEAGI status → Vtiger status:

| ASEAGI | Vtiger |
|--------|--------|
| open | Open |
| in_progress | In Progress |
| resolved | Closed |
| closed | Closed |
| pending | Wait For Response |

---

## 🔍 Troubleshooting

### **Error: "Authentication failed"**

**Check:**
1. Vtiger URL is correct (include https://)
2. Username matches Vtiger login
3. Access key is correct (regenerate if needed)
4. User has API access enabled

**Test connection manually:**
```bash
curl "https://your-crm.od2.vtiger.com/webservice.php?operation=getchallenge&username=admin"
```

Should return JSON with token.

### **Error: "Connection timeout"**

**Check:**
1. Vtiger URL is accessible from your server
2. Firewall allows outbound HTTPS (port 443)
3. Vtiger instance is running

**Test:**
```bash
curl -I https://your-crm.od2.vtiger.com
```

### **Error: "Module not found: integrations"**

**Fix:**
```bash
cd /root/phase0_bug_tracker
export PYTHONPATH=/root/phase0_bug_tracker:$PYTHONPATH
python3 scripts/test_vtiger_connection.py
```

### **Error: "Challenge request failed"**

**Possible causes:**
- Invalid username
- API access disabled for user
- Vtiger API not enabled

**Fix:**
1. Verify username in Vtiger
2. Check user has "Webservice Access"
3. Contact Vtiger admin

---

## 🔒 Security Best Practices

### **1. Protect Access Keys**

```bash
# Never commit .env files
echo ".env" >> .gitignore

# Use environment variables in production
export VTIGER_ACCESS_KEY="..." # from secure vault
```

### **2. Rotate Keys Regularly**

- Regenerate access keys every 90 days
- Update .env file
- Restart services

### **3. Restrict API User Permissions**

Create dedicated API user in Vtiger:
- Only HelpDesk module access
- Can't delete records
- Can't access sensitive data

### **4. Monitor API Usage**

Check Vtiger audit logs for:
- Unusual API activity
- Failed authentication attempts
- High request volumes

---

## 📈 Advanced Usage

### **Custom Field Mapping**

Edit `integrations/vtiger_sync.py` to map custom fields:

```python
ticket_data = {
    'ticket_title': bug.get('title'),
    'description': bug.get('description'),
    'cf_custom_field': bug.get('custom_value'),  # Custom field
    # ... other fields
}
```

### **Link to Accounts/Contacts**

```python
ticket_data = {
    'ticket_title': 'Issue for Client ABC',
    'parent_id': '11x123',  # Account ID
    'contact_id': '12x456',  # Contact ID
    # ...
}
```

### **Attach Files**

```python
# Upload file to Vtiger
def attach_file_to_ticket(ticket_id: str, file_path: str):
    # Implementation depends on Vtiger version
    # See Vtiger API docs for file upload
    pass
```

---

## 🧪 Testing Checklist

Before going to production:

- [ ] Test authentication with real credentials
- [ ] Create test ticket successfully
- [ ] Update test ticket
- [ ] Query tickets works
- [ ] Status mapping is correct
- [ ] Error handling works (test with wrong credentials)
- [ ] Timeout handling works (test with slow network)
- [ ] Logs are clear and helpful
- [ ] No sensitive data in logs
- [ ] Rate limiting respected

---

## 📚 Resources

**Vtiger API Documentation:**
- REST API: https://www.vtiger.com/docs/rest-api
- Webservices: https://www.vtiger.com/docs/webservices

**ASEAGI Integration:**
- Code: `integrations/vtiger_sync.py`
- Test: `scripts/test_vtiger_connection.py`
- Bug tracker hook: `core/bug_tracker.py:330-338`

---

## 💡 Tips

1. **Start with disabled** - Test locally first before enabling in production
2. **Monitor first week** - Watch for issues, adjust mappings
3. **Use test instance** - If available, test with Vtiger sandbox first
4. **Batch updates** - Don't create ticket for every minor bug
5. **Set filters** - Only sync important bugs (severity >= high)

---

## 🎯 Next Steps

1. ✅ Get Vtiger credentials
2. ✅ Configure .env file
3. ✅ Run test script
4. ✅ Create test ticket
5. ✅ Enable in production
6. ✅ Monitor for 1 week
7. ✅ Adjust as needed

---

**Need help?** Check Vtiger documentation or contact support.

**Last Updated:** November 7, 2025
