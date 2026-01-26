import tkinter as tk
from tkinter import messagebox
from ui_views import LoginView, DashboardView, AdminView, ScanPopup
from hardware import RFIDReader
from client_controller import ClientController

class SmartLibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Library Terminal")
        self.scan_popup = None
        
        # 1. INIT CONTROLLER
        # We pass 'self' so the controller can call methods like 'reset_ui'
        self.ctrl = ClientController(self)

        # 2. INIT UI FRAMES
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.frames = {}

        # Pass 'self.ctrl' to views so buttons can call 'ctrl.logout()', etc.
        for F in (LoginView, DashboardView, AdminView):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self.ctrl) 
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.show_frame("LoginView")
        self.center_window()

        # 3. INIT HARDWARE
        # Hardware calls controller directly
        self.rfid = RFIDReader(callback_function=self.ctrl.handle_scan)
        self.rfid.start()

    # --- UI HELPERS (Called by Controller) ---
    def show_frame(self, page_name):
        self.frames[page_name].tkraise()

    def login_success(self, user, role):
        # Update User Label on both views
        self.frames["DashboardView"].update_user(user)
        self.frames["AdminView"].update_user(user)
        
        # Switch View
        if role == "admin":
            self.show_frame("AdminView")
        else:
            self.show_frame("DashboardView")

    def reset_ui(self):
        # Clear Chats
        self.frames["DashboardView"].clear_chat()
        self.frames["AdminView"].clear_chat()
        self.show_frame("LoginView")

    def update_book_info(self, book_data):
        # Update both views just to be safe
        self.frames["DashboardView"].update_book(book_data)
        self.frames["AdminView"].update_book(book_data)

    def add_chat_message(self, sender, text, tag):
        # Add to currently visible view (or both)
        self.frames["DashboardView"].add_chat_msg(sender, text, tag)
        self.frames["AdminView"].add_chat_msg(sender, text, tag)

    def update_logs(self, logs):
        self.frames["AdminView"].update_logs(logs)

    def show_scan_popup(self, action_type):
        # Pass controller to popup so simulation buttons work
        self.scan_popup = ScanPopup(self, action_type, self.ctrl.cancel_action, self.ctrl)

    def close_popup(self):
        if self.scan_popup:
            self.scan_popup.destroy()
            self.scan_popup = None

    def show_error(self, msg):
        messagebox.showerror("Error", msg)

    def show_success(self, msg):
        messagebox.showinfo("Success", msg)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    app = SmartLibraryApp()
    app.mainloop()