import tkinter as tk
from tkinter import ttk, messagebox
import json
import paho.mqtt.client as mqtt

# IMPORT YOUR MODULES
from hardware import RFIDReader
from ui_views import *

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
        self.pending_action_mode = None
        self.scan_popup = None 

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

        if self.scan_popup:
            self.scan_popup.destroy()
            self.scan_popup = None

        if self.pending_action_mode:
            # Send Borrow/Return
            self.publish({
                "action": self.pending_action_mode,
                "user": self.current_user,
                "book_id": card_id 
            })
            self.pending_action_mode = None
        else:
            # Normal Scan
            self.publish({"action": "scan", "id": card_id})

    def simulate_scan(self, card_id):
        # Called by buttons on LoginView
        self.handle_rfid_scan(card_id)

    def prepare_action(self, action_type):
        """Called when user clicks Borrow or Return button"""
        self.pending_action_mode = action_type

        # PASS 'self' AS THE CONTROLLER
        self.scan_popup = ScanPopup(self, action_type, self.cancel_action, self) 

        msg = f"Please SCAN BOOK to {action_type.upper()}..."
        
        # Show message on current view (Background status)
        if self.current_role == "admin":
            self.frames["AdminView"].set_action_status(msg)
        else:
            self.frames["DashboardView"].set_action_status(msg)

    def cancel_action(self):
        """Called if user clicks CANCEL in the popup"""
        self.pending_action_mode = None
        if self.scan_popup:
            self.scan_popup.destroy()
            self.scan_popup = None

    def request_logs(self):
        self.publish({"action": "get_logs"})

    def send_chat(self, text):
        if self.current_role == "admin":
            current_view = self.frames["AdminView"]
        else:
            current_view = self.frames["DashboardView"]

        current_view.add_chat_msg("You", text, "user_msg")
        self.publish({"action": "chat", "user": self.current_user, "text": text})

    def logout(self):
        if self.current_user:
            self.publish({
                "action": "logout", 
                "user": self.current_user
            })

        if "DashboardView" in self.frames:
            self.frames["DashboardView"].clear_chat()

        if "AdminView" in self.frames:
            self.frames["AdminView"].clear_chat()
            
        self.current_user = ""
        self.current_book_id = ""
        self.current_role = "client"
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

        if data.get('type') == 'log_data':
            self.frames["AdminView"].update_logs(data['logs'])
            return

        if data.get('type') == 'action_confirm':
            messagebox.showinfo("Success", data['message'])
            return

        if data['type'] in ['login', 'chat_response']:
            self.current_user = data['user']
            book = data['book']

            if data['type'] == 'login':
                self.current_role = data.get('role', 'client')
                target_view = "AdminView" if self.current_role == "admin" else "DashboardView"
                self.frames[target_view].update_user(self.current_user)
                if self.current_role == "admin":
                    self.request_logs()
                self.show_frame(target_view)
            else:
                target_view = "AdminView" if self.current_role == "admin" else "DashboardView"

            view = self.frames[target_view]
            view.update_book(book)
            
            if data['type'] == 'chat_response':
                view.add_chat_msg("AI", book.get('reason', ''), "ai_msg")

if __name__ == "__main__":
    app = SmartLibraryApp()
    app.mainloop()