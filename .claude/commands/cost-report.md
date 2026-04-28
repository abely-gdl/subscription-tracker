# Cost Report

Generate a spending breakdown report across all subscriptions.

## Steps

1. Call the MCP tool `get_all_subscriptions` to fetch all subscription data.
2. Read the MCP resource `subscriptions://monthly-cost` for pre-aggregated monthly totals.
3. Produce the following Markdown report:

---

## Subscription Cost Report — {today's date}

### Summary
| Metric | Value |
|--------|-------|
| Total Subscriptions | N |
| Active | N |
| Paused / Cancelled | N |
| **Total Monthly Cost** | **$X.XX** |
| **Total Annual Cost** | **$X.XX** |

### By Category
| Category | # Subs | Monthly Cost | Annual Cost |
|----------|--------|-------------|-------------|
| Streaming | 3 | $X.XX | $X.XX |
| ... | | | |

### Monthly Subscriptions
| Name | Category | Cost/Month |
|------|----------|------------|

### Annual Subscriptions
| Name | Category | Cost/Month* | Annual Total |
|------|----------|-------------|--------------|

*Monthly equivalent (annual ÷ 12)

### Paused / Cancelled (excluded from totals)
| Name | Category | Status | Cost |
|------|----------|--------|------|

---

## Notes
- Annual costs divided by 12 for monthly equivalents.
- Paused and Cancelled subscriptions are excluded from cost totals.
- All amounts in USD with 2 decimal places.
