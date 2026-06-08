"""Dataset Discovery - Analyze all 9 datasets"""
import pandas as pd
import os

datasets = {
    'Ecommerce.csv': 'datasets/extracted_archive/Ecommerce.csv',
    'flipkart_com-ecommerce_sample.csv': 'datasets/extracted_archive (1)/flipkart_com-ecommerce_sample.csv',
    'Dataset-SA.csv': 'datasets/extracted_archive (2)/Dataset-SA.csv',
    'List of Orders.csv': 'datasets/extracted_archive (3)/List of Orders.csv',
    'Order Details.csv': 'datasets/extracted_archive (3)/Order Details.csv',
    'Sales target.csv': 'datasets/extracted_archive (3)/Sales target.csv',
    'Mall_Customers.csv': 'datasets/extracted_archive (4)/Mall_Customers.csv',
    'omnipulse_master_events.csv': 'datasets/omnipulse_master_events.csv',
    'ai_predictions.csv': 'datasets/ai_predictions.csv',
}

print("="*70)
print("DATASET DISCOVERY REPORT")
print("="*70)

for name, path in datasets.items():
    if os.path.exists(path):
        df = pd.read_csv(path, nrows=3)
        print(f"\n{name}:")
        print(f"  Path: {path}")
        print(f"  Columns ({len(df.columns)}): {', '.join(df.columns.tolist())}")
        print(f"  Sample rows: {df.shape[0]}")
    else:
        print(f"\n{name}: NOT FOUND at {path}")
