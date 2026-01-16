
import pandas as pd
try:
    df = pd.read_csv(r'D:\Travel RS\data\raw\tripadvisor_hotel_reviews.csv')
    print("--- First 5 Reviews Sample ---")
    for i, review in enumerate(df['Review'].head(5)):
        print(f"Review {i+1}: {review[:200]}...") 
        print("-" * 20)
except Exception as e:
    print(e)
