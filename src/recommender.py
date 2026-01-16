
import pandas as pd
import numpy as np
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
from src.feature_engine import TravelFeatureEngine

import os

# Get project root (parent of src)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "travel.db")

class TravelRecommender:
    def __init__(self):
        self.feature_engine = TravelFeatureEngine()
        self.destinations_df = self._load_destinations()
        
        # Pre-compute destination vectors
        # Note: In a large production system, we would cache this.
        if not self.destinations_df.empty:
            self.destination_vectors = self.feature_engine.transform(self.destinations_df)
        else:
            self.destination_vectors = None

    def _load_destinations(self):
        conn = sqlite3.connect(DB_PATH)
        # Read everything needed for encoding + display
        query = "SELECT * FROM destinations"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def recommend(self, user_profile, top_n=5):
        """
        user_profile: Dict containing UI inputs
        Returns: DataFrame of top_n destinations with 'match_score'
        """
        if self.destination_vectors is None:
            return pd.DataFrame()

        # 1. Vectorize User Profile
        user_vector = self.feature_engine.create_user_vector(user_profile)

        # 2. Compute Cosine Similarity
        # Result shape: (1, n_destinations)
        similarity_scores = cosine_similarity(user_vector, self.destination_vectors)
        
        # Flatten to 1D array
        scores = similarity_scores[0]
        
        # 3. Add scores to DataFrame
        results = self.destinations_df.copy()
        results['match_score'] = scores
        
        # 4. Filter & Sort
        # We can apply HARD FILTERS here if needed (Task 5.1), 
        # but for pure ML, we just sort.
        
        # Primary Sort: Match Score (Desc)
        # Secondary Sort: Google Rating (Desc) for tie-breaking
        results = results.sort_values(by=['match_score', 'google_rating'], ascending=[False, False])
        
        # 5. Apply Hard Constraints
        filtered_results = self.filter_by_constraints(results, user_profile)
        
        # 6. Generate Explanations
        # Apply row-wise function to create a human-readable string
        if not filtered_results.empty:
            filtered_results['explanation'] = filtered_results.apply(
                lambda row: self.generate_explanation(row, user_profile), axis=1
            )

        return filtered_results.head(top_n)

    def generate_explanation(self, row, profile):
        """
        Creates a dynamic string explaining why this place was chosen.
        """
        reasons = []
        
        # 1. Match on Interest/Type
        if row['type'] == profile.get('type') or row['significance'] == profile.get('significance'):
            reasons.append(f"Aligms with your interest in {row['type']}/{row['significance']}")
            
        # 2. Match on Budget
        if row['budget_bucket'] == profile.get('budget_bucket'):
            reasons.append(f"matches your {row['budget_bucket']} budget")
        elif row['budget_bucket'] == 'Free' and profile.get('budget_bucket') == 'Low':
             reasons.append("is budget-friendly (Free)")
             
        # 3. Match on Duration
        if row['duration_bucket'] == profile.get('duration_bucket'):
            reasons.append(f"fits your {row['duration_bucket']} time availability")

        # 4. Sentiment Boost
        if row.get('sentiment_score', 0) > 0.8:
            reasons.append("has highly positive visitor sentiment")

        if not reasons:
            return "Recommended based on overall similarity."
            
        return "This place " + ", ".join(reasons) + "."

    def filter_by_constraints(self, df, profile):
        """
        Applies business rules and hard filters.
        """
        filtered_df = df.copy()
        
        # --- Constraint 1: Job Type (Time Flexibility) ---
        # If Job Type is 'Fixed Schedule', strictly enforce Duration bucket.
        # (e.g., Someone with a 9-5 job likely wants Weekend/Short trips, not Long expeditions)
        job_type = profile.get('job_type', 'Flexible') # Default to Flexible
        if job_type == 'Fixed Schedule':
            # Strict logic: If user selected 'Short' or 'Medium', do NOT show 'Long'
            # Or simpler: Enforce their duration pref exactly.
            desired_duration = profile.get('duration_bucket')
            if desired_duration:
                # We allow slight flexibility (e.g. asking for Short can show Short + Medium),
                # but let's be strict for demonstration.
                 filtered_df = filtered_df[filtered_df['duration_bucket'] == desired_duration]

        # --- Constraint 2: Budget Strictness ---
        # If user says 'Low', remove 'High'. If 'High', show everything.
        budget_pref = profile.get('budget_bucket')
        if budget_pref == 'Low':
            # Remove 'High' cost places
            filtered_df = filtered_df[filtered_df['budget_bucket'] != 'High']
        elif budget_pref == 'Free':
             filtered_df = filtered_df[filtered_df['budget_bucket'] == 'Free']

        # --- Constraint 3: Weekly Off (Availability) ---
        # If user plans to visit on a specific day, ensure place is open.
        # Defaults to None (Any Day)
        visit_day = profile.get('visit_day') 
        if visit_day:
            # Data format in DB for weekly_off: "Monday" or null.
            # We filter out places where weekly_off == visit_day
            # Note: We need to handle NaN logic
            filtered_df = filtered_df[filtered_df['weekly_off'] != visit_day]

        return filtered_df

if __name__ == "__main__":
    # Test Run
    recommender = TravelRecommender()
    
    # Test User (Nature Lover, Short Trip, Low Budget, Fixed Job)
    test_user = {
        'type': 'Nature', 
        'significance': 'Nature',
        'duration_bucket': 'Short',
        'budget_bucket': 'Low', 
        'zone': 'Southern',
        'job_type': 'Fixed Schedule', # <--- NEW CONSTRAINT
        'visit_day': 'Monday'         # <--- NEW CONSTRAINT
    }
    
    print("--- User Profile ---")
    print(test_user)
    
    recs = recommender.recommend(test_user, top_n=5)
    
    print("\n--- Top 5 Recommendations (Filtered & Explained) ---")
    # Display full Explanation string
    pd.set_option('display.max_colwidth', None)
    print(recs[['name', 'match_score', 'explanation']])
