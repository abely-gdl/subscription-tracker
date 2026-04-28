"""Subscription Tracker MCP Server."""
import json
import logging
from datetime import date, timedelta
from typing import Any

from mcp.server.fastmcp import FastMCP

import api_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("subscription-tracker")


# ── TOOLS ────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_subscription(subscription_id: str) -> dict[str, Any]:
    """Retrieve a single subscription by its UUID."""
    return api_client.get_subscription(subscription_id)


@mcp.tool()
def get_all_subscriptions() -> list[dict[str, Any]]:
    """Return all subscriptions regardless of status."""
    return api_client.get_all_subscriptions()


@mcp.tool()
def add_subscription(
    name: str,
    cost: float,
    billing_cycle: str,
    category: str,
    renewal_date: str,
    status: str = "Active",
) -> dict[str, Any]:
    """Create a new subscription.

    billing_cycle: 'Monthly' or 'Annual'
    status: 'Active', 'Paused', or 'Cancelled'
    renewal_date: ISO-8601 date string (YYYY-MM-DD)
    """
    return api_client.add_subscription({
        "name": name,
        "cost": cost,
        "billingCycle": billing_cycle,
        "category": category,
        "renewalDate": renewal_date,
        "status": status,
    })


@mcp.tool()
def update_subscription(
    subscription_id: str,
    name: str | None = None,
    cost: float | None = None,
    billing_cycle: str | None = None,
    category: str | None = None,
    renewal_date: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    """Partially update a subscription — pass only the fields to change."""
    payload: dict[str, Any] = {}
    if name is not None:
        payload["name"] = name
    if cost is not None:
        payload["cost"] = cost
    if billing_cycle is not None:
        payload["billingCycle"] = billing_cycle
    if category is not None:
        payload["category"] = category
    if renewal_date is not None:
        payload["renewalDate"] = renewal_date
    if status is not None:
        payload["status"] = status
    return api_client.update_subscription(subscription_id, payload)


@mcp.tool()
def delete_subscription(subscription_id: str) -> dict[str, bool]:
    """Delete a subscription by UUID. Returns {deleted: true/false}."""
    deleted = api_client.delete_subscription(subscription_id)
    return {"deleted": deleted}


@mcp.tool()
def get_subscriptions_by_category(category: str) -> list[dict[str, Any]]:
    """Return all subscriptions matching a category (case-insensitive)."""
    return api_client.get_subscriptions_by_category(category)


# ── RESOURCES ────────────────────────────────────────────────────────────────

@mcp.resource("subscriptions://all")
def resource_all() -> str:
    """All subscriptions as JSON."""
    return json.dumps(api_client.get_all_subscriptions(), indent=2)


@mcp.resource("subscriptions://active")
def resource_active() -> str:
    """Only Active subscriptions."""
    subs = [s for s in api_client.get_all_subscriptions() if s.get("status") == "Active"]
    return json.dumps(subs, indent=2)


@mcp.resource("subscriptions://expiring-soon")
def resource_expiring_soon() -> str:
    """Subscriptions whose renewalDate falls within the next 7 days."""
    today = date.today()
    cutoff = today + timedelta(days=7)
    subs = [
        s for s in api_client.get_all_subscriptions()
        if today <= date.fromisoformat(s["renewalDate"]) <= cutoff
    ]
    return json.dumps(subs, indent=2)


@mcp.resource("subscriptions://monthly-cost")
def resource_monthly_cost() -> str:
    """Aggregated monthly cost across all Active subscriptions, broken down by category."""
    subs = [s for s in api_client.get_all_subscriptions() if s.get("status") == "Active"]
    by_category: dict[str, float] = {}
    total = 0.0
    for s in subs:
        monthly = s["cost"] if s["billingCycle"] == "Monthly" else s["cost"] / 12
        by_category[s["category"]] = by_category.get(s["category"], 0.0) + monthly
        total += monthly
    return json.dumps({
        "totalMonthly": round(total, 2),
        "byCategory": {k: round(v, 2) for k, v in by_category.items()},
    }, indent=2)


# ── PROMPTS ──────────────────────────────────────────────────────────────────

@mcp.prompt()
def monthly_summary() -> str:
    """Prompt: generate a monthly spending summary."""
    return (
        "Using the subscriptions://monthly-cost resource and get_all_subscriptions tool, "
        "produce a concise Markdown report titled '## Monthly Subscription Summary' that includes:\n"
        "- Total monthly spend\n"
        "- Spend breakdown by category (table format)\n"
        "- Top 3 most expensive subscriptions\n"
        "- Any paused or cancelled subscriptions that could be removed\n"
        "Format all currency values as USD with 2 decimal places."
    )


@mcp.prompt()
def renewal_alerts() -> str:
    """Prompt: generate a renewal alerts report."""
    return (
        "Using the subscriptions://expiring-soon resource, "
        "produce a Markdown report titled '## Upcoming Renewal Alerts (Next 7 Days)' that includes:\n"
        "- A list of subscriptions renewing within 7 days, sorted by renewalDate ascending\n"
        "- For each: Name, Cost, BillingCycle, RenewalDate, Category\n"
        "- A short action recommendation for each (renew, cancel, or review)\n"
        "If no renewals are due within 7 days, state that explicitly."
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
