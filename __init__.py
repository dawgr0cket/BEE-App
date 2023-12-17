import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute("DROP TABLE users")
#conn.execute('CREATE TABLE user (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(255) NOT NULL UNIQUE, email VARCHAR(255) NOT NULL UNIQUE, password INT(255) NOT NULL)')
# conn.execute('CREATE TABLE blog (title TEXT, summary TEXT, files FILE, description TEXT)')
print("Created table successfully!")

conn.close()