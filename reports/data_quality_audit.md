# Data Quality Audit — Nova Insights

## Summary
- Raw rows: **1,205**
- Exact duplicate rows flagged: **5**
- Missing cells in raw file: **55**
- Invalid core transaction rows excluded: **18**
- Missing profit values filled with the demonstration fallback: **0**
- Clean rows: **1,182**

## Cleaning decisions
1. The raw CSV is never modified.
2. Exact duplicate rows are removed.
3. Rows with invalid dates, missing/non-positive quantity, or missing/non-positive unit price are excluded from sales analysis.
4. Missing category/product/region values become `Unknown`; missing discounts become 0 and are clipped to [0, 1].
5. Revenue is recomputed from quantity, unit price, and discount so totals reconcile.
6. Existing profit values are retained; missing profit values use a clearly marked 20% revenue fallback. This is only a synthetic demonstration assumption.
7. IQR outliers are reported for investigation rather than automatically deleted.

## Before/after field profile

| column        |   missing_before |   missing_after |   outlier_count |
|:--------------|-----------------:|----------------:|----------------:|
| order_id      |                0 |               0 |               0 |
| order_date    |                0 |               0 |               0 |
| customer_id   |                0 |               0 |               0 |
| category      |                0 |               0 |               0 |
| product       |                9 |               0 |               0 |
| region        |               32 |               0 |               0 |
| quantity      |                0 |               0 |               0 |
| unit_price    |                0 |               0 |             119 |
| discount_rate |               14 |               0 |               0 |
| revenue       |                0 |               0 |              82 |
| profit        |                0 |               0 |              77 |

## Limitations
The bundled dataset is synthetic. For real data, confirm revenue, profit, returns, taxes, and discounts with the data owner before reporting results. The combined issue count is not a count of unique affected records.
