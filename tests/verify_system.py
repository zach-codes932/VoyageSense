
import os
import sys
import sqlite3
import pandas as pd
import logging
from termcolor import colored

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from src.recommender import TravelRecommender
from src.llm_explainer import TravelLLMExplainer
from src.youtube_manager import YouTubeVlogManager
from src.config import GEMINI_API_KEY, YOUTUBE_API_KEY

logging.basicConfig(level=logging.ERROR)

def check_db():
    print(colored("\n[1] Checking Database...", "blue"))
    db_path = os.path.join(PROJECT_ROOT, "data", "travel.db")
    if not os.path.exists(db_path):
        print(colored(f"FAIL: Database not found at {db_path}", "red"))
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check destinations count
        cursor.execute("SELECT COUNT(*) FROM destinations")
        dest_count = cursor.fetchone()[0]
        
        # Check users count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        conn.close()
        
        if dest_count > 0:
            print(colored(f"PASS: Database active. Found {dest_count} destinations and {user_count} users.", "green"))
            return True
        else:
            print(colored("FAIL: Destinations table is empty.", "red"))
            return False
            
    except Exception as e:
        print(colored(f"FAIL: DB Error: {e}", "red"))
        return False

def check_recommender():
    print(colored("\n[2] Checking Recommender System...", "blue"))
    try:
        rec = TravelRecommender()
        
        # Test Profile: Nature Lover
        profile = {
            'type': 'Nature',
            'significance': 'Relaxation',
            'duration_bucket': 'Short',
            'budget_bucket': 'Low',
            'zone': 'Southern',
            'job_type': 'Flexible'
        }
        
        print("   Test Profile: Nature | Low Budget | Southern")
        results = rec.recommend(profile, top_n=3)
        
        if results.empty:
            print(colored("FAIL: No recommendations returned.", "red"))
            return False
            
        top_name = results.iloc[0]['name']
        score = results.iloc[0]['match_score']
        
        print(colored(f"PASS: Recommendation successful. Top Result: {top_name} (Score: {score:.2f})", "green"))
        return True
        
    except Exception as e:
        print(colored(f"FAIL: Recommender Error: {e}", "red"))
        return False

def check_api_keys():
    print(colored("\n[3] Checking API Configurations...", "blue"))
    
    gemini_ok = False
    youtube_ok = False
    
    # Check Gemini
    if GEMINI_API_KEY and "AIza" in GEMINI_API_KEY:
        print(colored("PASS: Gemini API Key detected.", "green"))
        gemini_ok = True
    else:
        print(colored("WARN: Gemini API Key look invalid or missing.", "yellow"))
        
    # Check YouTube
    if YOUTUBE_API_KEY and "AIza" in YOUTUBE_API_KEY:
        print(colored("PASS: YouTube API Key detected.", "green"))
        youtube_ok = True
    else:
        print(colored("WARN: YouTube API Key looks invalid or missing.", "yellow"))
        
    return gemini_ok and youtube_ok

def run_tests():
    print(colored("=== VoyageSense System Verification ===", "cyan", attrs=['bold']))
    
    db_status = check_db()
    rec_status = check_recommender()
    api_status = check_api_keys()
    
    print("\n" + "="*40)
    if db_status and rec_status:
        print(colored("OVERALL STATUS: SYSTEM OPERATIONAL [OK]", "green", attrs=['bold']))
        if not api_status:
            print(colored("Note: Check API Keys for full functionality.", "yellow"))
    else:
        print(colored("OVERALL STATUS: SYSTEM FAILURE [X]", "red", attrs=['bold']))

if __name__ == "__main__":
    run_tests()
