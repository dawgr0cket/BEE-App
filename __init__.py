import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('CREATE TABLE blog (title TEXT, summary TEXT, files FILE, description TEXT)')
print("Created table successfully!")

conn.close()