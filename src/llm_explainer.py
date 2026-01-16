import requests
import json
import logging
from src.config import GEMINI_API_KEY, GEMINI_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TravelLLMExplainer:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model = GEMINI_MODEL
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def generate_detailed_explanation(self, destination, user_profile):
        """
        Generates a personalized explanation using Gemini API.
        
        Args:
            destination (dict): Destination details (name, reviews, type, etc.)
            user_profile (dict): User preferences.
            
        Returns:
            str: Generated text or fallback message.
        """
        
        # Construct the prompt
        prompt = f"""
        You are a smart travel assistant. 
        
        I will give you a User Profile and a Destination.
        Your goal is to write a short, persuasive, and personalized paragraph (approx 50-80 words) describing why this destination is a great match for this specific user.
        
        Use the 'Sample Reviews' to mention specific highlights or warnings that relevant to the user's interests.
        Do NOT mention that you are an AI. Sound like a knowledgeable local guide.
        
        --- User Profile ---
        Interest: {user_profile.get('type')}
        Travel Style: {user_profile.get('significance', 'General')}
        Budget: {user_profile.get('budget_bucket')}
        Available Time: {user_profile.get('duration_bucket')}
        
        --- Destination ---
        Name: {destination.get('name')}
        Type: {destination.get('type')}
        Highlights: {destination.get('significance')}
        Google Rating: {destination.get('google_rating')}
        Sample Reviews: "{destination.get('sample_reviews', '')[:500]}"
        
        --- Output ---
        """
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()
                # Extract text from Gemini response structure
                try:
                    explanation = result['candidates'][0]['content']['parts'][0]['text']
                    return explanation.strip()
                except (KeyError, IndexError) as e:
                    logger.error(f"Error parsing Gemini response: {e}")
                    return "Could not generate explanation due to unexpected response format."
            else:
                logger.error(f"API Error {response.status_code}: {response.text}")
                return "Service temporarily unavailable."
                
        except Exception as e:
            logger.error(f"Exception calling Gemini API: {e}")
            return "Could not connect to explanation service."

if __name__ == "__main__":
    # Test Block
    explainer = TravelLLMExplainer()
    
    # Dummy Data
    user = {
        'type': 'Nature',
        'significance': 'Relaxation',
        'budget_bucket': 'Low',
        'duration_bucket': 'Short'
    }
    
    dest = {
        'name': 'Munnar Tea Gardens',
        'type': 'Scenic Area',
        'significance': 'Nature',
        'google_rating': 4.8,
        'sample_reviews': "Amazing sunrise. Very crowded on weekends. Best tea tasting experience. Roads are curvy."
    }
    
    print("Testing Gemini API...")
    explanation = explainer.generate_detailed_explanation(dest, user)
    print("\n--- Generated Explanation ---")
    print(explanation)
