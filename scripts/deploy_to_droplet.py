#!/usr/bin/env python3
"""
Deploy dashboard fixes to DigitalOcean droplet
Automates the deployment process via SSH
"""

import subprocess
import sys
import time
from typing import List, Tuple

# Droplet configuration
DROPLET_IP = "137.184.1.91"
DROPLET_USER = "root"
DROPLET_PATH = "/root/ASEAGI"
GIT_BRANCH = "claude/framework-comparison-guide-011CUyvuditeFNvRT8iUjHoC"

# Dashboard configurations
DASHBOARDS = [
    {"file": "proj344_master_dashboard.py", "port": 8501, "name": "PROJ344 Master"},
    {"file": "ceo_dashboard.py", "port": 8502, "name": "CEO Dashboard"},
    {"file": "legal_intelligence_dashboard.py", "port": 8503, "name": "Legal Intelligence"},
    {"file": "enhanced_scanning_monitor.py", "port": 8504, "name": "Enhanced Scanning"},
    {"file": "scanning_monitor_dashboard.py", "port": 8505, "name": "Scanning Monitor"},
    {"file": "timeline_violations_dashboard.py", "port": 8506, "name": "Timeline Violations"},
    {"file": "system_overview_dashboard.py", "port": 8507, "name": "System Overview"},
]

class Colors:
    """ANSI color codes"""
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color

def run_ssh_command(command: str, show_output: bool = True) -> Tuple[int, str, str]:
    """
    Run command on droplet via SSH

    Returns:
        (return_code, stdout, stderr)
    """
    ssh_cmd = f"ssh {DROPLET_USER}@{DROPLET_IP} '{command}'"

    if show_output:
        print(f"{Colors.BLUE}  Running: {command}{Colors.NC}")

    try:
        result = subprocess.run(
            ssh_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )

        if show_output and result.stdout:
            print(result.stdout)

        if result.stderr and "Warning" not in result.stderr:
            if show_output:
                print(f"{Colors.YELLOW}{result.stderr}{Colors.NC}")

        return result.returncode, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}❌ Command timed out{Colors.NC}")
        return 1, "", "Timeout"
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.NC}")
        return 1, "", str(e)

def check_ssh_access() -> bool:
    """Check if we can SSH to droplet"""
    print(f"\n{Colors.BLUE}🔐 Checking SSH access to {DROPLET_IP}...{Colors.NC}")

    returncode, stdout, stderr = run_ssh_command("echo 'SSH OK'", show_output=False)

    if returncode == 0:
        print(f"{Colors.GREEN}✅ SSH connection successful{Colors.NC}")
        return True
    else:
        print(f"{Colors.RED}❌ SSH connection failed{Colors.NC}")
        print(f"\nTroubleshooting:")
        print(f"  1. Check SSH key: ssh-add -l")
        print(f"  2. Test manually: ssh {DROPLET_USER}@{DROPLET_IP}")
        print(f"  3. Check firewall/network")
        return False

def pull_latest_code() -> bool:
    """Pull latest code from git"""
    print(f"\n{Colors.BLUE}📥 Pulling latest code...{Colors.NC}")

    commands = [
        f"cd {DROPLET_PATH}",
        f"git fetch origin {GIT_BRANCH}",
        f"git checkout {GIT_BRANCH}",
        f"git pull origin {GIT_BRANCH}"
    ]

    full_command = " && ".join(commands)
    returncode, stdout, stderr = run_ssh_command(full_command)

    if returncode == 0:
        print(f"{Colors.GREEN}✅ Code pulled successfully{Colors.NC}")
        return True
    else:
        print(f"{Colors.RED}❌ Git pull failed{Colors.NC}")
        return False

def stop_dashboards() -> bool:
    """Stop all running Streamlit dashboards"""
    print(f"\n{Colors.BLUE}🛑 Stopping all Streamlit dashboards...{Colors.NC}")

    # First, list running processes
    returncode, stdout, stderr = run_ssh_command(
        "ps aux | grep streamlit | grep -v grep",
        show_output=True
    )

    if "streamlit" in stdout:
        print(f"  Found running Streamlit processes")

        # Kill all Streamlit processes
        returncode, stdout, stderr = run_ssh_command("pkill -f streamlit", show_output=False)

        # Wait a moment
        time.sleep(2)

        # Verify they're stopped
        returncode, stdout, stderr = run_ssh_command(
            "ps aux | grep streamlit | grep -v grep",
            show_output=False
        )

        if "streamlit" not in stdout:
            print(f"{Colors.GREEN}✅ All dashboards stopped{Colors.NC}")
            return True
        else:
            print(f"{Colors.YELLOW}⚠️  Some processes still running{Colors.NC}")
            return False
    else:
        print(f"{Colors.GREEN}✅ No dashboards were running{Colors.NC}")
        return True

def start_dashboards() -> bool:
    """Start all dashboards"""
    print(f"\n{Colors.BLUE}🚀 Starting dashboards...{Colors.NC}")

    success = True

    for dash in DASHBOARDS:
        print(f"\n  Starting {dash['name']} on port {dash['port']}...")

        command = (
            f"cd {DROPLET_PATH}/dashboards && "
            f"nohup streamlit run {dash['file']} "
            f"--server.port {dash['port']} "
            f"> /tmp/dash-{dash['port']}.log 2>&1 &"
        )

        returncode, stdout, stderr = run_ssh_command(command, show_output=False)

        if returncode == 0:
            print(f"{Colors.GREEN}  ✅ {dash['name']} started{Colors.NC}")
        else:
            print(f"{Colors.RED}  ❌ {dash['name']} failed to start{Colors.NC}")
            success = False

        # Small delay between starts
        time.sleep(1)

    return success

def verify_dashboards() -> List[dict]:
    """Verify all dashboards are running"""
    print(f"\n{Colors.BLUE}🔍 Verifying dashboards...{Colors.NC}")

    time.sleep(3)  # Give dashboards time to start

    results = []

    for dash in DASHBOARDS:
        port = dash['port']
        name = dash['name']

        # Check if port is listening
        returncode, stdout, stderr = run_ssh_command(
            f"lsof -i :{port}",
            show_output=False
        )

        status = "running" if returncode == 0 else "not_running"

        # Try HTTP request
        http_code = None
        if status == "running":
            returncode, stdout, stderr = run_ssh_command(
                f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{port} --connect-timeout 2 --max-time 5",
                show_output=False
            )
            http_code = stdout.strip()

        result = {
            "port": port,
            "name": name,
            "status": status,
            "http_code": http_code
        }
        results.append(result)

        # Print result
        if status == "running" and http_code == "200":
            print(f"{Colors.GREEN}  ✅ Port {port}: {name} - OK{Colors.NC}")
        elif status == "running":
            print(f"{Colors.YELLOW}  ⚠️  Port {port}: {name} - Running but HTTP {http_code}{Colors.NC}")
        else:
            print(f"{Colors.RED}  ❌ Port {port}: {name} - Not running{Colors.NC}")

    return results

def print_summary(results: List[dict]):
    """Print deployment summary"""
    print("\n" + "=" * 80)
    print(f"{Colors.BLUE}📋 DEPLOYMENT SUMMARY{Colors.NC}")
    print("=" * 80)

    running = sum(1 for r in results if r["status"] == "running")
    ok = sum(1 for r in results if r["status"] == "running" and r["http_code"] == "200")

    print(f"\nDashboards running: {running}/{len(results)}")
    print(f"HTTP 200 OK:        {ok}/{len(results)}")

    if ok == len(results):
        print(f"\n{Colors.GREEN}✅ ALL DASHBOARDS DEPLOYED SUCCESSFULLY!{Colors.NC}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  SOME ISSUES DETECTED{Colors.NC}")

    print("\nNext steps:")
    print(f"  1. Test dashboards: python3 scripts/test_all_dashboard_ports.py --host {DROPLET_IP}")
    print(f"  2. View logs: ssh {DROPLET_USER}@{DROPLET_IP} 'tail -50 /tmp/dash-XXXX.log'")
    print(f"  3. Run diagnostics: ssh {DROPLET_USER}@{DROPLET_IP} 'bash {DROPLET_PATH}/scripts/diagnose_dashboard_ports.sh'")

    print("\n" + "=" * 80 + "\n")

def main():
    """Main deployment process"""
    print("\n" + "=" * 80)
    print(f"{Colors.BLUE}🚀 ASEAGI DASHBOARD DEPLOYMENT TO DROPLET{Colors.NC}")
    print("=" * 80)

    print(f"\nTarget: {DROPLET_USER}@{DROPLET_IP}")
    print(f"Path:   {DROPLET_PATH}")
    print(f"Branch: {GIT_BRANCH}")

    # Step 1: Check SSH
    if not check_ssh_access():
        sys.exit(1)

    # Step 2: Pull code
    if not pull_latest_code():
        print(f"\n{Colors.RED}⚠️  Code pull failed, but continuing...{Colors.NC}")

    # Step 3: Stop dashboards
    if not stop_dashboards():
        print(f"\n{Colors.YELLOW}⚠️  Some dashboards still running, but continuing...{Colors.NC}")

    # Step 4: Start dashboards
    if not start_dashboards():
        print(f"\n{Colors.RED}❌ Some dashboards failed to start{Colors.NC}")
        sys.exit(1)

    # Step 5: Verify
    results = verify_dashboards()

    # Step 6: Summary
    print_summary(results)

    # Exit code
    ok_count = sum(1 for r in results if r["status"] == "running" and r["http_code"] == "200")
    if ok_count == len(results):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
