import json
import os
import requests
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ ERROR: API Key not found! Make sure you created the .env file.")

class LibraryAI:
    def __init__(self):
        # We don't need google.generativeai anymore!
        # We just need the URL for the REST API.
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        
        # Simple Database
        self.catalog = [
            {"id": "B001", "title": "Dune", "desc": "Sci-fi politics on desert planet."},
            {"id": "B002", "title": "Guns, Germs, and Steel", "desc": "History of civilization."},
            {"id": "B003", "title": "Fahrenheit 451", "desc": "Future where books are banned."},
            {"id": "B004", "title": "Sapiens", "desc": "History of humankind and biology."},
            {"id": "B005", "title": "Brief Answers to Big Questions", "desc": "Physics and the universe."},
            {"id": "B006", "title": "The Martian", "desc": "Survival on Mars with science."},
            {"id": "B007", "title": "Foundation", "desc": "Math predicts empire fall."},
            {"id": "B008", "title": "The Innovators", "desc": "History of computers and hackers."},
            {"id": "B009", "title": "The IoT Handbook", "desc": "Guide to IoT, sensors, and exams."}
        ]
        self.catalog_str = json.dumps(self.catalog)

    def get_recommendations(self, user_text):
        print(f"✨ Asking Gemini (via HTTP): '{user_text}'...")

        try:
            # --- CONSTRUCT RAW JSON PAYLOAD ---
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"""
                        You are a Library System.
                        DATABASE: {self.catalog_str}
                        USER INPUT: "{user_text}"
                        
                        TASK:
                        1. Pick the ONE best book ID.
                        2. Write a reason that is SHORT (max 10 words) and SIMPLE.
                        3. Return strictly valid JSON.
                        
                        JSON FORMAT:
                        {{
                            "id": "Bxxx",
                            "reason": "Short simple reason here."
                        }}
                        """
                    }]
                }]
            }

            # --- SEND REQUEST ---
            response = requests.post(self.api_url, json=payload, headers={'Content-Type': 'application/json'})
            
            # Check for HTTP errors
            if response.status_code != 200:
                print(f"❌ API Error: {response.text}")
                return self._get_fallback()

            # --- PARSE RESPONSE ---
            data = response.json()
            # Navigate the Google JSON structure to find the text
            raw_text = data['candidates'][0]['content']['parts'][0]['text']
            
            # Clean up Markdown if present
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_text)

            print(f"🤖 GEMINI ANSWER: {result['reason']}") 
            print(f"📚 RECOMMENDED: {result['id']}")
            
            # Get full book details
            full_book = self._get_book_by_id(result['id'])
            full_book['reason'] = result['reason']
            full_book['confidence'] = "AI Match"
            
            return [full_book]

        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return self._get_fallback()

    def _get_book_by_id(self, target_id):
        for book in self.catalog:
            if book['id'] == target_id: return book
        return self.catalog[0]

    def _get_fallback(self):
        return [{
            "title": "Sapiens", 
            "desc": "History of humankind.", 
            "reason": "AI is offline, but this is a classic.", 
            "confidence": "Offline"
        }]

if __name__ == "__main__":
    ai = LibraryAI()
    print(ai.get_recommendations("I need to study for IoT")[0]['reason'])