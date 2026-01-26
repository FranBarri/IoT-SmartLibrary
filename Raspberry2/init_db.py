import sqlite3

DB = "library.db"

def setup_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # --- USERS ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            department TEXT,
            interest TEXT,
            role TEXT NOT NULL,
            current_book_id TEXT
        )
    """)

    # --- BOOKS ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            genre TEXT,
            description TEXT,
            status TEXT NOT NULL
        )
    """)

    # --- LOG ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS log (
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT,
            book_id TEXT,
            action TEXT
        )
    """)

    # Users
    users = [
        ("1045542929320", "Alice",  21, "Science",      "Sci-Fi",       "admin",  None),
        ("152089854730",  "Bob",    20, "Arts",         "History",      "client", None),
        ("907835540408",  "John",   22, "Science",      "Nature",       "client", None),
        ("151533650804",  "Arthur", 23, "Engineering",  "Mathematics",  "client", None),
        ("702381884176",  "Mary",   21, "Sports",       "Sports",       "client", None),
    ]

    # Books
    books = [
        ("770095055811", "Dune", "Frank Herbert", "Sci-Fi", "Epic sci-fi on Arrakis.", "available"),
        ("840892482320", "Sapiens", "Yuval Noah Harari", "History", "A brief history of humankind.", "available"),
        ("700852798363", "The Hidden Life of Trees", "Peter Wohlleben", "Nature", "How forests work and communicate.", "available"),
        ("702212146116", "How Not to Be Wrong", "Jordan Ellenberg", "Mathematics", "Math thinking for real life.", "available"),
        ("427889591285", "Moneyball", "Michael Lewis", "Sports", "Data-driven sports revolution.", "available"),
    ]
    # Insert initial data if not exists (ignoring duplicates)
    c.executemany("""
        INSERT OR IGNORE INTO users (user_id, name, age, department, interest, role, current_book_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, users)

    c.executemany("""
        INSERT OR IGNORE INTO books (book_id, title, author, genre, description, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, books)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_db()
    print("Database initialized (users, books, log).")
