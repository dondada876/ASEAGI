#!/usr/bin/env python3
"""
Claude API Usage Tracker
Monitors your Anthropic API usage and costs
"""

import os
import json
from datetime import datetime, timedelta
from anthropic import Anthropic

# Pricing (as of 2024)
PRICING = {
    "claude-sonnet-4-20250514": {
        "input": 3.00 / 1_000_000,   # $3 per 1M tokens
        "output": 15.00 / 1_000_000   # $15 per 1M tokens
    },
    "claude-opus-4-20250514": {
        "input": 15.00 / 1_000_000,
        "output": 75.00 / 1_000_000
    },
    "claude-3-5-haiku-20241022": {
        "input": 0.25 / 1_000_000,
        "output": 1.25 / 1_000_000
    }
}

def get_usage_stats():
    """Get usage statistics from Anthropic API"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Note: Anthropic doesn't have a usage API endpoint yet
    # You'll need to check console.anthropic.com
    # This is a placeholder for when they add it

    print("📊 Anthropic API Usage Tracker")
    print("=" * 50)
    print()
    print("⚠️  Currently, usage must be checked manually at:")
    print("   https://console.anthropic.com/settings/usage")
    print()
    print("💡 Tip: You can:")
    print("   1. Set up budget alerts in the console")
    print("   2. Export usage data to CSV")
    print("   3. Track per API key")
    print()

def estimate_cost(input_tokens: int, output_tokens: int, model: str = "claude-sonnet-4-20250514"):
    """Estimate cost for a request"""
    pricing = PRICING.get(model, PRICING["claude-sonnet-4-20250514"])

    input_cost = input_tokens * pricing["input"]
    output_cost = output_tokens * pricing["output"]
    total_cost = input_cost + output_cost

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "model": model
    }

def format_cost_report(estimates: list):
    """Format a cost report"""
    print("\n💰 Cost Estimate Report")
    print("=" * 70)

    total_input_tokens = sum(e["input_tokens"] for e in estimates)
    total_output_tokens = sum(e["output_tokens"] for e in estimates)
    total_cost = sum(e["total_cost"] for e in estimates)

    print(f"\nTotal Input Tokens:  {total_input_tokens:>12,}")
    print(f"Total Output Tokens: {total_output_tokens:>12,}")
    print(f"\nTotal Cost: ${total_cost:>8.4f}")
    print()

    # Per model breakdown
    models = {}
    for e in estimates:
        model = e["model"]
        if model not in models:
            models[model] = {"input": 0, "output": 0, "cost": 0}
        models[model]["input"] += e["input_tokens"]
        models[model]["output"] += e["output_tokens"]
        models[model]["cost"] += e["total_cost"]

    print("\nBreakdown by Model:")
    print("-" * 70)
    for model, stats in models.items():
        print(f"\n{model}:")
        print(f"  Input:  {stats['input']:>10,} tokens")
        print(f"  Output: {stats['output']:>10,} tokens")
        print(f"  Cost:   ${stats['cost']:>8.4f}")

def save_usage_log(cost_data: dict, log_file: str = "usage_log.jsonl"):
    """Save usage to log file"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        **cost_data
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def example_usage():
    """Example: Calculate cost for typical operations"""
    print("\n📋 Example Cost Calculations")
    print("=" * 70)

    examples = [
        {
            "name": "Document Scanning (1 page)",
            "input": 2000,
            "output": 500,
            "model": "claude-sonnet-4-20250514"
        },
        {
            "name": "Bug Tracking (error log)",
            "input": 1000,
            "output": 200,
            "model": "claude-3-5-haiku-20241022"
        },
        {
            "name": "Complex Analysis",
            "input": 10000,
            "output": 2000,
            "model": "claude-opus-4-20250514"
        },
        {
            "name": "This Claude Code Session (~94K tokens)",
            "input": 94000,
            "output": 0,
            "model": "claude-sonnet-4-20250514"
        }
    ]

    estimates = []
    for ex in examples:
        cost = estimate_cost(ex["input"], ex["output"], ex["model"])
        estimates.append(cost)

        print(f"\n{ex['name']}:")
        print(f"  Model: {ex['model'].split('-')[1].title()}")
        print(f"  Input: {ex['input']:,} tokens")
        print(f"  Output: {ex['output']:,} tokens")
        print(f"  Cost: ${cost['total_cost']:.4f}")

    print("\n" + "=" * 70)
    format_cost_report(estimates)

if __name__ == "__main__":
    get_usage_stats()
    example_usage()

    print("\n✅ To track real usage:")
    print("   1. Visit: https://console.anthropic.com/settings/usage")
    print("   2. Set budget alerts")
    print("   3. Export usage data regularly")
    print()
