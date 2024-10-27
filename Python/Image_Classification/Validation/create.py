import sqlite3

# Specify the path where you want to create the database
db_path = 'C:\\Users\\danny\\Desktop\\repos\\CuWebsite2024Updated\\database.db'

# Connect to SQLite and create the database
def create_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()
    print("Database created successfully.")

if __name__ == "__main__":
    create_database()
