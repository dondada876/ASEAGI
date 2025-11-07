#!/usr/bin/env python3
"""
ASEAGI Dashboard Launcher
Quick access to all dashboards with correct ports
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

DASHBOARDS = {
    '1': {
        'name': 'PROJ344 Master Dashboard',
        'file': 'proj344_master_dashboard.py',
        'port': 8501,
        'description': 'Main legal case intelligence hub - Document registry, timeline, violations'
    },
    '2': {
        'name': 'Police Reports Dashboard',
        'file': 'police_reports_dashboard.py',
        'port': 8502,
        'description': 'Police reports viewer with filtering, search, and page-by-page viewing'
    },
    '3': {
        'name': 'CEO Global Dashboard',
        'file': 'ceo_global_dashboard.py',
        'port': 8503,
        'description': 'Executive overview - Business, legal, family, personal tracking'
    },
    '4': {
        'name': 'Legal Intelligence Dashboard',
        'file': 'legal_intelligence_dashboard.py',
        'port': 8504,
        'description': 'Document intelligence with scoring analysis'
    },
    '5': {
        'name': 'Court Events Dashboard',
        'file': 'court_events_dashboard.py',
        'port': 8505,
        'description': 'Court proceedings and event timeline'
    },
    '6': {
        'name': 'Truth Justice Timeline',
        'file': 'truth_justice_timeline.py',
        'port': 8506,
        'description': 'Truth scoring and justice analysis with 5W+H framework'
    },
    '7': {
        'name': 'Timeline Constitutional Violations',
        'file': 'timeline_constitutional_violations.py',
        'port': 8507,
        'description': 'Constitutional violations tracking and timeline'
    },
    '8': {
        'name': 'Supabase Dashboard',
        'file': 'supabase_dashboard.py',
        'port': 8508,
        'description': 'Database monitoring and diagnostics'
    },
}

def print_header():
    """Print header"""
    print("\n" + "=" * 80)
    print("🚀 ASEAGI DASHBOARD LAUNCHER")
    print("=" * 80)
    print()

def print_menu():
    """Print dashboard menu"""
    print("📊 Available Dashboards:")
    print("-" * 80)
    for key, dash in DASHBOARDS.items():
        status = "✅" if Path(dash['file']).exists() else "❌"
        print(f"  {status} {key}. {dash['name']} (Port {dash['port']})")
        print(f"      {dash['description']}")
        print()

    print("=" * 80)
    print("Options:")
    print("  [1-8]  Launch specific dashboard")
    print("  [a]    Launch ALL dashboards")
    print("  [l]    List running dashboards")
    print("  [k]    Kill all dashboards")
    print("  [q]    Quit")
    print("=" * 80)
    print()

def check_file_exists(filepath):
    """Check if dashboard file exists"""
    if not Path(filepath).exists():
        print(f"❌ Error: {filepath} not found")
        return False
    return True

def launch_dashboard(key, open_browser=True):
    """Launch a specific dashboard"""
    if key not in DASHBOARDS:
        print(f"❌ Invalid selection: {key}")
        return False

    dash = DASHBOARDS[key]

    if not check_file_exists(dash['file']):
        return False

    print(f"🚀 Launching {dash['name']}...")
    print(f"   File: {dash['file']}")
    print(f"   Port: {dash['port']}")
    print(f"   URL: http://localhost:{dash['port']}")
    print()

    # Launch Streamlit
    cmd = [
        'streamlit', 'run',
        dash['file'],
        f'--server.port={dash["port"]}',
        '--server.headless=true'
    ]

    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)  # Wait for startup

        print(f"✅ {dash['name']} started on port {dash['port']}")

        if open_browser:
            url = f"http://localhost:{dash['port']}"
            print(f"🌐 Opening browser: {url}")
            webbrowser.open(url)

        return True

    except FileNotFoundError:
        print("❌ Error: Streamlit not found. Install with: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        return False

def launch_all():
    """Launch all dashboards"""
    print("🚀 Launching ALL dashboards...")
    print()

    success_count = 0
    for key in DASHBOARDS.keys():
        if launch_dashboard(key, open_browser=False):
            success_count += 1
        time.sleep(1)  # Stagger launches

    print()
    print(f"✅ Launched {success_count}/{len(DASHBOARDS)} dashboards")
    print()
    print("📋 Access URLs:")
    for dash in DASHBOARDS.values():
        if Path(dash['file']).exists():
            print(f"  • {dash['name']}: http://localhost:{dash['port']}")
    print()

def list_running():
    """List running Streamlit processes"""
    import psutil

    print("🔍 Checking for running dashboards...")
    print()

    running = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and 'streamlit' in ' '.join(cmdline):
                # Extract port if present
                port = None
                for i, arg in enumerate(cmdline):
                    if '--server.port' in arg:
                        if '=' in arg:
                            port = arg.split('=')[1]
                        elif i + 1 < len(cmdline):
                            port = cmdline[i + 1]

                # Extract filename
                filename = None
                for arg in cmdline:
                    if arg.endswith('.py'):
                        filename = Path(arg).name
                        break

                running.append({
                    'pid': proc.info['pid'],
                    'port': port,
                    'file': filename
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if running:
        print("✅ Running dashboards:")
        print("-" * 80)
        for proc in running:
            file_info = proc['file'] if proc['file'] else 'Unknown'
            port_info = f"Port {proc['port']}" if proc['port'] else "Port unknown"
            print(f"  • PID {proc['pid']}: {file_info} ({port_info})")
            if proc['port']:
                print(f"    URL: http://localhost:{proc['port']}")
        print("-" * 80)
    else:
        print("⚠️  No running dashboards found")

    print()

def kill_all():
    """Kill all Streamlit processes"""
    import psutil

    print("🛑 Stopping all dashboards...")
    print()

    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and 'streamlit' in ' '.join(cmdline):
                proc.terminate()
                killed += 1
                print(f"✅ Stopped PID {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if killed:
        print(f"\n✅ Stopped {killed} dashboard(s)")
    else:
        print("⚠️  No running dashboards found")

    print()

def main():
    """Main menu loop"""
    print_header()

    # Check for psutil
    try:
        import psutil
    except ImportError:
        print("⚠️  Warning: psutil not installed. Some features unavailable.")
        print("   Install with: pip install psutil")
        print()

    while True:
        print_menu()
        choice = input("Select option: ").strip().lower()
        print()

        if choice == 'q':
            print("👋 Goodbye!")
            sys.exit(0)

        elif choice == 'a':
            launch_all()
            input("Press Enter to continue...")

        elif choice == 'l':
            list_running()
            input("Press Enter to continue...")

        elif choice == 'k':
            kill_all()
            input("Press Enter to continue...")

        elif choice in DASHBOARDS:
            launch_dashboard(choice)
            print("💡 Tip: Dashboard is running in background. Open more or press Ctrl+C to stop.")
            input("Press Enter to continue...")

        else:
            print("❌ Invalid choice. Please try again.")
            print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
