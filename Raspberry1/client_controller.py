import json
import paho.mqtt.client as mqtt
import sys
import os

# Import Common Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import config

class ClientController:
    def __init__(self, app):
        self.app = app
        self.current_user = ""
        self.current_role = "client"
        self.pending_action = None

        # --- MQTT SETUP ---
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_message = self.on_mqtt_message
        self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        self.client.subscribe(config.TOPIC_DISPLAY)
        self.client.loop_start()

    # --- ACTIONS (Called by UI) ---
    def handle_scan(self, card_id):
        """Main Logic for any scan (Real or Simulated)"""
        print(f"DEBUG: Scanned {card_id}")
        
        # 1. Close Popup if open
        self.app.close_popup()

        # 2. Logic
        if self.pending_action:
            self.publish({
                "action": self.pending_action,
                "user": self.current_user,
                "book_id": card_id 
            })
            self.pending_action = None
        else:
            self.publish({"action": "scan", "id": card_id})

    def simulate_scan(self, card_id):
        """Alias for UI buttons to call handle_scan"""
        self.handle_scan(card_id)

    def prepare_action(self, action_type):
        """Called when user clicks Borrow or Return button"""
        self.pending_action = action_type
        self.app.show_scan_popup(action_type)

    def cancel_action(self):
        self.pending_action = None
        self.app.close_popup()

    def send_chat(self, text):
        self.app.add_chat_message("You", text, "user_msg")
        self.publish({"action": "chat", "user": self.current_user, "text": text})

    def logout(self):
        if self.current_user:
            self.publish({"action": "logout", "user": self.current_user})
        
        self.current_user = ""
        self.current_role = "client"
        self.app.reset_ui() 

    def request_logs(self):
        self.publish({"action": "get_logs"})

    def publish(self, payload):
        self.client.publish(config.TOPIC_SCAN, json.dumps(payload))

    # --- MQTT HANDLING ---
    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            self.app.after(0, lambda: self.process_response(payload))
        except Exception as e:
            print(f"MQTT Error: {e}")

    def process_response(self, data):
        msg_type = data.get('type')

        if data.get('status') == 'error':
            self.app.show_error(data['message'])
            return

        if msg_type == 'action_confirm':
            self.app.show_success(data['message'])

        elif msg_type == 'log_data':
            self.app.update_logs(data['logs'])

        elif msg_type == 'login':
            self.current_user = data['user']
            self.current_role = data.get('role', 'client')
            self.app.login_success(self.current_user, self.current_role)
            self.app.update_book_info(data['book'])
            
            if self.current_role == "admin":
                self.request_logs()

        elif msg_type == 'chat_response':
            self.app.update_book_info(data['book'])
            self.app.add_chat_message("AI", data['book'].get('reason', ''), "ai_msg")