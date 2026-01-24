import os
import requests
from dotenv import load_dotenv

# Load your API Key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ Error: API Key not found in .env")
    exit()

# Ask Google for the list of available models
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
response = requests.get(url)

if response.status_code == 200:
    print("\n✅ AVAILABLE MODELS FOR YOUR KEY:")
    data = response.json()
    for model in data.get('models', []):
        # Only show models that can generate text
        if "generateContent" in model.get('supportedGenerationMethods', []):
            # Print the clean name (removing "models/" prefix)
            clean_name = model['name'].replace("models/", "")
            print(f"  👉 {clean_name}")
else:
    print(f"❌ Connection Error: {response.text}")