# 📚 Smart Library IoT Project (AI & UI Simulation)

This repository contains the code for the **Smart Library Kiosk**. It simulates the interaction between the Raspberry Pi Kiosk (UI), the Central Server (Brain), and the Cloud AI (Gemini).

## 🛠️ Prerequisites (What you need installed)

Before running the code, make sure you have these installed on your laptop:

1.  **Python 3.12** (or newer)
2.  **Mosquitto MQTT Broker** (Must be running in the background)
3.  **Python Libraries:**
    Run this command in your terminal to install the necessary packages:
    ```bash
    pip install paho-mqtt google-generativeai
    ```

## 🚀 How to Run the Simulation

Open the main **"IoT Project"** folder in VS Code (or your terminal).
You need to run the **Server** (Brain) and the **Client** (Kiosk) in two separate terminals.

### Step 1: Start the MQTT Broker
Make sure Mosquitto is running.
* **Windows:** It usually runs automatically. Test it by typing: `netstat -an | find "1883"`
* **Mac/Linux:** Run `mosquitto` in a terminal.

### Step 2: Run the Server (Terminal 1)
This script listens for scans and talks to the AI.
```bash
python AI/server_main.py
```

### Step 3: Run the UI (Terminal 2)
This script opens the Kiosk window with the buttons and chat.
```bash
python UI/client_ui.py
```
