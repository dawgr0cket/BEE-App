import sqlite3
from datetime import datetime

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

# all changes to tables are made here. If changes to tables are to be made, please make a new conn.execute line. This is to keep track of changes

#conn.execute("DROP TABLE addvouchers")
# conn.execute('CREATE TABLE user (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(255) NOT NULL UNIQUE, email VARCHAR(255) NOT NULL UNIQUE, password INT(255) NOT NULL, phone_no INT(8), dob STRING, gender STRING, profile_pic LONGBLOB, datetime INT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
# conn.execute('CREATE TABLE blog (username VARCHAR(255) NOT NULL,title TEXT, summary TEXT, blog_pic STRING, description TEXT, datetime INT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
# conn.execute('CREATE TABLE tradeinform (username VARCHAR(255) NOT NULL, no_of_clothes INT, tradein_pic LONGBLOB, description TEXT, datetime INT NOT NULL DEFAULT CURRENT_TIMESTAMP, tradein_id STRING)')
# conn.execute('CREATE TABLE tradeinentries (tradein_id STRING, username VARCHAR(255), no_of_clothes INT, status BOOLEAN)')
# conn.execute('ALTER TABLE tradeinform ADD COLUMN tradein_id INT')
# conn.execute('ALTER TABLE tradeinform ADD COLUMN status BOOLEAN')
#conn.execute('CREATE TABLE addvouchers (username VARCHAR(255) NOT NULL, title TEXT, value INT, condition TEXT, code TEXT NOT NULL UNIQUE, expiry_date DATETIME NOT NULL, status TEXT NOT NULL DEFAULT "active")')
# conn.execute('CREATE TABLE validvouchers (row_id INTEGER PRIMARY KEY AUTOINCREMENT, code STRING)')
# conn.execute('CREATE TABLE cart (username VARCHAR(255) NOT NULL, product_name STRING)')


# conn.execute('CREATE TABLE inventory (product_name STRING, product_price FLOAT, product_image LONGBLOB, product_description LONGTEXT, product_quantity INT, shop STRING)')
# ^ the 'shop' column is BOOLEAN, 0 means product is for eco while 1 means product is for trade in

# conn.execute('CREATE TABLE reviews (product_name STRING, review LONGTEXT)')
# conn.execute('CREATE TABLE wishlist (username VARCHAR(255) NOT NULL, product_name STRING)')
# conn.execute('CREATE TABLE inventorysize (product_name STRING, product_size STRING)')
# conn.execute('CREATE TABLE inventorycolour (product_name STRING, product_colour STRING)')
# conn.execute('ALTER TABLE inventory ADD COLUMN price_id STRING') # not ran yet
# conn.execute('DROP TABLE addvouchers')
# conn.execute('CREATE TABLE sessions (session_id STRING, username VARCHAR(255) NOT NULL, product_name STRING, payment_timestamp INT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
# conn.execute('CREATE TABLE addresses (id INTEGER PRIMARY KEY AUTOINCREMENT, block TEXT NOT NULL, unitno TEXT NOT NULL, street TEXT NOT NULL, city TEXT NOT NULL, postal_code TEXT NOT NULL, username VARCHAR(255) NOT NULL)')
print("Created table successfully!")

conn.close()
