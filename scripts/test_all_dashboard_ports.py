#!/usr/bin/env python3
"""
Test all dashboard ports via HTTP to verify they're serving unique content
Can run locally or on droplet
"""

import requests
import sys
from typing import Dict, List
from bs4 import BeautifulSoup

# Dashboard port configuration
DASHBOARDS = {
    8501: {
        "name": "PROJ344 Master Dashboard",
        "expected": "ALL documents",
        "keywords": ["745 documents", "PROJ344", "All Legal Documents"]
    },
    8502: {
        "name": "CEO Dashboard",
        "expected": "File organization",
        "keywords": ["CEO Dashboard", "File Organization", "Document Management"]
    },
    8503: {
        "name": "Legal Intelligence",
        "expected": "High-value docs ≥700",
        "keywords": ["Legal Intelligence", "High-Value", "relevancy ≥ 700"]
    },
    8504: {
        "name": "Enhanced Scanning Monitor",
        "expected": "Scanning with Supabase",
        "keywords": ["Enhanced", "Scanning Monitor", "Database Documents"]
    },
    8505: {
        "name": "Scanning Monitor",
        "expected": "Basic scanning",
        "keywords": ["Scanning Monitor", "Document Processing"]
    },
    8506: {
        "name": "Timeline Violations",
        "expected": "Timeline analysis",
        "keywords": ["Timeline Violations", "Court Events"]
    },
    8507: {
        "name": "System Overview",
        "expected": "Database health",
        "keywords": ["System Overview", "Database Health", "Table Metrics"]
    }
}

def test_port(host: str, port: int) -> Dict:
    """Test a single port and extract page info"""
    url = f"http://{host}:{port}"

    result = {
        "port": port,
        "name": DASHBOARDS[port]["name"],
        "status": "unknown",
        "http_code": None,
        "title": None,
        "keywords_found": [],
        "error": None
    }

    try:
        print(f"  Testing {url}...", end=" ")
        response = requests.get(url, timeout=5)
        result["http_code"] = response.status_code

        if response.status_code != 200:
            result["status"] = "error"
            result["error"] = f"HTTP {response.status_code}"
            print(f"❌ {response.status_code}")
            return result

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get title
        title_tag = soup.find('title')
        if title_tag:
            result["title"] = title_tag.get_text().strip()

        # Get page text
        page_text = soup.get_text()

        # Check for expected keywords
        expected_keywords = DASHBOARDS[port]["keywords"]
        for keyword in expected_keywords:
            if keyword.lower() in page_text.lower():
                result["keywords_found"].append(keyword)

        # Determine status
        if len(result["keywords_found"]) > 0:
            result["status"] = "ok"
            print(f"✅ OK")
        else:
            result["status"] = "mismatch"
            print(f"⚠️  Content mismatch")

    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["error"] = "Connection timeout"
        print(f"⏱️  Timeout")
    except requests.exceptions.ConnectionError:
        result["status"] = "not_running"
        result["error"] = "Connection refused"
        print(f"❌ Not running")
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"❌ Error: {e}")

    return result

def test_all_dashboards(host: str = "localhost") -> List[Dict]:
    """Test all dashboard ports"""
    print("\n" + "=" * 80)
    print(f"🔍 TESTING ALL DASHBOARD PORTS ON {host}")
    print("=" * 80 + "\n")

    results = []

    for port in sorted(DASHBOARDS.keys()):
        info = DASHBOARDS[port]
        print(f"\n{'─' * 80}")
        print(f"📊 Port {port}: {info['name']}")
        print(f"   Expected: {info['expected']}")

        result = test_port(host, port)
        results.append(result)

        if result["title"]:
            print(f"   Title: {result['title']}")

        if result["keywords_found"]:
            print(f"   ✅ Found keywords: {', '.join(result['keywords_found'])}")
        else:
            print(f"   ⚠️  Expected keywords NOT found: {', '.join(info['keywords'])}")

    return results

def print_summary(results: List[Dict]):
    """Print test summary"""
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80 + "\n")

    ok_count = sum(1 for r in results if r["status"] == "ok")
    mismatch_count = sum(1 for r in results if r["status"] == "mismatch")
    error_count = sum(1 for r in results if r["status"] in ["error", "timeout", "not_running"])

    print(f"✅ OK:           {ok_count}/{len(results)}")
    print(f"⚠️  Mismatch:     {mismatch_count}/{len(results)}")
    print(f"❌ Errors:       {error_count}/{len(results)}")

    if mismatch_count > 0:
        print("\n⚠️  CONTENT MISMATCHES DETECTED:")
        for r in results:
            if r["status"] == "mismatch":
                print(f"   Port {r['port']}: {r['name']}")
                print(f"     Expected: {DASHBOARDS[r['port']]['expected']}")
                print(f"     Check: The dashboard may be serving wrong content")

    if error_count > 0:
        print("\n❌ ERRORS DETECTED:")
        for r in results:
            if r["status"] in ["error", "timeout", "not_running"]:
                print(f"   Port {r['port']}: {r['name']} - {r['error']}")

    print("\n" + "=" * 80)

    if ok_count == len(results):
        print("✅ ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED - See details above")

    print("=" * 80 + "\n")

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Test all dashboard ports')
    parser.add_argument('--host', default='localhost', help='Host to test (default: localhost)')
    args = parser.parse_args()

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌ ERROR: beautifulsoup4 not installed")
        print("\nInstall with:")
        print("  pip3 install beautifulsoup4")
        sys.exit(1)

    results = test_all_dashboards(args.host)
    print_summary(results)

    # Exit code based on results
    if any(r["status"] != "ok" for r in results):
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
