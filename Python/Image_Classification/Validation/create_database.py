import os
import sqlite3

# Specify the path for the database
db_path = os.path.join(os.getcwd(), 'database.db')

# Create the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

conn.commit()
conn.close()

# Print the location of the database
print(f"Database created at: {db_path}")
