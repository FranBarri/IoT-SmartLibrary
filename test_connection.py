import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ SUCCESS: Connected to Mosquitto!")
    else:
        print(f"❌ ERROR: Connection code {rc}")

client = mqtt.Client()
client.on_connect = on_connect

print("Attempting to connect...")
try:
    # "localhost" means "this computer"
    client.connect("localhost", 1883, 60)
    client.loop_start()
    input("Press Enter to Exit...\n")
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    print("Make sure the black Mosquitto window is open!")