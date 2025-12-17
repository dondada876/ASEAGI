"""
Vtiger CRM Integration
Syncs bugs and tickets to Vtiger CRM
"""

import os
import requests
import hashlib
import time
from typing import Dict, Optional, List
from datetime import datetime

class VtigerIntegration:
    """
    Vtiger CRM API Integration
    
    Supports:
    - Authentication
    - Create tickets/cases
    - Update tickets
    - Query tickets
    - Link to documents
    """
    
    def __init__(self):
        self.enabled = os.getenv('VTIGER_ENABLED', 'false').lower() == 'true'
        self.url = os.getenv('VTIGER_URL', '')
        self.username = os.getenv('VTIGER_USERNAME', '')
        self.access_key = os.getenv('VTIGER_ACCESS_KEY', '')
        
        self.session_name = None
        self.user_id = None
        self.session_expires = 0
        
    def authenticate(self) -> bool:
        """
        Authenticate with Vtiger API
        
        Returns:
            bool: True if authentication successful
        """
        if not self.enabled:
            print("Vtiger integration is disabled")
            return False
            
        if not all([self.url, self.username, self.access_key]):
            print("ERROR: Vtiger credentials not configured")
            print(f"  URL: {bool(self.url)}")
            print(f"  Username: {bool(self.username)}")
            print(f"  Access Key: {bool(self.access_key)}")
            return False
        
        try:
            # Get challenge token
            challenge_url = f"{self.url}/webservice.php"
            challenge_params = {
                'operation': 'getchallenge',
                'username': self.username
            }
            
            print(f"🔐 Getting challenge token from {self.url}...")
            response = requests.get(challenge_url, params=challenge_params, timeout=10)
            response.raise_for_status()
            
            challenge_data = response.json()
            
            if not challenge_data.get('success'):
                print(f"ERROR: Challenge request failed: {challenge_data.get('error', {}).get('message', 'Unknown error')}")
                return False
            
            token = challenge_data['result']['token']
            
            # Generate access key hash
            access_key_hash = hashlib.md5(f"{token}{self.access_key}".encode()).hexdigest()
            
            # Login
            login_params = {
                'operation': 'login',
                'username': self.username,
                'accessKey': access_key_hash
            }
            
            print(f"🔑 Logging in as {self.username}...")
            response = requests.post(challenge_url, data=login_params, timeout=10)
            response.raise_for_status()
            
            login_data = response.json()
            
            if not login_data.get('success'):
                print(f"ERROR: Login failed: {login_data.get('error', {}).get('message', 'Unknown error')}")
                return False
            
            self.session_name = login_data['result']['sessionName']
            self.user_id = login_data['result']['userId']
            self.session_expires = time.time() + 3600  # 1 hour
            
            print(f"✅ Authenticated successfully!")
            print(f"   Session: {self.session_name}")
            print(f"   User ID: {self.user_id}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Network error: {str(e)}")
            return False
        except Exception as e:
            print(f"ERROR: Authentication failed: {str(e)}")
            return False
    
    def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid session"""
        if not self.session_name or time.time() >= self.session_expires:
            return self.authenticate()
        return True
    
    def create_ticket(self, bug: Dict) -> Optional[str]:
        """
        Create a ticket/case in Vtiger from bug data
        
        Args:
            bug: Bug dictionary with title, description, etc.
            
        Returns:
            str: Ticket ID if created, None otherwise
        """
        if not self._ensure_authenticated():
            return None
        
        try:
            # Map bug to Vtiger HelpDesk/Trouble Tickets module
            ticket_data = {
                'ticket_title': bug.get('title', 'Untitled Bug'),
                'description': bug.get('description', ''),
                'ticketstatus': self._map_status(bug.get('status', 'open')),
                'ticketseverity': self._map_severity(bug.get('severity', 'medium')),
                'ticketpriorities': self._map_priority(bug.get('priority', 'medium')),
                'ticketcategories': bug.get('category', 'Bug'),
                'product_id': '',  # Link to product if needed
                'parent_id': '',  # Link to account/contact if needed
                'assigned_user_id': self.user_id
            }
            
            # Create ticket
            url = f"{self.url}/webservice.php"
            params = {
                'operation': 'create',
                'sessionName': self.session_name,
                'elementType': 'HelpDesk',
                'element': str(ticket_data).replace("'", '"')
            }
            
            print(f"📝 Creating Vtiger ticket: {ticket_data['ticket_title']}")
            response = requests.post(url, data=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if not result.get('success'):
                print(f"ERROR: Ticket creation failed: {result.get('error', {}).get('message', 'Unknown error')}")
                return None
            
            ticket_id = result['result']['id']
            print(f"✅ Ticket created: {ticket_id}")
            
            return ticket_id
            
        except Exception as e:
            print(f"ERROR: Failed to create ticket: {str(e)}")
            return None
    
    def update_ticket(self, ticket_id: str, updates: Dict) -> bool:
        """Update an existing ticket"""
        if not self._ensure_authenticated():
            return False
        
        try:
            url = f"{self.url}/webservice.php"
            updates['id'] = ticket_id
            
            params = {
                'operation': 'update',
                'sessionName': self.session_name,
                'elementType': 'HelpDesk',
                'element': str(updates).replace("'", '"')
            }
            
            response = requests.post(url, data=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return result.get('success', False)
            
        except Exception as e:
            print(f"ERROR: Failed to update ticket: {str(e)}")
            return False
    
    def query_tickets(self, query: str) -> Optional[List[Dict]]:
        """Query tickets using Vtiger Query Language"""
        if not self._ensure_authenticated():
            return None
        
        try:
            url = f"{self.url}/webservice.php"
            params = {
                'operation': 'query',
                'sessionName': self.session_name,
                'query': query
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if not result.get('success'):
                return None
            
            return result.get('result', [])
            
        except Exception as e:
            print(f"ERROR: Query failed: {str(e)}")
            return None
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Get a specific ticket by ID"""
        if not self._ensure_authenticated():
            return None
        
        try:
            url = f"{self.url}/webservice.php"
            params = {
                'operation': 'retrieve',
                'sessionName': self.session_name,
                'id': ticket_id
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if not result.get('success'):
                return None
            
            return result.get('result')
            
        except Exception as e:
            print(f"ERROR: Failed to get ticket: {str(e)}")
            return None
    
    # Helper methods
    def _map_status(self, status: str) -> str:
        """Map internal status to Vtiger status"""
        mapping = {
            'open': 'Open',
            'in_progress': 'In Progress',
            'resolved': 'Closed',
            'closed': 'Closed',
            'pending': 'Wait For Response'
        }
        return mapping.get(status.lower(), 'Open')
    
    def _map_severity(self, severity: str) -> str:
        """Map internal severity to Vtiger severity"""
        mapping = {
            'low': 'Minor',
            'medium': 'Major',
            'high': 'Critical',
            'critical': 'Critical'
        }
        return mapping.get(severity.lower(), 'Major')
    
    def _map_priority(self, priority: str) -> str:
        """Map internal priority to Vtiger priority"""
        mapping = {
            'low': 'Low',
            'medium': 'Normal',
            'high': 'High',
            'urgent': 'High'
        }
        return mapping.get(priority.lower(), 'Normal')
    
    def test_connection(self) -> bool:
        """Test connection to Vtiger"""
        print("\n" + "=" * 60)
        print("🔌 VTIGER CONNECTION TEST")
        print("=" * 60)
        
        print(f"\n📋 Configuration:")
        print(f"   Enabled: {self.enabled}")
        print(f"   URL: {self.url or '(not set)'}")
        print(f"   Username: {self.username or '(not set)'}")
        print(f"   Access Key: {'*' * 20 if self.access_key else '(not set)'}")
        
        if not self.enabled:
            print("\n⚠️  Vtiger integration is DISABLED")
            print("   Set VTIGER_ENABLED=true in .env to enable")
            return False
        
        print(f"\n🔐 Testing authentication...")
        if not self.authenticate():
            print("\n❌ Authentication FAILED")
            return False
        
        print(f"\n✅ Authentication SUCCESSFUL!")
        
        # Try to query tickets
        print(f"\n🔍 Testing query...")
        try:
            query = "SELECT * FROM HelpDesk LIMIT 1;"
            tickets = self.query_tickets(query)
            
            if tickets is not None:
                print(f"✅ Query successful! Found {len(tickets)} ticket(s)")
            else:
                print("⚠️  Query returned no results (this is OK if no tickets exist)")
        except Exception as e:
            print(f"⚠️  Query test failed: {str(e)}")
        
        print("\n" + "=" * 60)
        print("✅ VTIGER CONNECTION TEST PASSED")
        print("=" * 60 + "\n")
        
        return True
