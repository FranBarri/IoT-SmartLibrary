import tkinter as tk
from tkinter import ttk, messagebox
import json
import paho.mqtt.client as mqtt

# IMPORT YOUR MODULES
from hardware import RFIDReader
from ui_views import LoginView, DashboardView, AdminView

# --- CONFIG ---
BROKER = "localhost" 
TOPIC_SEND = "library/scan"
TOPIC_LISTEN = "library/display"

class SmartLibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Library Terminal")
        
        # 1. REMOVE FIXED GEOMETRY
        # self.geometry("1000x700") <--- DELETE THIS LINE

        # STATE
        self.current_user = ""
        self.current_book_id = ""

        # 2. INIT UI
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.frames = {}

        for F in (LoginView, DashboardView, AdminView):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            # Use grid to stack frames
            frame.grid(row=0, column=0, sticky="nsew")

        # Configure the container to expand with the window
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_frame("LoginView")

        # 3. INIT HARDWARE & MQTT (Same as before)
        self.rfid = RFIDReader(callback_function=self.handle_rfid_scan)
        self.rfid.start()

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_message = self.on_mqtt_message
        self.client.connect(BROKER, 1883, 60)
        self.client.subscribe(TOPIC_LISTEN)
        self.client.loop_start()

        # 4. AUTO-SIZE & CENTER THE WINDOW
        self.center_window()

    def center_window(self):
        """
        Calculates the required size for the content and centers 
        the window on the screen.
        """
        self.update_idletasks() # Force Tkinter to calculate widget sizes
        
        # Get the required width/height based on the widgets
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate x and y coordinates to center the window
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Apply the geometry
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Optional: Set a minimum size so it doesn't get too small
        self.minsize(width, height)
        
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    # --- LOGIC ACTIONS ---
    def handle_rfid_scan(self, card_id):
        print(f"DEBUG: Scanned {card_id}")
        # Send raw scan to server. Server decides if it's login or borrow.
        self.publish({"action": "scan", "id": card_id})

    def simulate_scan(self, card_id):
        # Called by buttons on LoginView
        self.handle_rfid_scan(card_id)

    def send_chat(self, text):
        self.frames["DashboardView"].add_chat_msg("👤 You", text, "user_msg")
        self.publish({"action": "chat", "user": self.current_user, "text": text})

    def send_action(self, action_type):
        if not self.current_book_id:
            messagebox.showwarning("Warning", "No book selected!")
            return
        self.publish({"action": action_type, "user": self.current_user, "book_id": self.current_book_id})

    def logout(self):
        self.current_user = ""
        self.current_book_id = ""
        self.show_frame("LoginView")

    def publish(self, msg_dict):
        self.client.publish(TOPIC_SEND, json.dumps(msg_dict))

    # --- MQTT RESPONSE HANDLING ---
    def on_mqtt_message(self, client, userdata, msg):
        payload = json.loads(msg.payload.decode())
        # Run UI updates on main thread
        self.after(0, lambda: self.process_server_response(payload))

    def process_server_response(self, data):
        if data.get('status') == 'error':
            messagebox.showerror("Error", data['message'])
            return

        if data.get('type') == 'action_confirm':
            messagebox.showinfo("Success", data['message'])
            return

        if data['type'] in ['login', 'chat_response']:
            self.current_user = data['user']
            book = data['book']
            self.current_book_id = book['id']

            # Update Dashboard
            dash = self.frames["DashboardView"]
            dash.update_book(book)
            
            if data['type'] == 'chat_response':
                dash.add_chat_msg("🤖 AI", book.get('reason', ''), "ai_msg")
            
            if data['type'] == 'login':
                dash.update_user(self.current_user)
                if data.get('role') == 'admin':
                    self.show_frame("AdminView")
                else:
                    self.show_frame("DashboardView")

if __name__ == "__main__":
    app = SmartLibraryApp()
    app.mainloop()