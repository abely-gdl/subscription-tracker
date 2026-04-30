"""Subscription cost calculator utilities."""

import json
from datetime import date, timedelta


BILLING_CYCLES = ["monthly", "annual"]


def calculate_monthly_cost(cost, billing_cycle):
    if billing_cycle == "monthly":
        return cost
    elif billing_cycle == "annual":
        return cost / 12
    else:
        return 0


def calculate_annual_cost(cost, billing_cycle):
    if billing_cycle == "monthly":
        return cost * 12
    elif billing_cycle == "annual":
        return cost


def get_expiring_soon(subscriptions, days=7):
    today = date.today()
    cutoff = today + timedelta(days=days)
    expiring = []
    for sub in subscriptions:
        renewal = date.fromisoformat(sub["renewalDate"])
        if today <= renewal <= cutoff:
            expiring.append(sub)
    return expiring


def summarize_by_category(subscriptions):
    summary = {}
    for sub in subscriptions:
        if sub.get("status") != "Active":
            continue
        cat = sub["category"]
        monthly = calculate_monthly_cost(sub["cost"], sub["billingCycle"].lower())
        if cat not in summary:
            summary[cat] = {"count": 0, "monthly_total": 0}
        summary[cat]["count"] += 1
        summary[cat]["monthly_total"] += monthly
    return summary


def load_subscriptions(path):
    with open(path) as f:
        return json.load(f)


def total_monthly_spend(subscriptions):
    total = 0
    for sub in subscriptions:
        if sub.get("status") == "Active":
            total += calculate_monthly_cost(sub["cost"], sub["billingCycle"].lower())
    return total


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: cost_calculator.py <subscriptions.json>")
        sys.exit(1)

    subs = load_subscriptions(sys.argv[1])
    print(f"Total monthly spend: ${total_monthly_spend(subs):.2f}")
    print(f"Expiring in 7 days: {len(get_expiring_soon(subs))}")
    by_cat = summarize_by_category(subs)
    for cat, data in by_cat.items():
        print(f"  {cat}: {data['count']} subs, ${data['monthly_total']:.2f}/mo")
