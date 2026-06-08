"""Analyze the master events dataset."""
import pandas as pd

df = pd.read_csv("datasets/omnipulse_master_events.csv")
print("MASTER EVENTS DATASET:")
print(f"  Total rows: {len(df):,}")
print(f"  Unique customers: {df['customer_id'].nunique():,}")
print(f"  Unique products: {df['product_id'].nunique():,}")
print()
print("  Event types:")
for et, cnt in df["event_type"].value_counts().items():
    print(f"    {et:25s}: {cnt:,}")
print()
print("  Sentiments:")
for s, cnt in df["sentiment"].value_counts().items():
    print(f"    {s:15s}: {cnt:,}")
print()
print("  Emotions:")
for e, cnt in df["emotion"].value_counts().items():
    print(f"    {e:15s}: {cnt:,}")
print()
print("  Campaigns:")
for c, cnt in df["campaign_name"].dropna().value_counts().items():
    print(f"    {c:35s}: {cnt:,}")
print()
print("  Channels:")
for ch, cnt in df["channel"].value_counts().items():
    print(f"    {ch:20s}: {cnt:,}")

print()
print("  Cities:")
for c, cnt in df["city"].value_counts().head(15).items():
    print(f"    {c:20s}: {cnt:,}")

print()
print("  Revenue stats:")
rev = df["revenue"]
print(f"    Total revenue: {rev.sum():,.0f}")
print(f"    Non-zero revenue rows: {(rev > 0).sum():,}")
print(f"    Max revenue: {rev.max():,.0f}")

# Check AI predictions
print("\n\nAI PREDICTIONS DATASET:")
pred = pd.read_csv("datasets/ai_predictions.csv")
print(f"  Total rows: {len(pred):,}")
print(f"  Unique customers: {pred['customer_id'].nunique():,}")
print()
print("  Personas:")
for p, cnt in pred["persona"].value_counts().items():
    print(f"    {p:25s}: {cnt:,}")
print()
print("  NBA Actions:")
for a, cnt in pred["nba_action"].value_counts().items():
    print(f"    {a:30s}: {cnt:,}")
print()
print("  Offers:")
for o, cnt in pred["offer"].value_counts().items():
    print(f"    {o:30s}: {cnt:,}")
print()
print("  Digital Twin Outcomes:")
for o, cnt in pred["digital_twin_outcome"].value_counts().items():
    print(f"    {o:35s}: {cnt:,}")
print()
print("  Channels:")
for ch, cnt in pred["recommended_channel"].value_counts().items():
    print(f"    {ch:20s}: {cnt:,}")

# Check overlap
master_custs = set(df["customer_id"].unique())
pred_custs = set(pred["customer_id"].unique())
overlap = master_custs & pred_custs
print(f"\n  Overlap with master events: {len(overlap):,} / {len(pred_custs):,}")
