import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL UNIQUE,
            nickname TEXT NOT NULL,
            username TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_user_by_telegram_id(telegram_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def get_all_users_from_bd():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users')

    all_users = cursor.fetchall()

    conn.close()
    return all_users if all_users else []

def add_user(telegram_id, nickname, username, role):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (telegram_id, nickname, username, role) VALUES (?, ?, ?, ?)', (telegram_id, nickname, username, role))
    conn.commit()
    conn.close()

