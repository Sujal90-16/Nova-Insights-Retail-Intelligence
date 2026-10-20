# Known Limitations

- The bundled data is synthetic and is intended for demonstration only.
- The profit fallback assumes 20% of revenue when profit is missing; it is not a verified margin.
- Revenue is recomputed from quantity, price, and discount; this may differ from source-system accounting rules.
- IQR outliers are flags for review, not automatic evidence of incorrect data.
- RFM segments depend on the supplied RFM values, selected cluster count, and K-Means assumptions.
- Dashboard findings should be interpreted as exploratory rather than causal.
