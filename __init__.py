import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

# conn.execute("DROP TABLE blog")
#conn.execute('CREATE TABLE user (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(255) NOT NULL UNIQUE, email VARCHAR(255) NOT NULL UNIQUE, password INT(255) NOT NULL)')
conn.execute('CREATE TABLE blog (username VARCHAR(255) NOT NULL,title TEXT, summary TEXT, files FILE, description TEXT, datetime INT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
print("Created table successfully!")

conn.close()