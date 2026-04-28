# Spending Forecast

Project subscription costs forward 12 months based on renewal dates and billing cycles.

## Steps

1. Call `get_all_subscriptions` — filter to Active subscriptions only.
2. For each of the next 12 calendar months (starting from next month):
   - **Monthly billing**: add the subscription cost every month.
   - **Annual billing**: add the full annual cost only in the month where the day matches the subscription's `renewalDate` day-of-month (i.e., the renewal month).
3. Produce the following Markdown report:

---

## 12-Month Spending Forecast — {start month} to {end month}

### Month-by-Month Projection
| Month | Recurring (Monthly Subs) | Annual Renewals | Total |
|-------|--------------------------|-----------------|-------|
| May 2026 | $X.XX | $X.XX | $X.XX |
| Jun 2026 | $X.XX | — | $X.XX |
| ... | | | |

### Annual Renewals Detail
List each annual subscription with its renewal month and cost.

| Subscription | Category | Annual Cost | Renewal Month |
|-------------|----------|-------------|---------------|

### Highlights
- **Average monthly spend**: $X.XX
- **Peak month**: {month} — $X.XX (due to annual renewals: {list})
- **Lightest month**: {month} — $X.XX

---

## Notes
- Only Active subscriptions are included.
- Annual billing charges the full annual cost in the renewal month.
- Paused/Cancelled subscriptions are excluded.
