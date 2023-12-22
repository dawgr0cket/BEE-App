import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

#all changes to tables are made here. If changes to tables are to be made, please make a new conn.execute line. This is to keep track of changes

# conn.execute("DROP TABLE blog")
#conn.execute('CREATE TABLE user (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(255) NOT NULL UNIQUE, email VARCHAR(255) NOT NULL UNIQUE, password INT(255) NOT NULL)')
# conn.execute('CREATE TABLE blog (username VARCHAR(255) NOT NULL,title TEXT, summary TEXT, blog_pic STRING, description TEXT, datetime INT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
# conn.execute('ALTER TABLE user ADD COLUMN phone_no INT(8)')
# conn.execute('ALTER TABLE user ADD COLUMN dob STRING')
# conn.execute('ALTER TABLE user ADD COLUMN gender STRING')
# conn.execute('ALTER TABLE user ADD COLUMN profile_pic STRING')


print("Created table successfully!")

conn.close()