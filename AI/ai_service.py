import json
import google.generativeai as genai

# --- CONFIGURATION ---
# Paste your key inside the quotes
API_KEY = "AIzaSyBglrChYLdRbCzbj1mQ6w0sQ5izLBya18Y"

class LibraryAI:
    def __init__(self):
        genai.configure(api_key=API_KEY)
        
        # USE THIS MODEL - It is the standard free-tier version
        self.model = genai.GenerativeModel('gemini-flash-latest')
        
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
        print(f"✨ Asking Gemini: '{user_text}'...")

        try:
            # --- THE "SIMPLE" PROMPT ---
            # We explicitly tell it to be short and dumb it down.
            prompt = f"""
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

            response = self.model.generate_content(prompt)
            
            # Clean up response
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_text)

            # --- NEW: PRINT THE ANSWER TO TERMINAL ---
            print(f"🤖 GEMINI ANSWER: {result['reason']}") 
            print(f"📚 RECOMMENDED: {result['id']}")
            
            # Get full book details
            full_book = self._get_book_by_id(result['id'])
            full_book['reason'] = result['reason']
            full_book['confidence'] = "AI Match"
            
            return [full_book]

        except Exception as e:
            # If we hit a rate limit (429) again, fallback gracefully
            print(f"❌ Error: {e}")
            return self._get_fallback()

    def _get_book_by_id(self, target_id):
        for book in self.catalog:
            if book['id'] == target_id: return book
        return self.catalog[0]

    def _get_fallback(self):
        return [{
            "title": "Sapiens", 
            "desc": "History of humankind.", 
            "reason": "AI is busy, but this is a classic.", 
            "confidence": "Offline"
        }]

if __name__ == "__main__":
    ai = LibraryAI()
    print(ai.get_recommendations("I need to study for IoT")[0]['reason'])