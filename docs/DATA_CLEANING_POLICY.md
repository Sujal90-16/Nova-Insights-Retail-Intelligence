# Data Cleaning Policy

1. Preserve raw source data.
2. Remove exact duplicate transaction rows from the analysis copy.
3. Exclude rows with invalid dates, missing/non-positive quantity, or missing/non-positive unit price.
4. Fill missing category, product, and region with `Unknown`.
5. Fill missing discounts with 0 and clip discount rates to the interval [0, 1].
6. Recompute revenue to make the formula explicit and consistent.
7. Retain valid existing profit values; use the documented 20% revenue fallback only where profit is missing.
8. Report IQR outliers for review instead of deleting them automatically.

These are demonstration assumptions, not universal accounting rules. Confirm returns, tax, shipping, revenue recognition, and margin definitions before using real commercial data.
