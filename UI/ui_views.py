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
        
        tk.Button(self.sim_frame, text="[Sim] Alice", command=lambda: controller.simulate_scan("123"), bg="white", width=15).pack(side="left", padx=5)
        tk.Button(self.sim_frame, text="[Sim] Bob", command=lambda: controller.simulate_scan("456"), bg="white", width=15).pack(side="left", padx=5)

class DashboardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#BDC3C7")
        self.controller = controller
        
        # --- HEADER ---
        header = tk.Frame(self, bg=BG_HEADER, height=60)
        header.pack(fill="x", side="top")
        self.lbl_user = tk.Label(header, text="User: ---", font=("Arial", 14, "bold"), fg="white", bg=BG_HEADER)
        self.lbl_user.pack(side="left", padx=20, pady=15)
        tk.Button(header, text="LOGOUT", command=controller.logout, bg="#C0392B", fg="white", bd=0, padx=15).pack(side="right", padx=20, pady=15)

        # --- MAIN CONTENT ---
        content = tk.Frame(self, bg=BG_LIGHT)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. LEFT PANEL (Book Info)
        left_panel = tk.Frame(content, bg="white", width=400, bd=1, relief="solid")
        left_panel.pack(side="left", fill="y", padx=(0, 20))
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="CURRENT RECOMMENDATION", font=("Arial", 10, "bold"), fg="gray", bg="white").pack(pady=(30, 10))
        self.lbl_title = tk.Label(left_panel, text="Waiting...", font=("Georgia", 22, "bold"), wraplength=350, bg="white", fg=BG_DARK)
        self.lbl_title.pack(pady=10)
        
        self.lbl_desc = tk.Label(left_panel, text="Scan a card...", font=("Arial", 12), wraplength=350, justify="left", bg="white", fg="#34495E")
        self.lbl_desc.pack(pady=10, padx=20)
        
        tk.Frame(left_panel, height=2, bg=BG_LIGHT, width=300).pack(pady=20) # Divider
        
        self.lbl_reason = tk.Label(left_panel, text="", font=("Arial", 11, "italic"), wraplength=350, bg="white", fg=ACCENT_GREEN)
        self.lbl_reason.pack(padx=20)

        # 2. RIGHT PANEL (Tabs)
        right_panel = tk.Frame(content, bg=BG_LIGHT)
        right_panel.pack(side="right", fill="both", expand=True)

        tabs = ttk.Notebook(right_panel)
        tabs.pack(fill="both", expand=True)

        # --- TAB 1: ACTIONS ---
        tab_actions = tk.Frame(tabs, bg="white")
        tabs.add(tab_actions, text=" ⚡ Actions ")
        
        tk.Label(tab_actions, text="What would you like to do?", font=("Arial", 14), bg="white").pack(pady=40)
        
        tk.Button(tab_actions, text="BORROW BOOK", command=lambda: controller.send_action("borrow"), 
                  bg=ACCENT_GREEN, fg="white", font=("Arial", 14, "bold"), width=20, height=2).pack(pady=10)
        
        tk.Button(tab_actions, text="RETURN BOOK", command=lambda: controller.send_action("return"), 
                  bg="#F39C12", fg="white", font=("Arial", 14, "bold"), width=20, height=2).pack(pady=10)

        # --- TAB 2: CHAT ---
        tab_chat = tk.Frame(tabs, bg="#F4F6F7")
        tabs.add(tab_chat, text=" 💬 AI Librarian ")
        
        self.chat_history = scrolledtext.ScrolledText(tab_chat, state='disabled', font=("Arial", 11), padx=10, pady=10)
        self.chat_history.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        self.chat_history.tag_config("user_msg", foreground=ACCENT_BLUE, font=("Arial", 11, "bold"))
        self.chat_history.tag_config("ai_msg", foreground=ACCENT_GREEN, font=("Arial", 11, "bold"))
        
        input_frame = tk.Frame(tab_chat, bg="#F4F6F7")
        input_frame.pack(fill="x", padx=10, pady=10)
        
        self.entry_chat = tk.Entry(input_frame, font=("Arial", 12))
        self.entry_chat.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_chat.bind("<Return>", lambda e: self.send_chat())
        
        self.btn_ask = tk.Button(input_frame, text="Send", command=self.send_chat, bg=ACCENT_BLUE, fg="white", width=10)
        self.btn_ask.pack(side="right")

    def send_chat(self):
        text = self.entry_chat.get()
        if text:
            self.controller.send_chat(text)
            self.entry_chat.delete(0, tk.END)

    # --- UPDATE HELPERS ---
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

class AdminView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2C3E50")
        tk.Label(self, text="ADMIN PANEL", fg="white", font=("Arial", 20)).pack(pady=50)
        tk.Button(self, text="LOGOUT", command=controller.logout).pack()