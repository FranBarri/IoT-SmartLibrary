import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# --- STYLES & FONTS ---
BG_DARK = "#2C3E50"
BG_LIGHT = "#ECF0F1"
BG_HEADER = "#34495E"
ACCENT_GREEN = "#27AE60"
ACCENT_BLUE = "#2980B9"

class LoginView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        tk.Label(self, text="Smart Library System", font=("Helvetica", 32, "bold"), fg="white", bg=BG_DARK).pack(pady=120)
        tk.Label(self, text="Scan ID to Login", font=("Helvetica", 16), fg="#BDC3C7", bg=BG_DARK).pack()
        
        # Simulation Buttons (Only visible if IS_PI is False, controlled by main app)
        self.sim_frame = tk.Frame(self, bg=BG_DARK)
        self.sim_frame.pack(pady=40)
        
        tk.Button(self.sim_frame, text="[Sim] Alice", command=lambda: controller.simulate_scan("1045542929320"), bg="white", width=15).pack(side="left", padx=5)
        tk.Button(self.sim_frame, text="[Sim] Bob", command=lambda: controller.simulate_scan("152089854730"), bg="white", width=15).pack(side="left", padx=5)

class DashboardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#BDC3C7")
        self.controller = controller
        
        # --- HEADER ---
        header = tk.Frame(self, bg="#34495E", height=60)
        header.pack(fill="x", side="top")
        self.lbl_user = tk.Label(header, text="User: ---", font=("Arial", 14, "bold"), fg="white", bg="#34495E")
        self.lbl_user.pack(side="left", padx=20, pady=15)
        tk.Button(header, text="LOGOUT", command=controller.logout, bg="#C0392B", fg="white", bd=0, padx=15).pack(side="right", padx=20, pady=15)

        # --- MAIN CONTENT ---
        content = tk.Frame(self, bg="#ECF0F1")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. LEFT PANEL (Book Info + SIMULATION)
        left_panel = tk.Frame(content, bg="white", width=400, bd=1, relief="solid")
        left_panel.pack(side="left", fill="y", padx=(0, 20))
        left_panel.pack_propagate(False)

        # ... (Keep Title, Desc, Reason labels same as before) ...
        tk.Label(left_panel, text="CURRENT RECOMMENDATION", font=("Arial", 10, "bold"), fg="gray", bg="white").pack(pady=(30, 10))
        self.lbl_title = tk.Label(left_panel, text="Waiting...", font=("Georgia", 22, "bold"), wraplength=350, bg="white", fg="#2C3E50")
        self.lbl_title.pack(pady=10)
        self.lbl_desc = tk.Label(left_panel, text="Scan a card...", font=("Arial", 12), wraplength=350, justify="left", bg="white", fg="#34495E")
        self.lbl_desc.pack(pady=10, padx=20)
        tk.Frame(left_panel, height=2, bg="#ECF0F1", width=300).pack(pady=20)
        self.lbl_reason = tk.Label(left_panel, text="", font=("Arial", 11, "italic"), wraplength=350, bg="white", fg="#27AE60")
        self.lbl_reason.pack(padx=20)

        # 2. RIGHT PANEL (Tabs)
        right_panel = tk.Frame(content, bg="#ECF0F1")
        right_panel.pack(side="right", fill="both", expand=True)

        self.tabs = ttk.Notebook(right_panel)
        self.tabs.pack(fill="both", expand=True)

        # --- TAB 1: ACTIONS ---
        tab_actions = tk.Frame(self.tabs, bg="white")
        self.tabs.add(tab_actions, text="Actions ")
        
        tk.Label(tab_actions, text="Select an Action & Scan Book", font=("Arial", 14), bg="white").pack(pady=50)
        
        tk.Button(tab_actions, text="BORROW BOOK", command=lambda: controller.prepare_action("borrow"), 
                  bg="#27AE60", fg="white", font=("Arial", 14, "bold"), width=20, height=2).pack(pady=10)
        
        tk.Button(tab_actions, text="RETURN BOOK", command=lambda: controller.prepare_action("return"), 
                  bg="#F39C12", fg="white", font=("Arial", 14, "bold"), width=20, height=2).pack(pady=10)
                
        # Status Label for "Waiting for scan..."
        self.lbl_action_status = tk.Label(tab_actions, text="", font=("Arial", 12, "bold"), fg="#C0392B", bg="white")
        self.lbl_action_status.pack(pady=20)

        # --- TAB 2: CHAT ---
        tab_chat = tk.Frame(self.tabs, bg="#F4F6F7")
        self.tabs.add(tab_chat, text="AI Librarian ")
        
        self.chat_history = scrolledtext.ScrolledText(tab_chat, state='disabled', font=("Arial", 11), padx=10, pady=10)
        self.chat_history.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        self.chat_history.tag_config("user_msg", foreground="#2980B9", font=("Arial", 11, "bold"))
        self.chat_history.tag_config("ai_msg", foreground="#27AE60", font=("Arial", 11, "bold"))
        
        input_frame = tk.Frame(tab_chat, bg="#F4F6F7")
        input_frame.pack(fill="x", padx=10, pady=10)
        self.entry_chat = tk.Entry(input_frame, font=("Arial", 12))
        self.entry_chat.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.btn_ask = tk.Button(input_frame, text="Send", command=self.send_chat, bg="#2980B9", fg="white", width=10)
        self.btn_ask.pack(side="right")

    def send_chat(self):
        text = self.entry_chat.get()
        if text:
            self.controller.send_chat(text)
            self.entry_chat.delete(0, tk.END)

    def update_user(self, name):
        self.lbl_user.config(text=f"User: {name}")

    def update_book(self, book):
        self.lbl_title.config(text=book['title'])
        self.lbl_desc.config(text=book['desc'])
        self.lbl_reason.config(text=f"AI Insight: {book.get('reason', '')}")

    def add_chat_msg(self, sender, text, tag):
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, f"{sender}: {text}\n", tag)
        self.chat_history.see(tk.END)
        self.chat_history.config(state='disabled')

    def clear_chat(self):
        """Wipes the chat history window"""
        self.chat_history.config(state='normal') # Enable editing
        self.chat_history.delete('1.0', tk.END)  # Delete everything
        self.chat_history.config(state='disabled') # Disable editing

    def set_action_status(self, text):
        self.lbl_action_status.config(text=text)

# --- NEW ADMIN VIEW (INHERITS FROM DASHBOARD) ---
class AdminView(DashboardView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        # Change Header Color to identify Admin
        self.lbl_user.config(bg="#8E44AD", text="User: ADMIN")
        
        # --- TAB 3: LOGS ---
        tab_logs = tk.Frame(self.tabs, bg="white")
        self.tabs.add(tab_logs, text="System Logs ")
        
        # Table (Treeview)
        columns = ("time", "user", "book", "action")
        self.tree = ttk.Treeview(tab_logs, columns=columns, show="headings")
        
        self.tree.heading("time", text="Time")
        self.tree.heading("user", text="User")
        self.tree.heading("book", text="Book")
        self.tree.heading("action", text="Action")
        
        self.tree.column("time", width=150)
        self.tree.column("user", width=100)
        self.tree.column("book", width=150)
        self.tree.column("action", width=100)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Refresh Button
        tk.Button(tab_logs, text="REFRESH LOGS", command=controller.request_logs, 
                  bg="#8E44AD", fg="white").pack(pady=10)

    def update_logs(self, log_data):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Add new
        for log in log_data:
            self.tree.insert("", tk.END, values=(log['timestamp'], log['name'], log['title'], log['action']))

class ScanPopup(tk.Toplevel):
    def __init__(self, parent, action_type, on_cancel, controller): # <--- Added controller
        super().__init__(parent)
        self.title(f"{action_type.capitalize()} Book")
        self.geometry("400x250") # Made it slightly bigger
        self.config(bg="#ECF0F1")
        
        # Center the popup
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 125
        self.geometry(f"+{x}+{y}")
        
        # Modal (blocks other windows)
        self.transient(parent)
        self.grab_set()
        
        # Instructions
        tk.Label(self, text=f"Please SCAN Book to\n{action_type.upper()}", 
                 font=("Arial", 14, "bold"), bg="#ECF0F1", fg="#2C3E50").pack(pady=20)
        
        # Cancel Button
        tk.Button(self, text="CANCEL", command=on_cancel, bg="#C0392B", fg="white", font=("Arial", 10)).pack(pady=5)

        # --- SIMULATION TOOLS (For PC Testing) ---
        # These buttons allow you to simulate a scan directly from the popup
        tk.Frame(self, height=2, bd=1, relief="sunken", bg="gray").pack(fill="x", pady=10)
        tk.Label(self, text="[DEV] Simulate Scan:", bg="#ECF0F1", fg="gray").pack()
        
        sim_frame = tk.Frame(self, bg="#ECF0F1")
        sim_frame.pack(pady=5)

        # Use the specific IDs from your init_db.py
        tk.Button(sim_frame, text="Dune", command=lambda: controller.simulate_scan("427889591285")).pack(side="left", padx=2)
        tk.Button(sim_frame, text="Sapiens", command=lambda: controller.simulate_scan("840892482320")).pack(side="left", padx=2)
        tk.Button(sim_frame, text="Math", command=lambda: controller.simulate_scan("702212146116")).pack(side="left", padx=2)