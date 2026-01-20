import paho.mqtt.client as mqtt
import json
import time
from ai_service import LibraryAI 

# --- CONFIGURATION ---
BROKER = "localhost"
TOPIC_SCAN = "library/scan"
TOPIC_DISPLAY = "library/display"

# --- INITIALIZE AI ---
print("⏳ Initializing AI...")
ai = LibraryAI()
# NOTE: ai.train() is REMOVED because the new brain doesn't need it!

# --- FAKE DATABASE ---
users_db = {
    "123": {"name": "Alice", "role": "client", "dept": "Engineering", "interest": "SciFi"},
    "456": {"name": "Bob", "role": "client", "dept": "Arts", "interest": "History"},
    "999": {"name": "Admin", "role": "admin", "dept": "Staff", "interest": "Tech"}
}

# --- MQTT FUNCTIONS ---
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"✅ SERVER ONLINE. Connected to {BROKER}")
    client.subscribe(TOPIC_SCAN)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        action = payload.get("action")
        
        # --- 1. LOGIN / SCAN ---
        if action == "scan":
            card_id = payload.get("id")
            user = users_db.get(card_id)
            
            if user:
                print(f"[LOGIN] {user['name']} found.")
                
                # NEW LOGIC: Create a "Prompt" for the NLP AI
                # Instead of sending numbers, we send a sentence describing the user
                user_persona = f"{user['interest']} books for {user['dept']} students"
                recs = ai.get_recommendations(user_persona)
                
                response = {
                    "status": "success",
                    "type": "login",
                    "user": user['name'],
                    "role": user['role'],
                    "book": recs[0] # Send the best match
                }
            else:
                response = {"status": "error", "message": "Unknown User"}

            client.publish(TOPIC_DISPLAY, json.dumps(response))

        # --- 2. CHAT REQUEST ---
        elif action == "chat":
            user_text = payload.get("text")
            username = payload.get("user")
            
            print(f"[CHAT] {username} asked: '{user_text}'")
            
            # Ask the AI directly with the user's text
            recs = ai.get_recommendations(user_text)
            
            response = {
                "status": "success",
                "type": "chat_response",
                "user": username,
                "book": recs[0]
            }
            client.publish(TOPIC_DISPLAY, json.dumps(response))
            
        # --- 3. BORROW / RETURN ACTIONS ---
        elif action in ["borrow", "return"]:
            username = payload.get("user")
            book_id = payload.get("book_id")
            
            # In a real app, you would update the SQL database here.
            # For now, we just acknowledge it.
            status_msg = "Borrowed successfully! Due in 7 days." if action == "borrow" else "Returned. Thank you!"
            
            print(f"[ACTION] {username} performed {action} on {book_id}")
            
            response = {
                "status": "success",
                "type": "action_confirm",
                "action": action,
                "message": status_msg
            }
            client.publish(TOPIC_DISPLAY, json.dumps(response))

    except Exception as e:
        print(f"❌ ERROR: {e}")

# --- START SERVER ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, 1883, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("Server Stopped.")