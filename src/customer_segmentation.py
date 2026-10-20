"""Reproducible RFM clustering and diagnostics for CodeNova Task 4."""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from analytics import build_rfm, evaluate_clusters, run_clustering, segment_profiles

ROOT = Path(__file__).resolve().parents[1]
rfm = build_rfm(ROOT / "data" / "customer_rfm.csv")
results = evaluate_clusters(rfm, 2, min(7, len(rfm) - 1))
results.to_csv(ROOT / "reports" / "cluster_diagnostics.csv", index=False)
valid = results.dropna(subset=["silhouette_score"])
chosen = int(valid.loc[valid["silhouette_score"].idxmax(), "clusters"]) if not valid.empty else 4
model, labels, score, scaled = run_clustering(rfm, chosen)
segmented = rfm.copy()
segmented["segment"] = labels.astype(int)
segmented.to_csv(ROOT / "data" / "processed_customer_segments.csv", index=False)
summary = segment_profiles(segmented)
summary.to_csv(ROOT / "reports" / "segment_profiles.csv", index=False)
figures = ROOT / "reports" / "figures"
figures.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(results.clusters, results.inertia, marker="o", linewidth=2)
ax.axvline(chosen, color="grey", linestyle="--", linewidth=1, label=f"Selected k={chosen}")
ax.set_title("K-Means elbow diagnostic")
ax.set_xlabel("Number of clusters (k)")
ax.set_ylabel("Inertia")
ax.grid(alpha=.25)
ax.legend()
plt.tight_layout()
fig.savefig(figures / "cluster_elbow.png", dpi=180)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(results.clusters, results.silhouette_score, marker="o", linewidth=2)
ax.axvline(chosen, color="grey", linestyle="--", linewidth=1, label=f"Selected k={chosen}")
ax.set_title("Silhouette score by cluster count")
ax.set_xlabel("Number of clusters (k)")
ax.set_ylabel("Silhouette score")
ax.grid(alpha=.25)
ax.legend()
plt.tight_layout()
fig.savefig(figures / "cluster_silhouette.png", dpi=180)
plt.close(fig)

print("Cluster diagnostics:")
print(results.round(3).to_string(index=False))
print(f"\nSelected k by highest tested silhouette score: {chosen} (score={score:.3f})")
print("\nSegment profiles:")
print(summary.round(2).to_string(index=False))
print("\nWrote diagnostics, segment profiles, and customer assignments.")
