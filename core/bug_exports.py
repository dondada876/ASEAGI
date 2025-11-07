"""
Bug Export Utilities
Lightweight CSV/JSON/Excel export tools
"""

import os
import csv
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

sys.path.append(str(Path(__file__).parent.parent))

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: Supabase not installed")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class BugExporter:
    """Lightweight file-based bug export utilities"""

    def __init__(self):
        self.export_dir = Path(os.getenv('BUG_EXPORT_DIR', '/data/bugs'))
        self.export_dir.mkdir(parents=True, exist_ok=True)
        (self.export_dir / 'exports').mkdir(exist_ok=True)
        (self.export_dir / 'logs').mkdir(exist_ok=True)

        if SUPABASE_AVAILABLE:
            try:
                self.supabase: Client = create_client(
                    os.getenv("SUPABASE_URL", ""),
                    os.getenv("SUPABASE_KEY", "")
                )
                self.db_enabled = True
            except:
                self.db_enabled = False
        else:
            self.db_enabled = False

    def export_all_to_csv(self, output_file: Optional[str] = None) -> str:
        """Export all bugs to CSV"""

        if output_file is None:
            output_file = str(self.export_dir / 'bugs_export.csv')

        if not self.db_enabled:
            print("Database not available")
            return output_file

        try:
            bugs = self.supabase.table('bugs')\
                .select('*')\
                .order('created_at', desc=True)\
                .execute()

            self._write_csv(bugs.data, Path(output_file))
            print(f"✅ Exported {len(bugs.data)} bugs to {output_file}")

        except Exception as e:
            print(f"Export failed: {e}")

        return output_file

    def export_active_bugs(self) -> str:
        """Export only active bugs"""

        output_file = self.export_dir / 'bugs_active.csv'

        if not self.db_enabled:
            return str(output_file)

        try:
            bugs = self.supabase.table('bugs')\
                .select('*')\
                .not_.in_('status', ['resolved', 'closed', 'wont_fix'])\
                .order('severity', desc=False)\
                .order('created_at', desc=True)\
                .execute()

            self._write_csv(bugs.data, output_file)
            print(f"✅ Exported {len(bugs.data)} active bugs")

        except Exception as e:
            print(f"Export failed: {e}")

        return str(output_file)

    def export_critical_bugs(self) -> str:
        """Export only critical/high severity bugs"""

        output_file = self.export_dir / 'bugs_critical.csv'

        if not self.db_enabled:
            return str(output_file)

        try:
            bugs = self.supabase.table('bugs')\
                .select('*')\
                .in_('severity', ['critical', 'high'])\
                .not_.in_('status', ['resolved', 'closed'])\
                .order('created_at', desc=True)\
                .execute()

            self._write_csv(bugs.data, output_file)
            print(f"✅ Exported {len(bugs.data)} critical bugs")

        except Exception as e:
            print(f"Export failed: {e}")

        return str(output_file)

    def export_by_workspace(self, workspace_id: str) -> str:
        """Export bugs for specific workspace"""

        output_file = self.export_dir / f'bugs_{workspace_id}.csv'

        if not self.db_enabled:
            return str(output_file)

        try:
            bugs = self.supabase.table('bugs')\
                .select('*')\
                .eq('workspace_id', workspace_id)\
                .order('created_at', desc=True)\
                .execute()

            self._write_csv(bugs.data, output_file)
            print(f"✅ Exported {len(bugs.data)} bugs for {workspace_id}")

        except Exception as e:
            print(f"Export failed: {e}")

        return str(output_file)

    def export_weekly_report(self) -> str:
        """Export weekly bug report"""

        week_start = datetime.now() - timedelta(days=7)
        week_num = datetime.now().strftime('%Y-W%W')
        output_file = self.export_dir / 'exports' / f'weekly_report_{week_num}.csv'

        if not self.db_enabled:
            return str(output_file)

        try:
            bugs = self.supabase.table('bugs')\
                .select('*')\
                .gte('created_at', week_start.isoformat())\
                .execute()

            # Generate stats
            stats = {
                'report_date': datetime.now().isoformat(),
                'week_number': week_num,
                'total_bugs': len(bugs.data),
                'critical': len([b for b in bugs.data if b.get('severity') == 'critical']),
                'high': len([b for b in bugs.data if b.get('severity') == 'high']),
                'resolved': len([b for b in bugs.data if b.get('status') == 'resolved'])
            }

            # Write bugs
            self._write_csv(bugs.data, output_file)

            # Write summary
            summary_file = output_file.with_suffix('.summary.json')
            with open(summary_file, 'w') as f:
                json.dump(stats, f, indent=2)

            print(f"✅ Weekly report: {output_file}")

        except Exception as e:
            print(f"Export failed: {e}")

        return str(output_file)

    def export_to_json(self, filters: Optional[Dict] = None) -> str:
        """Export bugs to JSON format"""

        output_file = self.export_dir / f'bugs_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

        if not self.db_enabled:
            return str(output_file)

        try:
            query = self.supabase.table('bugs').select('*')

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            bugs = query.execute()

            with open(output_file, 'w') as f:
                json.dump(bugs.data, f, indent=2)

            print(f"✅ Exported {len(bugs.data)} bugs to JSON")

        except Exception as e:
            print(f"Export failed: {e}")

        return str(output_file)

    def export_to_excel(self) -> str:
        """Export bugs to Excel format (requires pandas and openpyxl)"""

        if not PANDAS_AVAILABLE:
            print("pandas not installed - cannot export to Excel")
            return ""

        output_file = self.export_dir / f'bugs_export_{datetime.now().strftime("%Y%m%d")}.xlsx'

        if not self.db_enabled:
            return str(output_file)

        try:
            bugs = self.supabase.table('bugs').select('*').execute()
            df = pd.DataFrame(bugs.data)

            # Write to Excel
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='All Bugs', index=False)

                # Add separate sheets for different views
                active_df = df[~df['status'].isin(['resolved', 'closed', 'wont_fix'])]
                active_df.to_excel(writer, sheet_name='Active Bugs', index=False)

                critical_df = df[df['severity'].isin(['critical', 'high'])]
                critical_df.to_excel(writer, sheet_name='Critical Bugs', index=False)

            print(f"✅ Exported to Excel: {output_file}")

        except Exception as e:
            print(f"Export failed: {e}")

        return str(output_file)

    def export_logs_to_csv(self, hours: int = 24) -> str:
        """Export system logs to CSV"""

        output_file = self.export_dir / f'logs_export_{datetime.now().strftime("%Y%m%d")}.csv'

        if not self.db_enabled:
            return str(output_file)

        try:
            cutoff = datetime.now() - timedelta(hours=hours)

            logs = self.supabase.table('system_logs')\
                .select('*')\
                .gte('created_at', cutoff.isoformat())\
                .order('created_at', desc=True)\
                .execute()

            # Flatten JSONB fields
            flattened = []
            for log in logs.data:
                flat_log = {k: v for k, v in log.items() if k != 'details'}
                flat_log['details'] = json.dumps(log.get('details', {}))
                flattened.append(flat_log)

            self._write_csv(flattened, output_file)
            print(f"✅ Exported {len(logs.data)} logs from last {hours} hours")

        except Exception as e:
            print(f"Export failed: {e}")

        return str(output_file)

    def generate_summary_report(self) -> str:
        """Generate human-readable summary report"""

        output_file = self.export_dir / f'summary_report_{datetime.now().strftime("%Y%m%d")}.txt'

        if not self.db_enabled:
            with open(output_file, 'w') as f:
                f.write("Database not available\n")
            return str(output_file)

        try:
            # Get stats
            total = self.supabase.table('bugs').select('id', count='exact').execute()
            active = self.supabase.table('bugs').select('id', count='exact')\
                .not_.in_('status', ['resolved', 'closed']).execute()
            critical = self.supabase.table('bugs').select('id', count='exact')\
                .eq('severity', 'critical').eq('status', 'open').execute()

            # Get recent bugs
            recent = self.supabase.table('bugs')\
                .select('bug_number, title, severity, status')\
                .order('created_at', desc=True)\
                .limit(10)\
                .execute()

            # Generate report
            report = f"""BUG TRACKING SUMMARY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== OVERVIEW ===
Total Bugs: {total.count}
Active Bugs: {active.count}
Critical Open: {critical.count}

=== RECENT BUGS ===
"""

            for bug in recent.data:
                report += f"\n{bug['bug_number']}: {bug['title']}"
                report += f"\n  Severity: {bug['severity']} | Status: {bug['status']}\n"

            with open(output_file, 'w') as f:
                f.write(report)

            print(f"✅ Summary report: {output_file}")

        except Exception as e:
            print(f"Export failed: {e}")

        return str(output_file)

    def _write_csv(self, data: List[Dict], output_file: Path):
        """Helper to write data to CSV"""

        if not data:
            with open(output_file, 'w') as f:
                f.write("# No data\n")
            return

        with open(output_file, 'w', newline='') as f:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for row in data:
                # Convert complex types to strings
                clean_row = {}
                for key, value in row.items():
                    if isinstance(value, (dict, list)):
                        clean_row[key] = json.dumps(value)
                    else:
                        clean_row[key] = value
                writer.writerow(clean_row)


# ============================================
# COMMAND-LINE INTERFACE
# ============================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Bug Tracker Export Utilities')
    parser.add_argument('command', choices=[
        'all', 'active', 'critical', 'weekly', 'workspace', 'logs', 'summary', 'json', 'excel'
    ])
    parser.add_argument('--workspace', help='Workspace ID')
    parser.add_argument('--hours', type=int, default=24, help='Hours for log export')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    exporter = BugExporter()

    if args.command == 'all':
        exporter.export_all_to_csv(args.output)

    elif args.command == 'active':
        exporter.export_active_bugs()

    elif args.command == 'critical':
        exporter.export_critical_bugs()

    elif args.command == 'weekly':
        exporter.export_weekly_report()

    elif args.command == 'workspace':
        if not args.workspace:
            print("Error: --workspace required")
            exit(1)
        exporter.export_by_workspace(args.workspace)

    elif args.command == 'logs':
        exporter.export_logs_to_csv(args.hours)

    elif args.command == 'summary':
        exporter.generate_summary_report()

    elif args.command == 'json':
        exporter.export_to_json()

    elif args.command == 'excel':
        exporter.export_to_excel()
