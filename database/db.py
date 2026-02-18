import sqlite3

def init_db():
    conn=sqlite3.connect("database.db")
    cursor=conn.cursor()

    cursor.execute("""
               CREATE TABLE IF NOT EXISTS users(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT UNIQUE NOT NULL,
                   password TEXT NOT NULL
               );
               """)
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS search_history (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL,
                      query TEXT NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)

    conn.commit()
    conn.close()