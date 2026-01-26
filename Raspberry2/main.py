import json
import paho.mqtt.client as mqtt
import sys
import os

# 1. SETUP PATHS
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import config
from controller import LibraryController
import init_db

# 2. AUTO-INIT DB
if not os.path.exists(config.DB_PATH):
    print("Initializing Database...")
    init_db.setup_db()

# 3. INIT CONTROLLER
ctrl = LibraryController()

# 4. MQTT LOGIC
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"RECEIVED: {payload}")
        
        action = payload.get("action")
        response = None
        
        # Callback for async AI responses
        def async_reply(data):
            print(f"ASYNC: {data}")
            client.publish(config.TOPIC_DISPLAY, json.dumps(data))

        # ROUTING
        if action == "scan":
            response = ctrl.handle_scan(payload, async_reply)
        elif action == "borrow":
            response = ctrl.handle_borrow(payload)
        elif action == "return":
            response = ctrl.handle_return(payload)
        elif action == "get_logs":
            response = ctrl.handle_logs()
        elif action == "chat":
            ctrl.handle_chat(payload, async_reply) 
        elif action == "logout":
            if payload.get("user") in ctrl.active_sessions:
                del ctrl.active_sessions[payload.get("user")]
                print("Logged out")

        # IMMEDIATE RESPONSE
        if response:
            # Create a copy strictly for printing to avoid console flood
            print_data = response.copy()
            
            if print_data.get("type") == "log_data":
                count = len(print_data.get("logs", []))
                print_data["logs"] = f"<Hiding {count} log entries for console clarity>"

            print(f"SENDING: {print_data}")
            client.publish(config.TOPIC_DISPLAY, json.dumps(response))

    except Exception as e:
        print(f"ERROR: {e}")

# 5. START SERVER
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
client.subscribe(config.TOPIC_SCAN)

print(f"SERVER LISTENING ON: {config.TOPIC_SCAN}")
client.loop_forever()