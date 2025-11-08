#!/usr/bin/env python3
"""
Promotional Credit Tracker for Claude Code
Track your $1,000 promo credit usage
"""

from datetime import datetime, timedelta
import json
from pathlib import Path

class PromoTracker:
    """Track promotional credit balance"""

    def __init__(self, initial_credit: float = 1000.0):
        self.initial_credit = initial_credit
        self.log_file = Path.home() / ".claude_promo_tracker.json"
        self.load_or_create()

    def load_or_create(self):
        """Load existing tracker or create new one"""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "initial_credit": self.initial_credit,
                "start_date": datetime.now().isoformat(),
                "entries": []
            }
            self.save()

    def save(self):
        """Save tracker data"""
        with open(self.log_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add_entry(self, current_balance: float, notes: str = ""):
        """Add a balance check entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "balance_remaining": current_balance,
            "spent_since_last": 0,
            "notes": notes
        }

        # Calculate spent since last entry
        if self.data["entries"]:
            last_balance = self.data["entries"][-1]["balance_remaining"]
            entry["spent_since_last"] = last_balance - current_balance
        else:
            entry["spent_since_last"] = self.initial_credit - current_balance

        self.data["entries"].append(entry)
        self.save()

        return entry

    def get_stats(self):
        """Calculate usage statistics"""
        if not self.data["entries"]:
            return None

        latest = self.data["entries"][-1]
        total_spent = self.initial_credit - latest["balance_remaining"]

        # Calculate daily burn rate
        start_date = datetime.fromisoformat(self.data["start_date"])
        days_elapsed = (datetime.now() - start_date).days or 1
        daily_burn = total_spent / days_elapsed

        # Estimate days remaining
        days_remaining = latest["balance_remaining"] / daily_burn if daily_burn > 0 else float('inf')

        # Monthly projection
        monthly_projection = daily_burn * 30

        return {
            "initial_credit": self.initial_credit,
            "current_balance": latest["balance_remaining"],
            "total_spent": total_spent,
            "percent_used": (total_spent / self.initial_credit) * 100,
            "days_elapsed": days_elapsed,
            "daily_burn_rate": daily_burn,
            "days_remaining": days_remaining,
            "estimated_end_date": (datetime.now() + timedelta(days=days_remaining)).strftime("%Y-%m-%d"),
            "monthly_projection": monthly_projection,
            "entries_count": len(self.data["entries"])
        }

    def print_report(self):
        """Print formatted report"""
        stats = self.get_stats()

        if not stats:
            print("⚠️  No entries yet. Add your current balance first.")
            return

        print("\n" + "=" * 70)
        print("💳 PROMOTIONAL CREDIT TRACKER")
        print("=" * 70)

        # Current Status
        print(f"\n💰 Current Balance:     ${stats['current_balance']:>8.2f}")
        print(f"📊 Initial Credit:      ${stats['initial_credit']:>8.2f}")
        print(f"💸 Total Spent:         ${stats['total_spent']:>8.2f}")
        print(f"📈 Percent Used:        {stats['percent_used']:>8.1f}%")

        # Usage Rate
        print(f"\n⏱️  Days Elapsed:        {stats['days_elapsed']:>8} days")
        print(f"🔥 Daily Burn Rate:     ${stats['daily_burn_rate']:>8.2f}/day")
        print(f"📅 Days Remaining:      {stats['days_remaining']:>8.0f} days (~{stats['days_remaining']/30:.1f} months)")
        print(f"🎯 Estimated End:       {stats['estimated_end_date']}")

        # Projections
        print(f"\n📊 Monthly Projection:  ${stats['monthly_projection']:>8.2f}/month")

        # Progress Bar
        percent = stats['percent_used']
        bar_length = 50
        filled = int(bar_length * percent / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\n[{bar}] {percent:.1f}%")

        # Warnings
        print("\n" + "-" * 70)
        if percent < 25:
            print("✅ Status: GOOD - Plenty of credit remaining")
        elif percent < 50:
            print("⚠️  Status: WATCH - Quarter credit used")
        elif percent < 75:
            print("🟡 Status: CAUTION - Over half used")
        else:
            print("🔴 Status: LOW - Consider upgrading plan")

        # Recent Activity
        print("\n" + "-" * 70)
        print("Recent Activity (Last 5 entries):")
        for entry in self.data["entries"][-5:]:
            dt = datetime.fromisoformat(entry["timestamp"])
            print(f"\n  {dt.strftime('%Y-%m-%d %H:%M')}")
            print(f"    Balance: ${entry['balance_remaining']:.2f}")
            print(f"    Spent:   ${entry['spent_since_last']:.2f}")
            if entry["notes"]:
                print(f"    Note:    {entry['notes']}")

        print("\n" + "=" * 70)

    def set_alerts(self):
        """Suggest alert thresholds"""
        stats = self.get_stats()
        if not stats:
            return

        print("\n📢 SUGGESTED BUDGET ALERTS:")
        print("-" * 70)

        thresholds = [
            (750, "75% remaining - All good"),
            (500, "50% remaining - Halfway point"),
            (250, "25% remaining - Start planning"),
            (100, "10% remaining - Urgent!"),
            (50, "5% remaining - Critical!")
        ]

        for balance, message in thresholds:
            if stats['current_balance'] > balance:
                print(f"  Set alert at ${balance:>4} - {message}")

        print("\n💡 To set alerts in Anthropic Console:")
        print("   1. Visit: https://console.anthropic.com/settings/limits")
        print("   2. Set custom thresholds based on above")
        print("   3. Enable email notifications")

def main():
    """Main function"""
    print("\n🎉 Promotional Credit Tracker")
    print("=" * 70)
    print("\nYou have a $1,000 promotional credit from Claude Code!")
    print("Let's track your usage...\n")

    tracker = PromoTracker(initial_credit=1000.0)

    # Check if we have entries
    if not tracker.data["entries"]:
        print("📝 First time setup!\n")
        print("Current balance: $876 (as of today)")
        print("Adding entry...")
        tracker.add_entry(
            current_balance=876.0,
            notes="Initial tracking - $124 spent from promotional credit"
        )
        print("✅ Entry added!\n")

    # Show report
    tracker.print_report()

    # Show alert suggestions
    tracker.set_alerts()

    # Usage tips
    print("\n" + "=" * 70)
    print("💡 TIPS TO MAXIMIZE YOUR CREDIT:")
    print("-" * 70)
    print("  1. Use Haiku for simple tasks (1/12th the cost)")
    print("  2. Use bug tracker smart routing (60-80% savings)")
    print("  3. Check balance weekly: python3 scripts/promo_credit_tracker.py")
    print("  4. Set alerts in Anthropic Console")
    print("  5. Export usage data monthly for records")

    print("\n" + "=" * 70)
    print("📍 Tracker saved to:", tracker.log_file)
    print("\n🔗 Quick Links:")
    print("   Balance: https://console.anthropic.com/settings/billing")
    print("   Usage:   https://console.anthropic.com/settings/usage")
    print("   Limits:  https://console.anthropic.com/settings/limits")
    print("\n")

if __name__ == "__main__":
    main()
