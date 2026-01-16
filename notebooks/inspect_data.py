
import pandas as pd
import os

data_dir = r"D:\Travel RS\data\raw"
dest_file = os.path.join(data_dir, "Top Indian Places to Visit.csv")
review_file = os.path.join(data_dir, "tripadvisor_hotel_reviews.csv")

def inspect_csv(filepath, name):
    print(f"--- Inspecting {name} ---")
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        df = pd.read_csv(filepath)
        print(f"Shape: {df.shape}")
        print("\nColumns:")
        print(df.columns.tolist())
        print("\nInfo:")
        print(df.info())
        print("\nMissing Values:")
        print(df.isnull().sum())
        print("\nFirst 3 Rows:")
        print(df.head(3))
        print("\n" + "="*50 + "\n")
    except Exception as e:
        print(f"Error reading {name}: {e}")

inspect_csv(dest_file, "Destinations Dataset")
inspect_csv(review_file, "Reviews Dataset")
