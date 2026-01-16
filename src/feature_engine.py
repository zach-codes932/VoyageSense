
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.compose import ColumnTransformer

# Paths
DATA_PATH = r"D:\Travel RS\data\processed\destinations_with_sentiment.csv"
ARTIFACTS_DIR = r"D:\Travel RS\data\artifacts"

class TravelFeatureEngine:
    def __init__(self):
        self.column_transformer = None
        self.scaler = None
        self.feature_columns = [
            'type', 'significance', 'duration_bucket', 
            'budget_bucket', 'zone'
        ]
        self.numerical_columns = ['google_rating', 'sentiment_score', 'review_count']
        
    def fit_and_save(self, df):
        print("Fitting feature encoders...")
        
        # Rename CSV columns to match DB/clean schema
        if 'google_review_rating' in df.columns:
            df = df.rename(columns={'google_review_rating': 'google_rating'})

        # 1. Categorical Encoding (One-Hot)
        # We explicitly list categories to handle unseen data gracefull via handle_unknown='ignore'
        # But for valid recommendation, we try to match vocab.
        
        self.column_transformer = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), self.feature_columns),
                ('num', MinMaxScaler(), self.numerical_columns)
            ],
            remainder='drop'  # Drop name, city, etc. from the vector
        )
        
        # Fit on the entire dataset
        self.column_transformer.fit(df)
        
        # Save the transformer
        if not os.path.exists(ARTIFACTS_DIR):
            os.makedirs(ARTIFACTS_DIR)
            
        with open(os.path.join(ARTIFACTS_DIR, "feature_encoder.pkl"), "wb") as f:
            pickle.dump(self.column_transformer, f)
            
        print("Encoders saved successfully.")
        
    def load_encoders(self):
        with open(os.path.join(ARTIFACTS_DIR, "feature_encoder.pkl"), "rb") as f:
            self.column_transformer = pickle.load(f)
    
    def transform(self, df):
        if self.column_transformer is None:
            self.load_encoders()
        return self.column_transformer.transform(df)

    def create_user_vector(self, user_dict):
        """
        Converts user UI inputs into the same vector space as destinations.
        user_dict examples:
        {
            'type': 'Nature',
            'significance': 'Relaxation',
            'duration_bucket': 'Short',
            'budget_bucket': 'Low',
            'zone': 'Northern'
            # Numerical preferences are defaulted or derived
        }
        """
        # Create a single-row DataFrame
        user_df = pd.DataFrame([user_dict])
        
        # We need to ensure columns exist. 
        # Add numerical cols with "ideal" values
        # e.g., User wants 5.0 rating, 1.0 sentiment, 1000 reviews (popularity)
        user_df['google_rating'] = 4.8
        user_df['sentiment_score'] = 0.9
        user_df['review_count'] = 100  # Reasonable popularity
        
        # Ensure vectors align
        return self.transform(user_df)

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    engine = TravelFeatureEngine()
    engine.fit_and_save(df)
    
    # Test Transformation
    vectors = engine.transform(df)
    print(f"Feature Matrix Shape: {vectors.shape}")
    
    # Test User Vector
    dummy_user = {
        'type': 'Type_to_replace', # Will be ignored if not in vocab or handled
        'significance': 'Historical',
        'duration_bucket': 'Short',
        'budget_bucket': 'Low',
        'zone': 'Northern'
    }
    # Note: 'type' in DF has many values. Let's pick one valid one for testing
    dummy_user['type'] = df['type'].iloc[0] 
    
    uv = engine.create_user_vector(dummy_user)
    print(f"User Vector Shape: {uv.shape}")
