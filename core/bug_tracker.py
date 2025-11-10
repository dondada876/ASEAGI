"""
BugTracker - Automatic Error Detection and Bug Management
Phase 0 Implementation
"""

import os
import sys
import functools
import traceback
import uuid
import json
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, List
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: Supabase not installed. Using file-only mode.")


class BugTracker:
    """
    Automatic bug detection and logging system

    Features:
    - Auto-creates bugs from errors
    - Logs all activity to database
    - Exports to CSV/JSON files
    - Optional external integrations
    """

    def __init__(self):
        self.request_id = str(uuid.uuid4())

        # Initialize Supabase client
        if SUPABASE_AVAILABLE:
            try:
                self.supabase: Client = create_client(
                    os.getenv("SUPABASE_URL", ""),
                    os.getenv("SUPABASE_KEY", "")
                )
                self.db_enabled = True
            except Exception as e:
                print(f"Warning: Failed to connect to Supabase: {e}")
                self.db_enabled = False
        else:
            self.db_enabled = False

        # File logging directories
        self.bug_dir = Path(os.getenv('BUG_EXPORT_DIR', '/data/bugs'))
        self.log_dir = self.bug_dir / 'logs'
        self.bug_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        level: str,
        message: str,
        component: str,
        details: Optional[Dict] = None,
        error: Optional[Exception] = None,
        workspace_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Log message to system_logs table and files

        Args:
            level: debug, info, warning, error, critical
            message: Log message
            component: Component name (e.g., 'csv_parser', 'telegram_bot')
            details: Additional structured data
            error: Exception object if applicable
            workspace_id: Workspace context

        Returns:
            Log ID (UUID) if successfully stored
        """

        log_entry = {
            'log_level': level,
            'component': component,
            'message': message,
            'context': details or {},
            'request_id': self.request_id,
            'workspace_id': workspace_id
        }

        if error:
            log_entry.update({
                'error_type': type(error).__name__,
                'error_message': str(error),
                'stack_trace': traceback.format_exc()
            })

        log_id = None

        # Store in database
        if self.db_enabled:
            try:
                result = self.supabase.table('error_logs').insert(log_entry).execute()
                log_id = result.data[0]['id'] if result.data else None

                # Auto-create bug if critical
                if level == 'critical' and log_id:
                    self.auto_create_bug(log_entry, log_id)

            except Exception as e:
                print(f"Failed to log to database: {e}")
                self._log_to_file(log_entry)
        else:
            self._log_to_file(log_entry)

        # Always log to file as backup
        self._log_to_file(log_entry)

        return log_id

    def auto_create_bug(self, log_entry: Dict, log_id: str) -> Optional[str]:
        """
        Automatically create bug from critical error

        Args:
            log_entry: Log entry dictionary
            log_id: UUID of the log entry

        Returns:
            Bug ID if created
        """

        if not self.db_enabled:
            print("Database not available - cannot create bug")
            return None

        try:
            # Check if similar bug already exists (last 24 hours)
            existing = self.supabase.table('bugs')\
                .select('id, bug_number, occurrence_count')\
                .eq('error_message', log_entry.get('error_message', ''))\
                .eq('status', 'open')\
                .gte('created_at', (datetime.now() - timedelta(days=1)).isoformat())\
                .execute()

            if existing.data:
                # Update existing bug
                bug = existing.data[0]
                self.supabase.table('bugs')\
                    .update({
                        'occurrence_count': bug['occurrence_count'] + 1,
                        'last_occurred_at': datetime.now().isoformat()
                    })\
                    .eq('id', bug['id'])\
                    .execute()

                print(f"📝 Updated existing bug: {bug['bug_number']}")
                return bug['id']

            # Create new bug
            bug_data = {
                'title': f"Critical: {log_entry['component']} - {log_entry.get('error_type', 'Error')}",
                'description': log_entry['message'],
                'severity': 'critical',
                'priority': 'urgent',
                'bug_type': 'error',
                'category': 'auto_detected',
                'component': log_entry['component'],
                'workspace_id': log_entry.get('workspace_id'),
                'environment': os.getenv('ENVIRONMENT', 'production'),
                'status': 'open',
                'report_source': 'auto_detected',
                'reported_by': 'system',
                'error_message': log_entry.get('error_message'),
                'stack_trace': log_entry.get('stack_trace'),
                'related_log_ids': [log_id],
                'first_occurred_at': datetime.now().isoformat(),
                'last_occurred_at': datetime.now().isoformat(),
                'occurrence_count': 1
            }

            result = self.supabase.table('bugs').insert(bug_data).execute()

            if result.data:
                bug = result.data[0]
                bug_id = bug['id']
                bug_number = bug['bug_number']

                # Link log back to bug
                self.supabase.table('error_logs')\
                    .update({'related_bug_id': bug_id})\
                    .eq('id', log_id)\
                    .execute()

                # Export to files
                self.export_bug_to_csv(bug_number, bug_data)
                self.export_bug_to_log(bug_number, bug_data)

                # Optional: sync to external system
                if os.getenv('EXTERNAL_INTEGRATION_ENABLED') == 'true':
                    self.sync_to_external(bug_number, bug_data)

                print(f"🐛 Auto-created bug: {bug_number}")

                return bug_id

        except Exception as e:
            print(f"Failed to auto-create bug: {e}")
            traceback.print_exc()

        return None

    def create_bug(
        self,
        title: str,
        description: str,
        severity: str = 'medium',
        priority: str = 'medium',
        component: Optional[str] = None,
        workspace_id: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict]:
        """
        Manually create a bug

        Args:
            title: Bug title
            description: Bug description
            severity: critical, high, medium, low
            priority: urgent, high, medium, low
            component: Component name
            workspace_id: Workspace
            **kwargs: Additional bug fields

        Returns:
            Bug dictionary with bug_number
        """

        bug_data = {
            'title': title,
            'description': description,
            'severity': severity,
            'priority': priority,
            'bug_type': kwargs.get('bug_type', 'bug'),
            'component': component,
            'workspace_id': workspace_id,
            'environment': os.getenv('ENVIRONMENT', 'production'),
            'status': 'open',
            'report_source': kwargs.get('report_source', 'manual'),
            'reported_by': kwargs.get('reported_by', 'user'),
            **{k: v for k, v in kwargs.items() if k not in ['bug_type', 'report_source', 'reported_by']}
        }

        if self.db_enabled:
            try:
                result = self.supabase.table('bugs').insert(bug_data).execute()
                if result.data:
                    bug = result.data[0]

                    # Export to files
                    self.export_bug_to_csv(bug['bug_number'], bug)
                    self.export_bug_to_log(bug['bug_number'], bug)

                    print(f"🐛 Created bug: {bug['bug_number']}")
                    return bug
            except Exception as e:
                print(f"Failed to create bug in database: {e}")

        # Fallback to file only
        bug_data['bug_number'] = f"BUG-{str(uuid.uuid4())[:8].upper()}"
        self.export_bug_to_csv(bug_data['bug_number'], bug_data)
        self.export_bug_to_log(bug_data['bug_number'], bug_data)

        return bug_data

    def export_bug_to_csv(self, bug_number: str, bug: Dict):
        """Export bug to CSV file"""
        import csv

        csv_file = self.bug_dir / 'bugs_export.csv'
        file_exists = csv_file.exists()

        try:
            with open(csv_file, 'a', newline='') as f:
                fieldnames = [
                    'bug_number', 'title', 'severity', 'status', 'component',
                    'created_at', 'assigned_to', 'error_message'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                if not file_exists:
                    writer.writeheader()

                writer.writerow({
                    'bug_number': bug_number,
                    'title': bug.get('title', '')[:100],
                    'severity': bug.get('severity', ''),
                    'status': bug.get('status', ''),
                    'component': bug.get('component', ''),
                    'created_at': datetime.now().isoformat(),
                    'assigned_to': bug.get('assigned_to', ''),
                    'error_message': bug.get('error_message', '')[:100]
                })
        except Exception as e:
            print(f"Failed to export bug to CSV: {e}")

    def export_bug_to_log(self, bug_number: str, bug: Dict):
        """Export bug to daily JSON log file"""
        log_file = self.log_dir / f"bugs_{datetime.now().strftime('%Y-%m-%d')}.jsonl"

        try:
            with open(log_file, 'a') as f:
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'bug_number': bug_number,
                    'bug': bug
                }
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Failed to export bug to log: {e}")

    def sync_to_external(self, bug_number: str, bug: Dict):
        """Optional: Sync to external system (Vtiger, Linear, etc.)"""
        external_system = os.getenv('EXTERNAL_SYSTEM', 'vtiger')

        try:
            if external_system == 'vtiger':
                from integrations.vtiger_sync import VtigerIntegration
                vtiger = VtigerIntegration()
                if vtiger.enabled and vtiger.authenticate():
                    vtiger.create_ticket(bug)

        except Exception as e:
            # Don't fail bug creation if external sync fails
            print(f"Warning: Failed to sync to {external_system}: {e}")
            self.log('warning', f'External sync failed for {bug_number}', 'bug_tracker',
                    details={'error': str(e), 'system': external_system})

    def _log_to_file(self, log_entry: Dict):
        """Fallback file logging"""
        log_file = self.log_dir / f"system_{datetime.now().strftime('%Y-%m-%d')}.log"

        try:
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - {json.dumps(log_entry)}\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}")


# ============================================
# DECORATOR FOR AUTOMATIC ERROR TRACKING
# ============================================

def track_errors(component: str, workspace_id: Optional[str] = None):
    """
    Decorator to automatically track errors

    Usage:
        @track_errors('csv_parser', workspace_id='legal')
        def my_function():
            # Your code here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            tracker = BugTracker()
            try:
                tracker.log('info', f'Starting {func.__name__}', component, workspace_id=workspace_id)
                result = func(*args, **kwargs)
                tracker.log('info', f'Completed {func.__name__}', component, workspace_id=workspace_id)
                return result

            except Exception as e:
                tracker.log(
                    'error',
                    f'Error in {func.__name__}: {str(e)}',
                    component,
                    details={
                        'function': func.__name__,
                        'args': str(args)[:200],
                        'kwargs': str(kwargs)[:200]
                    },
                    error=e,
                    workspace_id=workspace_id
                )
                raise

        return wrapper
    return decorator


# ============================================
# TESTING
# ============================================

if __name__ == '__main__':
    # Test bug tracker
    from datetime import timedelta

    print("🧪 Testing BugTracker...")

    tracker = BugTracker()

    # Test logging
    print("\n1. Testing logging...")
    log_id = tracker.log('info', 'Test log message', 'test_component')
    print(f"   ✅ Log ID: {log_id}")

    # Test bug creation
    print("\n2. Testing manual bug creation...")
    bug = tracker.create_bug(
        title='Test Bug',
        description='This is a test bug',
        severity='low',
        priority='low',
        component='test_component'
    )
    print(f"   ✅ Bug Number: {bug.get('bug_number')}")

    # Test error logging
    print("\n3. Testing error logging...")
    try:
        raise ValueError("Test error")
    except Exception as e:
        tracker.log('error', 'Test error occurred', 'test_component', error=e)
        print(f"   ✅ Error logged")

    # Test decorator
    print("\n4. Testing @track_errors decorator...")

    @track_errors('test_decorator')
    def test_function():
        print("   Inside decorated function")
        return "success"

    result = test_function()
    print(f"   ✅ Decorator result: {result}")

    # Test CSV export
    print("\n5. Checking CSV export...")
    csv_file = Path('/data/bugs/bugs_export.csv')
    if csv_file.exists():
        print(f"   ✅ CSV file exists: {csv_file}")
    else:
        print(f"   ⚠️  CSV file not found (may need to create /data/bugs directory)")

    print("\n✅ All tests completed!")
