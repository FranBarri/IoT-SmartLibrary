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

book_rfid_map = {
    "901": "B001", # Scanning card 901 = Dune
    "902": "B002",
    "903": "B003",
    "904": "B004",
    "905": "B005",
    "906": "B006", # The Martian
    "907": "B007",
    "908": "B008",
    "909": "B009"
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
            scanned_rfid = payload.get("rfid_id") # The card they just scanned
            
            # 1. Convert Physical Card ID to Book ID
            book_id = book_rfid_map.get(scanned_rfid)
            
            if book_id:
                # Success: We found the book
                # In a real app, check if book is already borrowed here
                status_msg = f"Successfully {action}ed book: {book_id}"
                msg_type = "action_confirm"
            else:
                # Failure: They scanned a random card or a user card
                status_msg = f"Error: Scanned card {scanned_rfid} is not a valid book."
                msg_type = "error"

            print(f"[ACTION] {username} tried to {action} card {scanned_rfid} -> Result: {status_msg}")
            
            response = {
                "status": "success" if book_id else "error",
                "type": msg_type,
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