# 📚 Smart Library System (IoT Project)

A Smart Library simulation built with **IoT and MQTT**, using two Raspberry Pis that communicate in real time.

---

## 🧠 System Architecture

- **Raspberry Pi 1 (Client)**
  - Touchscreen / HDMI display
  - RFID Scanner (RC522)
  - Graphical User Interface

- **Raspberry Pi 2 (Server)**
  - MQTT Broker (Mosquitto)
  - Database & AI processing (Gemini API)
  - Central message handler

Both devices communicate via **MQTT** over the same network.

---

## 🛠 Hardware Prerequisites

### Raspberry Pi 1 (Client)
- Raspberry Pi (any model with GPIO)
- Touchscreen or HDMI Monitor
- **RFID-RC522 Module**
  - Wiring:
    - SDA → GPIO 24
    - SCK → GPIO 23
    - MOSI → GPIO 19
    - MISO → GPIO 21
    - RST → GPIO 22
    - GND → GND
    - 3.3V → 3.3V

### Raspberry Pi 2 (Server)
- Raspberry Pi with internet access (required for Gemini AI API)

### Network
- Both Pis must be on the **same Wi-Fi network**
- 💡 *Tip:* University Wi-Fi may isolate devices — use a mobile hotspot if needed

---

## 🚀 Phase 1: Common Setup (Both Pis)

### 1️⃣ Copy Project Files
Place the project in:
```
/home/pi/SmartLibrary
```
on **both** Raspberry Pis.

### 2️⃣ Install Python Dependencies
```bash
sudo apt update
sudo apt install python3-pip
pip3 install paho-mqtt requests python-dotenv
```

---

## 🖥 Phase 2: Server Setup (Raspberry Pi 2)

The server acts as the **MQTT broker and processing unit**.

### 1️⃣ Install Mosquitto MQTT Broker
```bash
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

### 2️⃣ Configure Environment Variables
Create a `.env` file:
```bash
nano /home/pi/SmartLibrary/raspberry2/.env
```

Paste the following (replace with your real API key):
```ini
GEMINI_API_KEY=AIzaSy...YourActualKey...
MQTT_BROKER=localhost
MQTT_PORT=1883
```

Save with **Ctrl+O**, press **Enter**, then **Ctrl+X**.

### 3️⃣ Get Server IP Address
```bash
hostname -I
```
Example:
```
192.168.1.50
```
📌 You will need this IP for the Client setup.

---

## 📟 Phase 3: Client Setup (Raspberry Pi 1)

The client handles the **UI and RFID scanning**.

### 1️⃣ Enable SPI Interface
```bash
sudo raspi-config
```
Navigate to:
```
3 Interface Options → I4 SPI → Enable
```
Reboot if prompted.

### 2️⃣ Install Hardware Libraries
```bash
pip3 install mfrc522 spidev RPi.GPIO
```

### 3️⃣ Configure Environment Variables
Create a `.env` file:
```bash
nano /home/pi/SmartLibrary/raspberry1/.env
```

Paste the following (use the **Server IP** from Phase 2):
```ini
MQTT_BROKER=192.168.1.50
MQTT_PORT=1883
```

---

## 🏁 Phase 4: Launch Sequence

⚠️ **Always start the Server first**

### ▶️ Step 1: Start Server (Pi 2)
```bash
cd /home/pi/SmartLibrary/raspberry2
python3 main.py
```

✅ Success message:
```
SERVER LISTENING ON: library/scan
```

---

### ▶️ Step 2: Start Client (Pi 1)
If running via SSH, export the display:
```bash
cd /home/pi/SmartLibrary/raspberry1
export DISPLAY=:0
python3 main.py
```

The GUI should appear on the connected screen.

---

## ✅ Project Status
- MQTT communication established
- RFID scanning functional
- Client–Server architecture working
- AI integration via Gemini API

---

## 📌 Notes
- Ensure both Pis remain on the same network
- Do not expose your `.env` files publicly
- Use Python 3.x only

---

## 📄 License
This project is for educational purposes.
