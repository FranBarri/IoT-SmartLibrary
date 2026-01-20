import tkinter as tk
from tkinter import font, ttk, scrolledtext, messagebox
import paho.mqtt.client as mqtt
import json
import threading
import time

# --- CONFIGURATION ---
BROKER = "localhost"
TOPIC_SEND = "library/scan"
TOPIC_LISTEN = "library/display"

# --- HARDWARE CHECK ---
try:
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522
    reader = SimpleMFRC522()
    IS_PI = True
except:
    IS_PI = False

# --- STATE ---
current_username = ""
current_book_id = "" # Track what we are looking at

# --- MQTT LOGIC ---
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode("utf-8"))
    root.after(0, handle_server_response, payload)

def handle_server_response(data):
    global current_username, current_book_id
    
    # Enable chat button if it was disabled
    btn_ask.config(state="normal", text="Send")

    if data.get('status') == 'error':
        messagebox.showerror("Error", data['message'])
        return

    # HANDLE ACTIONS (Borrow/Return success)
    if data.get('type') == 'action_confirm':
        messagebox.showinfo("Success", data['message'])
        return

    # HANDLE LOGIN OR CHAT (Updates the UI)
    if data['type'] in ['login', 'chat_response']:
        current_username = data['user']
        book = data['book']
        current_book_id = book['id']

        # 1. UPDATE PERSISTENT LEFT PANEL
        lbl_book_title.config(text=book['title'])
        lbl_book_desc.config(text=book['desc'])
        lbl_book_reason.config(text=f"AI Insight: {book.get('reason', '')}")
        
        # 2. UPDATE CHAT HISTORY (If needed)
        if data['type'] == 'chat_response':
            chat_history.config(state='normal')
            chat_history.insert(tk.END, f"🤖 AI: {book.get('reason', '')}\n", "ai_msg")
            chat_history.insert(tk.END, f"   (Rec: {book['title']})\n\n", "ai_ref")
            chat_history.config(state='disabled')
            chat_history.see(tk.END)

        # 3. SWITCH TO DASHBOARD ON LOGIN
        if data['type'] == 'login':
            if data.get('role') == 'admin':
                show_frame(frame_admin)
            else:
                show_frame(frame_dashboard)
                lbl_user_welcome.config(text=f"User: {current_username}")
                
                # Reset Chat
                chat_history.config(state='normal')
                chat_history.delete(1.0, tk.END)
                chat_history.insert(tk.END, f"System: Hello {current_username}. I have selected a book for you based on your profile.\n\n", "sys_msg")
                chat_history.config(state='disabled')

def send_chat(event=None):
    text = entry_chat.get()
    if text:
        chat_history.config(state='normal')
        chat_history.insert(tk.END, f"👤 You: {text}\n", "user_msg")
        chat_history.config(state='disabled')
        chat_history.see(tk.END)
        
        msg = {"action": "chat", "user": current_username, "text": text}
        client.publish(TOPIC_SEND, json.dumps(msg))
        
        entry_chat.delete(0, tk.END)
        btn_ask.config(state="disabled", text="...")

def send_action(action_type):
    if not current_book_id:
        messagebox.showwarning("Warning", "No book selected!")
        return
    print(f"Sending {action_type} for {current_book_id}")
    msg = {"action": action_type, "user": current_username, "book_id": current_book_id}
    client.publish(TOPIC_SEND, json.dumps(msg))

def logout():
    global current_username, current_book_id
    current_username = ""
    current_book_id = ""
    show_frame(frame_login)

# --- SIMULATION ---
def simulate_scan(id_val):
    msg = {"action": "scan", "id": id_val}
    client.publish(TOPIC_SEND, json.dumps(msg))

def real_scan_loop():
    while IS_PI:
        id, text = reader.read()
        client.publish(TOPIC_SEND, json.dumps({"action": "scan", "id": str(id)}))
        time.sleep(2)

# --- SETUP MQTT ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC_LISTEN)
client.loop_start()

if IS_PI:
    threading.Thread(target=real_scan_loop, daemon=True).start()

# --- GUI CONSTRUCTION ---
root = tk.Tk()
root.title("Smart Library Terminal")
root.geometry("1000x700")

# STYLES
style = ttk.Style()
style.theme_use('clam')
style.configure("TNotebook", background="#ECF0F1", borderwidth=0)
style.configure("TNotebook.Tab", padding=[20, 12], font=('Arial', 11, 'bold'))

def show_frame(frame):
    frame_login.pack_forget()
    frame_dashboard.pack_forget()
    frame_admin.pack_forget()
    frame.pack(fill="both", expand=True)

# 1. LOGIN SCREEN
frame_login = tk.Frame(root, bg="#2C3E50")
tk.Label(frame_login, text="Smart Library System", font=("Helvetica", 32, "bold"), fg="white", bg="#2C3E50").pack(pady=120)
tk.Label(frame_login, text="Scan ID to Login", font=("Helvetica", 16), fg="#BDC3C7", bg="#2C3E50").pack()

if not IS_PI:
    frame_sim = tk.Frame(frame_login, bg="#2C3E50")
    frame_sim.pack(pady=40)
    tk.Button(frame_sim, text="[Simulate] Alice (Eng)", command=lambda: simulate_scan("123"), bg="white", width=20).pack(pady=5)
    tk.Button(frame_sim, text="[Simulate] Bob (Arts)", command=lambda: simulate_scan("456"), bg="white", width=20).pack(pady=5)

# 2. DASHBOARD (Split Layout)
frame_dashboard = tk.Frame(root, bg="#BDC3C7")

# --- HEADER ---
header = tk.Frame(frame_dashboard, bg="#34495E", height=60)
header.pack(fill="x", side="top")
lbl_user_welcome = tk.Label(header, text="User: ---", font=("Arial", 14, "bold"), fg="white", bg="#34495E")
lbl_user_welcome.pack(side="left", padx=20, pady=15)
tk.Button(header, text="LOGOUT", command=logout, bg="#C0392B", fg="white", bd=0, padx=15).pack(side="right", padx=20, pady=15)

# --- MAIN CONTENT AREA ---
content_area = tk.Frame(frame_dashboard, bg="#ECF0F1")
content_area.pack(fill="both", expand=True, padx=20, pady=20)

# LEFT PANEL: PERSISTENT BOOK INFO
left_panel = tk.Frame(content_area, bg="white", width=400, bd=1, relief="solid")
left_panel.pack(side="left", fill="y", padx=(0, 20))
left_panel.pack_propagate(False) # Force width

tk.Label(left_panel, text="CURRENT RECOMMENDATION", font=("Arial", 10, "bold"), fg="#7F8C8D", bg="white").pack(pady=(30, 10))
lbl_book_title = tk.Label(left_panel, text="Waiting...", font=("Georgia", 22, "bold"), wraplength=350, bg="white", fg="#2C3E50")
lbl_book_title.pack(pady=10)

lbl_book_desc = tk.Label(left_panel, text="Scan a card or ask the AI to see details here.", font=("Arial", 12), wraplength=350, justify="left", bg="white", fg="#34495E")
lbl_book_desc.pack(pady=10, padx=20)

tk.Frame(left_panel, height=2, bg="#ECF0F1", width=300).pack(pady=20) # Separator

lbl_book_reason = tk.Label(left_panel, text="", font=("Arial", 11, "italic"), wraplength=350, bg="white", fg="#27AE60")
lbl_book_reason.pack(padx=20)

# RIGHT PANEL: TABS (ACTIONS & CHAT)
right_panel = tk.Frame(content_area, bg="#ECF0F1")
right_panel.pack(side="right", fill="both", expand=True)

tabs = ttk.Notebook(right_panel)
tabs.pack(fill="both", expand=True)

# TAB 1: ACTIONS
tab_actions = tk.Frame(tabs, bg="white")
tabs.add(tab_actions, text=" ⚡ Actions ")

tk.Label(tab_actions, text="What would you like to do with this book?", font=("Arial", 14), bg="white").pack(pady=40)

btn_borrow = tk.Button(tab_actions, text="BORROW BOOK", command=lambda: send_action("borrow"), 
                       bg="#27AE60", fg="white", font=("Arial", 14, "bold"), width=20, height=2)
btn_borrow.pack(pady=10)

btn_return = tk.Button(tab_actions, text="RETURN BOOK", command=lambda: send_action("return"), 
                       bg="#F39C12", fg="white", font=("Arial", 14, "bold"), width=20, height=2)
btn_return.pack(pady=10)

# TAB 2: CHAT
tab_chat = tk.Frame(tabs, bg="#F4F6F7")
tabs.add(tab_chat, text=" 💬 AI Librarian ")

chat_history = scrolledtext.ScrolledText(tab_chat, state='disabled', font=("Arial", 11), padx=10, pady=10)
chat_history.pack(fill="both", expand=True, padx=10, pady=(10, 0))
chat_history.tag_config("user_msg", foreground="#2980B9", font=("Arial", 11, "bold"))
chat_history.tag_config("ai_msg", foreground="#27AE60", font=("Arial", 11, "bold"))
chat_history.tag_config("sys_msg", foreground="gray", font=("Arial", 10, "italic"))

input_frame = tk.Frame(tab_chat, bg="#F4F6F7")
input_frame.pack(fill="x", padx=10, pady=10)

entry_chat = tk.Entry(input_frame, font=("Arial", 12))
entry_chat.pack(side="left", fill="x", expand=True, padx=(0, 10))
entry_chat.bind("<Return>", send_chat)

btn_ask = tk.Button(input_frame, text="Send", command=send_chat, bg="#2980B9", fg="white", width=10)
btn_ask.pack(side="right")

# 3. ADMIN FRAME
frame_admin = tk.Frame(root, bg="#2C3E50")
tk.Label(frame_admin, text="ADMIN PANEL", fg="white", font=("Arial", 20)).pack(pady=50)
tk.Button(frame_admin, text="LOGOUT", command=logout).pack()

# Start
show_frame(frame_login)
root.mainloop()