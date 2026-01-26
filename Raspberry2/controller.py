import json
import threading
import database
from ai_service import LibraryAI

class LibraryController:
    def __init__(self):
        self.db = database.db_connect()
        self.ai = LibraryAI(self.db)
        self.active_sessions = {}

    def handle_scan(self, payload, publish_callback):
        """
        Handles card scans.
        publish_callback: A function to send data back to MQTT (used for AI threading)
        """
        scanned_id = payload.get("id")
        result = database.scan_id(self.db, scanned_id)
        
        if result.get("status") == "error":
            return {"status": "error", "message": result.get("message")}

        # 1. LOGIN LOGIC
        if result["type"] == "login":
            user_name = result["user"]
            self.active_sessions[user_name] = result["user_id"]
            database.log_action(self.db, result["user_id"], "login")
            
            # Start AI Recommendation in Background Thread (Don't block login!)
            def bg_recommend():
                rec = self.ai.get_recommendations(f"Recommend a book about {result['interest']}")[0]
                # Send a second update with the book
                publish_callback({
                    "type": "chat_response", # Or a specific 'rec_update' type
                    "user": user_name,
                    "book": rec
                })
            threading.Thread(target=bg_recommend).start()

            return {
                "type": "login",
                "user": user_name,
                "role": result["role"],
                "book": {"title": "Loading...", "desc": "AI is thinking...", "reason": "..."} 
            }

        # 2. BOOK LOGIC
        elif result["type"] == "book_scan":
            # Log view if someone is logged in
            user = payload.get("user")
            user_id = self.active_sessions.get(user)
            if user_id:
                database.log_action(self.db, user_id, "viewed_book", result["id"])

            return {
                "type": "chat_response",
                "user": user,
                "book": {"id": result["id"], "title": result["title"], "desc": result["desc"], "reason": "Scanned Book"}
            }

    def handle_borrow(self, payload):
        user = payload.get("user")
        user_id = self.active_sessions.get(user)
        if not user_id: return {"status": "error", "message": "Session Expired"}
        return database.borrow_book(self.db, user_id, payload.get("book_id"))

    def handle_return(self, payload):
        user = payload.get("user")
        user_id = self.active_sessions.get(user)
        if not user_id: return {"status": "error", "message": "Session Expired"}
        return database.return_book(self.db, user_id, payload.get("book_id"))

    def handle_logs(self):
        return {"type": "log_data", "logs": database.get_logs(self.db)}

    def handle_chat(self, payload, publish_callback):
        """Runs AI Chat in a background thread"""
        def task():
            recs = self.ai.get_recommendations(payload.get("text"))
            response = {
                "type": "chat_response",
                "user": payload.get("user"),
                "book": recs[0]
            }
            publish_callback(response)
        
        threading.Thread(target=task).start()
        return None # No immediate response, it comes later via callback