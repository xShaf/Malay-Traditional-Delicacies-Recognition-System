import sqlite3

DATABASE_NAME = 'kuih.db'

def get_db(db_name=DATABASE_NAME):
    conn = sqlite3.connect(db_name)
    return conn

def init_db(db_name=DATABASE_NAME):
    conn = get_db(db_name)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS kuih (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image TEXT NOT NULL,
            history TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_kuih(name, image, history, db_name=DATABASE_NAME):
    conn = get_db(db_name)
    c = conn.cursor()
    c.execute("INSERT INTO kuih (name, image, history) VALUES (?, ?, ?)", (name, image, history))
    conn.commit()
    conn.close()
