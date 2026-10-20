# Data Dictionary

## Sales transactions (`data/sales_raw.csv`)

| Field | Meaning | Expected handling |
|---|---|---|
| `order_date` | Transaction date | Parse as datetime; invalid dates are excluded from transaction analysis |
| `quantity` | Units sold | Numeric and positive |
| `unit_price` | Price per unit | Numeric and positive |
| `discount_rate` | Fractional discount | Expected range 0–1; missing values are assumed to be 0 for this demo |
| `revenue` | Transaction revenue | Recomputed from quantity × unit price × (1 − discount rate) |
| `profit` | Transaction profit | Existing values retained; missing values use a demonstration fallback |
| `category` | Product category | Missing values labelled `Unknown` |
| `product` | Product name | Missing values labelled `Unknown` |
| `region` | Sales region | Missing values labelled `Unknown` |

## Customer RFM (`data/customer_rfm.csv`)

- `recency_days`: days since the customer's latest purchase in the dataset's reference frame.
- `frequency`: purchase frequency measure supplied by the demo dataset.
- `monetary_value`: customer spend measure supplied by the demo dataset.

Confirm definitions with a data owner before using this design with production data.
