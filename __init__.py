import sqlite3
from datetime import datetime

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

# all changes to tables are made here. If changes to tables are to be made, please make a new conn.execute line. This is to keep track of changes

# conn.execute("DROP TABLE addvouchers")
# conn.execute('CREATE TABLE user (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(255) NOT NULL UNIQUE, email VARCHAR(255) NOT NULL UNIQUE, password INT(255) NOT NULL, phone_no INT(8), dob STRING, gender STRING, profile_pic LONGBLOB, datetime INT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
# conn.execute('CREATE TABLE blog (username VARCHAR(255) NOT NULL,title TEXT, summary TEXT, blog_pic STRING, description TEXT, datetime INT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
# conn.execute('CREATE TABLE tradeinform (username VARCHAR(255) NOT NULL, no_of_clothes INT, tradein_pic LONGBLOB, description TEXT, datetime INT NOT NULL DEFAULT CURRENT_TIMESTAMP, tradein_id STRING)')
# conn.execute('CREATE TABLE tradeinentries (tradein_id STRING, username VARCHAR(255), no_of_clothes INT, status BOOLEAN)')
# conn.execute('ALTER TABLE tradeinform ADD COLUMN tradein_id INT')
# conn.execute('ALTER TABLE tradeinform ADD COLUMN status BOOLEAN')
# conn.execute('CREATE TABLE addvouchers (username VARCHAR(255) NOT NULL, title TEXT, value INT, condition TEXT, code TEXT NOT NULL UNIQUE, expiry_date DATETIME NOT NULL, status TEXT NOT NULL DEFAULT "active")')
# conn.execute('CREATE TABLE validvouchers (row_id INTEGER PRIMARY KEY AUTOINCREMENT, code STRING)')
# conn.execute('CREATE TABLE cart (username VARCHAR(255) NOT NULL, product_name STRING)')


# conn.execute('CREATE TABLE inventory (product_name STRING, product_price FLOAT, product_image LONGBLOB, product_description LONGTEXT, product_quantity INT, shop STRING)')
# ^ the 'shop' column is BOOLEAN, 0 means product is for eco while 1 means product is for trade in

# conn.execute('CREATE TABLE reviews (product_name STRING, review LONGTEXT)')
# conn.execute('CREATE TABLE wishlist (username VARCHAR(255) NOT NULL, product_name STRING)')
# conn.execute('CREATE TABLE inventorysize (product_name STRING, product_size STRING)')
# conn.execute('CREATE TABLE inventorycolour (product_name STRING, product_colour STRING)')
# conn.execute('ALTER TABLE cart ADD COLUMN product_quantity STRING')
# conn.execute('DROP TABLE addvouchers')
# conn.execute('CREATE TABLE sessions (session_id STRING, username VARCHAR(255) NOT NULL, product_name STRING,total INT, payment_timestamp INT NOT NULL DEFAULT CURRENT_TIMESTAMP, status BOOLEAN)')
# conn.execute('CREATE TABLE addresses (id INTEGER PRIMARY KEY AUTOINCREMENT, block TEXT NOT NULL, unitno TEXT NOT NULL, street TEXT NOT NULL, city TEXT NOT NULL, postal_code TEXT NOT NULL, username VARCHAR(255) NOT NULL)')
# conn.execute('''
#         CREATE TABLE IF NOT EXISTS pages (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             title TEXT,
#             content TEXT
#         )
#     ''')
# conn.execute('''
#     INSERT INTO pages (title, content)
#     VALUES
#         ('blog', 'Blog
# Create Your Own Blog Now!
# Create Blog
#
# I Love To Recycle!
# @wongjaeno
# i love to save the environment by making my own planter with recyclable materials.
#
# Blog Image
# testetstetetettetetetetetetetettetetetetettetetetetetetetteteetetete
#
# Created On 2024-02-07 18:08:28
#
# Edit
# Delete
# Welcome To B.E.E
# @adminappdev
# welcome! i hope you enjoy your experience here!
#
# Blog Image
# i hateeeeeeeeeeeeeeee cattttttttttttttttt. testingsssssssssssssss
#
# Created On 2024-01-24 06:04:09
#
# Edit
# Delete'),
#         ('eco', 'Eco
#
# Hoodie
# $35.00
#
# Add To Cart
#
#
# White Polo Shirt
# $24.00
#
# Add To Cart
#
# '),
#         ('tradein', 'Trade-In
# Trade-In Your preloved clothes
#
# Trade-In Now!
# Trade-In
# Red Blouse Shirt
# Red Blouse Shirt
# $15.00
#
# Out Of Stock
#
# Orange Round-Neck Shirt
# Orange Round-Neck Shirt
# $18.00
#
# Add To Cart
# '),
#         ('cart', 'Cart
# adminappdev''s Cart
#
# No Items in cart!
# Product	Price	Stock Left	Quantity
# Hoodie
#
#
# 35.0
#
# 13
#
# +
# 1
# -
# Shipping Information
# Address: 972 sunshine street 82, #04-917, 760972, Singapore
#
# Edit AddressProceed to Checkout
# '),
# ('order_history', 'Order History
# adminappdev''s Order History
#
# Past Orders
# Order ID	Date	Items	Total	Status
# #CUnDVerHNW	2024-01-25	2	$33	Packing...
#
# '),
# ('view_vouchers', 'Vouchers
# adminappdev''s Vouchers
#
# $5 OFF
# Code:
# 9BYoeSnEHviTerM4iycoVh
# Condition:
# '),
# ('view_tradeins', 'Trade-In Forms
# adminappdev''s Trade-In Forms
#
# Trade-In No.	Trade-In ID	No. Of Clothes	Status	Date Of Submission	View Form
# 1	f30a20b1	1
# Approved
#
#
# Mail your clothing items to
# 123 henderson road Avenue 4 S782038, #02-238
#
# 2024-01-09 08:41:57	View
# '),
# ('tradeinno', 'Trade-In Form
# Hello adminappdev! What do you want to trade in?
#
#
# Number Of Clothes
#
# 1
# ')
# ''')
# conn.commit()
print("Created table successfully!")

conn.close()
