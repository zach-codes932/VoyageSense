
import pandas as pd
import numpy as np
import os
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download VADER lexicon if not present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# Paths
RAW_DIR = r"D:\Travel RS\data\raw"
PROCESSED_DIR = r"D:\Travel RS\data\processed"
DEST_FILE = os.path.join(RAW_DIR, "Top Indian Places to Visit.csv")
REVIEW_FILE = os.path.join(RAW_DIR, "tripadvisor_hotel_reviews.csv")
OUTPUT_FILE = os.path.join(PROCESSED_DIR, "destinations_with_sentiment.csv")

def clean_destinations(df):
    print("Cleaning Destinations Dataset...")
    # Drop index column if exists
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    
    # Fix 'Establishment Year' if needed (dropping for now as agreed)
    if 'Establishment Year' in df.columns:
        df = df.drop(columns=['Establishment Year'])

    # Convert 'time needed to visit in hrs' to numeric
    # Some values might be "1.5", others might be dirty.
    df['time_needed_hrs'] = pd.to_numeric(df['time needed to visit in hrs'], errors='coerce').fillna(2.0) # Default to 2 hours
    
    # Create duration buckets (Task 1.3)
    # < 5 hours (~ half day) = Short
    # 5 - 24 hours (1 day) = Medium
    # > 24 hours = Long
    labels = ['Short', 'Medium', 'Long']
    df['duration_bucket'] = pd.cut(df['time_needed_hrs'], bins=[-1, 5, 24, 1000], labels=labels)

    # Clean Entrance Fee
    # Assuming 'Entrance Fee in INR' is numeric, but let's force it
    df['entrance_fee'] = pd.to_numeric(df['Entrance Fee in INR'], errors='coerce').fillna(0)
    
    # Bucket Budget
    # 0 = Free
    # 1 - 500 = Low
    # 500+ = High
    df['budget_bucket'] = pd.cut(df['entrance_fee'], bins=[-1, 0, 500, 100000], labels=['Free', 'Low', 'High'])

    return df

def synthetic_review_mapping(dest_df, review_df):
    print("Performing Synthetic Review Mapping...")
    
    # Initialize VADER
    sia = SentimentIntensityAnalyzer()
    
    # Add sentiment columns
    dest_df['sentiment_score'] = 0.0
    dest_df['review_count'] = 0
    dest_df['sample_reviews'] = "" # Storing a few review texts for explainability

    # Strategy:
    # 1. Split reviews into High (4-5 stars) and Low/Mid (1-3 stars) bins
    positive_reviews = review_df[review_df['Rating'] >= 4]['Review'].tolist()
    mixed_reviews = review_df[review_df['Rating'] < 4]['Review'].tolist()
    
    # 2. Iterate destinations
    # If Google Rating >= 4.0 -> Assign mostly positive reviews
    # Else -> Assign mixed reviews
    
    processed_count = 0
    
    for idx, row in dest_df.iterrows():
        rating = row['Google review rating']
        
        # Decide how many reviews to assign (Random between 3 to 10 for realism)
        num_reviews = np.random.randint(3, 11)
        
        if rating >= 4.0:
            # 80% chance of positive review
            chosen_reviews = []
            for _ in range(num_reviews):
                if np.random.random() < 0.8 and positive_reviews:
                    chosen_reviews.append(np.random.choice(positive_reviews))
                elif mixed_reviews:
                    chosen_reviews.append(np.random.choice(mixed_reviews))
        else:
            # 60% chance of mixed review
            chosen_reviews = []
            for _ in range(num_reviews):
                if np.random.random() < 0.6 and mixed_reviews:
                    chosen_reviews.append(np.random.choice(mixed_reviews))
                elif positive_reviews:
                    chosen_reviews.append(np.random.choice(positive_reviews))
        
        # 3. Calculate Average Sentiment Score using VADER
        scores = [sia.polarity_scores(r)['compound'] for r in chosen_reviews]
        avg_score = np.mean(scores) if scores else 0.0
        
        dest_df.at[idx, 'sentiment_score'] = round(avg_score, 4)
        dest_df.at[idx, 'review_count'] = num_reviews
        # Store first 2 reviews as sample text (truncated)
        dest_df.at[idx, 'sample_reviews'] = " || ".join([r[:100] + "..." for r in chosen_reviews[:2]])
        
        processed_count += 1
        if processed_count % 50 == 0:
            print(f"Processed {processed_count} destinations...")

    return dest_df

def main():
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)

    # Load Data
    print("Loading datasets...")
    dest_df = pd.read_csv(DEST_FILE)
    review_df = pd.read_csv(REVIEW_FILE)

    # Step 1: Clean Destinations
    dest_df = clean_destinations(dest_df)

    # Step 2: Synthetic Mapping & NLP
    final_df = synthetic_review_mapping(dest_df, review_df)

    # Clean Column Names (Standardize)
    final_df.columns = [c.strip().replace(" ", "_").lower() for c in final_df.columns]

    # Save
    print(f"Saving to {OUTPUT_FILE}...")
    final_df.to_csv(OUTPUT_FILE, index=False)
    print("Processing Complete!")
    print(final_df[['name', 'google_review_rating', 'sentiment_score', 'duration_bucket', 'budget_bucket']].head())

if __name__ == "__main__":
    main()
