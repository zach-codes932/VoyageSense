import requests
from src.config import GEMINI_API_KEY

def list_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print("Available Models:")
        for m in models:
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                print(f"- {m['name']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    list_models()
