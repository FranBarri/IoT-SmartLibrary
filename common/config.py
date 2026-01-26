import os
from dotenv import load_dotenv

# Load .env from the current working directory or parent
load_dotenv()

# --- NETWORK CONFIG ---
# If running on the same Pi, use "localhost". 
# If separate, use the Server's IP (e.g., "192.168.1.X")
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

# --- TOPICS ---
TOPIC_SCAN = "library/scan"       # Client -> Server
TOPIC_DISPLAY = "library/display" # Server -> Client

# --- DATABASE ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "raspberry2", "library.db")

# --- API KEYS ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")