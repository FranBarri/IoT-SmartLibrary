import json
import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import config

class LibraryAI:
    def __init__(self, db_conn):
        self.db = db_conn
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={config.GEMINI_KEY}"

    def get_dynamic_catalog(self):
        """Fetches real books from SQLite to give context to the AI"""
        try:
            rows = self.db.execute("SELECT book_id, title, description FROM books").fetchall()
            catalog = [{"id": r["book_id"], "title": r["title"], "desc": r["description"]} for r in rows]
            return json.dumps(catalog)
        except Exception:
            return "[]"

    def get_recommendations(self, user_text):
        catalog_str = self.get_dynamic_catalog()
        print(f"Asking Gemini about: '{user_text}'...")

        try:
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"""
                        You are a Library System.
                        REAL CATALOG: {catalog_str}
                        USER INPUT: "{user_text}"
                        
                        TASK:
                        1. Pick the ONE best book ID from the catalog.
                        2. Write a reason (max 10 words).
                        3. Return strictly valid JSON.
                        
                        JSON FORMAT: {{ "id": "...", "reason": "..." }}
                        """
                    }]
                }]
            }

            response = requests.post(self.api_url, json=payload, headers={'Content-Type': 'application/json'})
            
            if response.status_code != 200:
                return self._get_fallback()

            # Parse (Simplistic parsing for brevity)
            raw = response.json()['candidates'][0]['content']['parts'][0]['text']
            clean = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean)
            
            # Fetch full details from DB to ensure accuracy
            book = self.db.execute("SELECT * FROM books WHERE book_id=?", (result['id'],)).fetchone()
            if book:
                return [{
                    "id": book["book_id"],
                    "title": book["title"],
                    "desc": book["description"],
                    "reason": result["reason"]
                }]
            return self._get_fallback()

        except Exception as e:
            print(f"AI Error: {e}")
            return self._get_fallback()

    def _get_fallback(self):
        return [{"title": "System Offline", "desc": "Check API Key", "reason": "AI unavailable."}]