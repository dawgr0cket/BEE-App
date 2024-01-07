import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

#all changes to tables are made here. If changes to tables are to be made, please make a new conn.execute line. This is to keep track of changes

# conn.execute("DROP TABLE user")
# conn.execute('CREATE TABLE user (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(255) NOT NULL UNIQUE, email VARCHAR(255) NOT NULL UNIQUE, password INT(255) NOT NULL, phone_no INT(8), dob STRING, gender STRING, profile_pic LONGBLOB, datetime INT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
# conn.execute('CREATE TABLE blog (username VARCHAR(255) NOT NULL,title TEXT, summary TEXT, blog_pic STRING, description TEXT, datetime INT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
# conn.execute('CREATE TABLE tradeinform (username VARCHAR(255) NOT NULL, no_of_clothes INT, tradein_pic LONGBLOB, description TEXT, datetime INT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
# conn.execute('ALTER TABLE tradeinform ADD COLUMN tradein_id INT')
# conn.execute('ALTER TABLE tradeinform ADD COLUMN status BOOLEAN')
# conn.execute('CREATE TABLE addvouchers (username VARCHAR(255) NOT NULL, title TEXT, value INT, condition TEXT, code STRING)')
# conn.execute('CREATE TABLE validvouchers (row_id INTEGER PRIMARY KEY AUTOINCREMENT, code STRING)')
print("Created table successfully!")

conn.close()