# Customer Segmentation Method

The demo uses Recency, Frequency, and Monetary value (RFM) features. Features are standardized before K-Means so that different scales do not dominate Euclidean distance simply because of their units.

The number of clusters is a modeling choice rather than a ground-truth label. Use inertia/elbow and silhouette diagnostics as supporting evidence, inspect cluster profiles, and verify whether the segments are actionable. A silhouette score measures separation/cohesion in feature space; it does not prove business value.

Segment names are descriptive interpretations of the demo profiles, not validated customer personas.
