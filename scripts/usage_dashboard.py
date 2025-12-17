#!/usr/bin/env python3
"""
Real-time Claude API Usage Dashboard
Track costs as you use Claude Code
"""

import os
import json
from datetime import datetime
from pathlib import Path

class UsageTracker:
    """Track Claude API usage locally"""

    def __init__(self, log_file: str = None):
        if log_file is None:
            log_file = Path.home() / ".claude_usage_log.jsonl"
        self.log_file = Path(log_file)

    def log_request(self, model: str, input_tokens: int, output_tokens: int,
                    task: str = "general", workspace: str = "default"):
        """Log an API request"""

        # Calculate cost
        pricing = {
            "sonnet": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
            "opus": {"input": 15.00 / 1_000_000, "output": 75.00 / 1_000_000},
            "haiku": {"input": 0.25 / 1_000_000, "output": 1.25 / 1_000_000}
        }

        # Determine model type
        model_type = "sonnet"
        if "opus" in model.lower():
            model_type = "opus"
        elif "haiku" in model.lower():
            model_type = "haiku"

        cost = (input_tokens * pricing[model_type]["input"] +
                output_tokens * pricing[model_type]["output"])

        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "model_type": model_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": cost,
            "task": task,
            "workspace": workspace
        }

        # Append to log
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def get_summary(self, days: int = 30):
        """Get usage summary for last N days"""
        if not self.log_file.exists():
            return {"total_cost": 0, "total_tokens": 0, "requests": 0}

        total_cost = 0
        total_tokens = 0
        requests = 0
        by_task = {}
        by_model = {}

        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    total_cost += entry["cost"]
                    total_tokens += entry["total_tokens"]
                    requests += 1

                    # By task
                    task = entry["task"]
                    if task not in by_task:
                        by_task[task] = {"cost": 0, "tokens": 0, "count": 0}
                    by_task[task]["cost"] += entry["cost"]
                    by_task[task]["tokens"] += entry["total_tokens"]
                    by_task[task]["count"] += 1

                    # By model
                    model = entry["model_type"]
                    if model not in by_model:
                        by_model[model] = {"cost": 0, "tokens": 0, "count": 0}
                    by_model[model]["cost"] += entry["cost"]
                    by_model[model]["tokens"] += entry["total_tokens"]
                    by_model[model]["count"] += 1

                except:
                    continue

        return {
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "requests": requests,
            "by_task": by_task,
            "by_model": by_model
        }

    def print_summary(self):
        """Print formatted summary"""
        summary = self.get_summary()

        print("\n" + "=" * 70)
        print("📊 CLAUDE API USAGE SUMMARY")
        print("=" * 70)
        print(f"\n💰 Total Cost:    ${summary['total_cost']:>10.4f}")
        print(f"🎯 Total Tokens:  {summary['total_tokens']:>10,}")
        print(f"📡 Total Requests: {summary['requests']:>10,}")

        if summary['by_model']:
            print("\n" + "-" * 70)
            print("By Model:")
            for model, stats in summary['by_model'].items():
                print(f"\n  {model.upper()}:")
                print(f"    Requests: {stats['count']:>6,}")
                print(f"    Tokens:   {stats['tokens']:>10,}")
                print(f"    Cost:     ${stats['cost']:>8.4f}")

        if summary['by_task']:
            print("\n" + "-" * 70)
            print("By Task:")
            sorted_tasks = sorted(summary['by_task'].items(),
                                 key=lambda x: x[1]['cost'], reverse=True)
            for task, stats in sorted_tasks[:10]:  # Top 10
                print(f"\n  {task}:")
                print(f"    Requests: {stats['count']:>6,}")
                print(f"    Tokens:   {stats['tokens']:>10,}")
                print(f"    Cost:     ${stats['cost']:>8.4f}")

        print("\n" + "=" * 70)

if __name__ == "__main__":
    tracker = UsageTracker()

    # Example: Log this session
    tracker.log_request(
        model="claude-sonnet-4-20250514",
        input_tokens=96000,
        output_tokens=5000,
        task="claude_code_session",
        workspace="ASEAGI"
    )

    # Show summary
    tracker.print_summary()

    print("\n✅ Usage logged to:", tracker.log_file)
    print("\n💡 To view official usage:")
    print("   open https://console.anthropic.com/settings/usage")
