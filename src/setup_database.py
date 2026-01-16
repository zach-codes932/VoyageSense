
import sqlite3
import pandas as pd
import os
import json

# Configuration
DB_PATH = r"D:\Travel RS\data\travel.db"
CSV_PATH = r"D:\Travel RS\data\processed\destinations_with_sentiment.csv"

def init_db():
    print(f"Initializing database at {DB_PATH}...")
    
    # Remove old DB if exists to ensure clean slate (optional, but good for dev)
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Removed existing database.")
        except Exception as e:
            print(f"Warning: Could not remove existing DB: {e}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create Users Table
    # Stores user profile settings matching UI design
    print("Creating 'users' table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            activity_type_pref TEXT,   -- e.g., Nature, Heritage
            travel_interest_pref TEXT, -- e.g., Relaxation, Exploration
            duration_pref TEXT,        -- e.g., Short, Medium
            budget_pref TEXT,          -- e.g., Low, High
            location_zone_pref TEXT,   -- e.g., Northern, Southern
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Create Destinations Table
    # Stores the processed destination features
    print("Creating 'destinations' table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            zone TEXT,
            state TEXT,
            city TEXT,
            type TEXT,
            significance TEXT,
            time_needed_hrs REAL,
            duration_bucket TEXT,
            entrance_fee REAL,
            budget_bucket TEXT,
            google_rating REAL,
            sentiment_score REAL,
            review_count INTEGER,
            sample_reviews TEXT,
            best_time_to_visit TEXT,
            weekly_off TEXT
        )
    ''')

    # 3. Create Interactions/Logs Table
    # Stores basic history of what was recommended or clicked
    print("Creating 'interactions' table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            destination_id INTEGER,
            action_type TEXT, -- e.g., 'recommended', 'viewed', 'liked'
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(destination_id) REFERENCES destinations(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database schema created successfully.")

def populate_destinations():
    print(f"Loading data from {CSV_PATH}...")
    if not os.path.exists(CSV_PATH):
        print("Error: Processed CSV not found.")
        return

    df = pd.read_csv(CSV_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert data row by row (or use to_sql)
    # Mapping CSV columns to DB Schema
    # CSV Cols: zone,state,city,name,type,time_needed_to_visit_in_hrs,google_review_rating,
    # entrance_fee_in_inr,airport_with_50km_radius,weekly_off,significance,dslr_allowed,
    # number_of_google_review_in_lakhs,best_time_to_visit,time_needed_hrs,duration_bucket,
    # entrance_fee,budget_bucket,sentiment_score,review_count,sample_reviews

    count = 0
    for _, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT INTO destinations (
                    name, zone, state, city, type, significance, 
                    time_needed_hrs, duration_bucket, 
                    entrance_fee, budget_bucket, 
                    google_rating, sentiment_score, review_count, 
                    sample_reviews, best_time_to_visit, weekly_off
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['name'], row['zone'], row['state'], row['city'], row['type'], row['significance'],
                row['time_needed_hrs'], row['duration_bucket'],
                row['entrance_fee'], row['budget_bucket'],
                row['google_review_rating'], row['sentiment_score'], row['review_count'],
                row['sample_reviews'], row['best_time_to_visit'], row['weekly_off']
            ))
            count += 1
        except Exception as e:
            print(f"Error inserting row {row['name']}: {e}")

    conn.commit()
    conn.close()
    print(f"Successfully inserted {count} destinations.")

def create_dummy_user():
    # Insert a dummy profile for testing
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating dummy user (Student Profile)...")
    cursor.execute('''
        INSERT INTO users (username, activity_type_pref, travel_interest_pref, duration_pref, budget_pref, location_zone_pref)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('TestUser_Student', 'Nature', 'Exploration', 'Short', 'Low', 'Northern'))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    populate_destinations()
    create_dummy_user()
