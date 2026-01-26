import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import config

def db_connect():
    # Use the shared config path
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def scan_id(conn, scanned_id):
    # 1. Try to find a USER
    user = conn.execute(
        "SELECT user_id, name, role, current_book_id, interest FROM users WHERE user_id=?",
        (scanned_id,)
    ).fetchone()
    
    if user:
        return {
            "status": "success", 
            "type": "login", # Changed 'user' to 'login' to match your UI logic
            "user": user["name"], # Changed to match UI
            "role": user["role"],
            "user_id": user["user_id"],
            "interest": user["interest"],
            "current_book_id": user["current_book_id"]
        }

    # 2. Try to find a BOOK
    book = conn.execute(
        "SELECT book_id, title, author, genre, description, status FROM books WHERE book_id=?",
        (scanned_id,)
    ).fetchone()
    
    if book:
        return {
            "status": "success",
            "type": "book_scan",
            "id": book["book_id"],
            "title": book["title"],
            "author": book["author"],
            "desc": book["description"],
            "status_book": book["status"],
        }

    return {"status": "error", "message": "Unknown ID"}

def borrow_book(conn, user_id, book_id):
    # Logic: Check if user exists, check if book is available
    try:
        user = conn.execute("SELECT user_id, current_book_id FROM users WHERE user_id=?", (user_id,)).fetchone()
        book = conn.execute("SELECT book_id, status FROM books WHERE book_id=?", (book_id,)).fetchone()

        if not user: return {"status": "error", "message": "User not found"}
        if not book: return {"status": "error", "message": "Book not found"}
        if user["current_book_id"]: return {"status": "error", "message": "You already have a book borrowed!"}
        if book["status"] != "available": return {"status": "error", "message": "Book is already borrowed"}

        # Perform Transaction
        conn.execute("UPDATE users SET current_book_id=? WHERE user_id=?", (book_id, user_id))
        conn.execute("UPDATE books SET status='borrowed' WHERE book_id=?", (book_id,))
        conn.execute("INSERT INTO log(user_id, book_id, action) VALUES (?, ?, 'borrowed')", (user_id, book_id))
        conn.commit()
        return {"status": "success", "type": "action_confirm", "message": f"Successfully borrowed book {book_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def return_book(conn, user_id, book_id):
    try:
        user = conn.execute("SELECT user_id, current_book_id FROM users WHERE user_id=?", (user_id,)).fetchone()
        
        if not user: return {"status": "error", "message": "User not found"}
        if user["current_book_id"] != book_id: return {"status": "error", "message": "You don't have this book borrowed."}

        # Perform Transaction
        conn.execute("UPDATE users SET current_book_id=NULL WHERE user_id=?", (user_id,))
        conn.execute("UPDATE books SET status='available' WHERE book_id=?", (book_id,))
        conn.execute("INSERT INTO log(user_id, book_id, action) VALUES (?, ?, 'returned')", (user_id, book_id))
        conn.commit()
        return {"status": "success", "type": "action_confirm", "message": f"Successfully returned book {book_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def log_action(conn, user_id, action, book_id=None):
    try:
        conn.execute(
            "INSERT INTO log (user_id, book_id, action) VALUES (?, ?, ?)",
            (user_id, book_id, action)
        )
        conn.commit()
    except Exception as e:
        print(f"LOG ERROR: {e}")

def get_logs(conn):
    try:
        # Join tables to get readable names instead of just IDs
        query = """
            SELECT log.timestamp, users.name, books.title, log.action 
            FROM log
            LEFT JOIN users ON log.user_id = users.user_id
            LEFT JOIN books ON log.book_id = books.book_id
            ORDER BY log.timestamp DESC LIMIT 50
        """
        rows = conn.execute(query).fetchall()
        # Convert to list of dicts for JSON serialization
        return [dict(row) for row in rows]
    except Exception as e:
        return []