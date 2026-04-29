"""MCP prompt definitions for the Subscription Tracker server."""


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
