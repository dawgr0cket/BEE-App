import ast
import os
import urllib.parse
import uuid
import shortuuid
import functools
import stripe
import re

from chatbot import get_response
from tradeinform import Tradeinform
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, g, session, abort
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from Users import Users
from flask_login import UserMixin, logout_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, FileField, EmailField, IntegerField, DateField, RadioField, SelectField, \
    TextAreaField, validators
from wtforms.validators import Length, ValidationError, DataRequired
import sqlite3

from flask import Flask, render_template, request, jsonify
from chatbot import get_response

app = Flask(__name__)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'sbufbv8829gf2k'

# stripe.api_key = os.environ.get(
#     'sk_test_51OPSVaIGppHzuUaIImziYC43tisQhhhwNwjgcFtY1yltxTHYQrQRykjkHpBpGEHaUwmAH7Dbb3RwhuhZhMqztw1S00d7rsLUVF')  # add in secret key
# app.config[
#     'STRIPE_PUBLIC_KEY'] = 'pk_test_51OPSVaIGppHzuUaIIJsjb08I1RVMYwSN1IinmZ5TcUrqhi1xSlFnDAlbW1hw046EfdSnCvneXtf6n3hVvFfTcDgX00WfET7pNV'
# app.config[
#     'STRIPE_SECRET_KEY'] = 'sk_test_51OPSVaIGppHzuUaIImziYC43tisQhhhwNwjgcFtY1yltxTHYQrQRykjkHpBpGEHaUwmAH7Dbb3RwhuhZhMqztw1S00d7rsLUVF'
stripe.api_key = os.environ.get(
    'sk_test_51OXo7EE7eSiwC8HIawN9uzawPtA4zM4zGnQPRXAkT45I2BqkgrQtLObsI335ynYMGxNCLn8oGqwc4TmSwXJQHyk800TanNYJTX')  # add in secret key
app.config[
    'STRIPE_PUBLIC_KEY'] = 'pk_test_51OXo7EE7eSiwC8HINmXeqKjUfYXu9wrOW0jJ1JwFjqyUfkqSdofrl1c41rFxfsXQDJp1xOozWfAptREuraUHklvx00wl8Zg5xl'
app.config[
    'STRIPE_SECRET_KEY'] = 'sk_test_51OXo7EE7eSiwC8HIawN9uzawPtA4zM4zGnQPRXAkT45I2BqkgrQtLObsI335ynYMGxNCLn8oGqwc4TmSwXJQHyk800TanNYJTX'
endpoint_secret = 'whsec_ce34836592ee6b8aae39f8c9a53faf9ae4280570777cc4a7d381ac33d50423ac'

UPLOAD_FOLDER = 'static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db.init_app(app)


def create_product_and_price(name, price, currency, image_url, quantity, sizes):
    # Create product
    product = stripe.Product.create(name=name, images=['static/img/' + image_url], metadata={'sizes': sizes})

    # Create price
    price = stripe.Price.create(
        unit_amount=price,
        currency=currency,
        product=product.id,
    )

    # Update product inventory
    stripe.Product.modify(
        product.id,
        metadata={
            'quantity': quantity
        }
    )

    return product.id, price.id


# @app.route('/create-checkout-session/<rows>', methods=['POST'])
def create_stripe_checkout_session(lists, username):
    stripe.api_key = 'sk_test_51OXo7EE7eSiwC8HIawN9uzawPtA4zM4zGnQPRXAkT45I2BqkgrQtLObsI335ynYMGxNCLn8oGqwc4TmSwXJQHyk800TanNYJTX'
    decoded_url = urllib.parse.unquote(lists)  # Decode the URL
    start_index = decoded_url.find("[")  # Find the start index of the list
    end_index = decoded_url.find("]") + 1  # Find the end index of the list
    list_str = decoded_url[start_index:end_index]  # Extract the list string
    lists = ast.literal_eval(list_str)
    line_items = []
    for row in lists:
        item = {
            'price_data': {
                'currency': 'sgd',
                'unit_amount': int(row['price'] * 100),
                "product_data": {
                    "name": row['name'],
                    "images": ["static/img/" + row['image']]
                }
            },
            'quantity': 1
        }
        line_items.append(item)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        metadata={
            'username': username
        },
        client_reference_id=username,  # Store the username in the client_reference_id field
        success_url='http://localhost:5000/success/' + username,
        cancel_url='http://localhost:5000/cancel/' + username,
    )
    return session


@app.route('/checkout/<lists>/<username>', methods=['GET','POST'])
def checkout(lists, username):
    session_id = create_stripe_checkout_session(lists, username)
    return redirect(session_id.url, code=303)
    # return redirect(f"https://checkout.stripe.com/pay/{session_id}")
    # return render_template('checkout.html')


@app.route('/applydisc/<username>', methods=['GET', 'POST'])
def applydisc(username):
    if request.method == 'POST':
        discount = request.form['discount']
        con = get_db()
        cur = con.cursor()
        cur.execute('SELECT value FROM addvouchers WHERE code = ?', (discount,))
        deduct = cur.fetchall()[0]
        cur.execute('DELETE FROM addvouchers WHERE code = ?', (discount,))
        con.commit()
    return redirect(url_for('cart', username=username, deduct=deduct))


@app.route('/cart/<username>/<deduct>')
def cartdisc(username,deduct):
    return render_template('cart.html', username=username, deduct=deduct)


# def checkoutform(lists, username):
#     form = AddressForm()
#     if form.validate_on_submit():
#         # Access the form data
#         block = form.block.data
#         unitno = form.unitno.data
#         street = form.street.data
#         city = form.city.data
#         state = form.state.data
#         postal_code = form.postal_code.data
#
#         con = get_db()
#         con.execute('INSERT INTO addresses (block, unitno, street, city, state, postal_code, username) VALUE (?,?,?,?,?,?,?)', (block, unitno, street, city, state, postal_code, username))
#         con.commit()
#         # Redirect to a success page or display a success message
#         return redirect(url_for('checkout', lists=lists, username=username))
#     return render_template('checkout.html', form=form)


@app.route('/payment')
def payment():
    return render_template('payment.html')


@app.route('/success/<username>')
def success(username):
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute('SELECT * FROM cart WHERE username = ?', (username,))
        products = cur.fetchall()
        sessionid = str(shortuuid.uuid())
        productnamelist = []
        orders = []
        total = 0
        for product in products:
            cur.execute('INSERT INTO sessions (session_id, username, product_name) VALUES (?,?,?)', (sessionid, username, product[1]))
            con.commit()
            productnamelist.append(product[1])
        for productname in productnamelist:
            cur.execute('SELECT * FROM inventory WHERE product_name = ?', (productname,))
            order = cur.fetchall()
            for price in order:
                total = total + price[1]
            orders.append(order)
        cur.execute('DELETE FROM cart WHERE username = ?', (username,))
    except:
        msg = 'An Error has Occurred'
        flash(msg)
    finally:
        msg = 'Purchase Completed!'
        flash(msg)
        return render_template('successfultrans.html', orders=orders, sessionid=sessionid, total=total, username=username)


# @app.route('/successfultrans/<username>')
# def successfultrans(username):
#     charge_id = None
#     amount = None
#     currency = None
#     transaction_id = None
#     product_details = None
#
#     try:
#         # Retrieve the customer based on the username from metadata
#         customers = stripe.Customer.list(metadata={'username': username})
#         if len(customers.data) == 0:
#             return render_template('successfultrans.html', charge_id=charge_id, amount=amount, currency=currency, transaction_id=transaction_id, product_details=product_details)
#
#         customer = customers.data[0]
#
#         # Retrieve the customer's charges and sort them by created date in descending order
#         charges = stripe.Charge.list(
#             customer=customer.id,
#             limit=1,
#             paid=True,
#             status='succeeded',
#             expand=['data.balance_transaction', 'data.payment_intent', 'data.payment_intent.lines.data.price.product']
#         )
#         if len(charges.data) == 0:
#             return render_template('successfultrans.html', charge_id=charge_id, amount=amount, currency=currency, transaction_id=transaction_id, product_details=product_details)
#
#         charge = charges.data[0]
#
#         # Extract relevant information from the charge
#         charge_id = charge.id
#         amount = charge.amount
#         currency = charge.currency
#         transaction_id = charge.balance_transaction.id
#
#         # Retrieve product details for each line item
#         product_details = []
#         for line_item in charge.payment_intent.lines.data:
#             product = line_item.price.product
#             product_id = product.id
#             product_name = product.name
#             price = line_item.price.unit_amount / 100  # Convert the price to the desired currency format
#             product_details.append({'product_id': product_id, 'product_name': product_name, 'price': price})
#     except Exception as e:
#         msg = 'An Error has Occurred: ' + str(e)
#         flash(msg)
#         return render_template('home.html')
#     finally:
#         return render_template('successfultrans.html', charge_id=charge_id, amount=amount, currency=currency, transaction_id=transaction_id, product_details=product_details)
#

@app.route('/cancel')
def cancel():
    return 'Payment canceled.'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE user_id = ?', (user_id,)
        ).fetchone()


# bp = Blueprint('auth', __name__, url_prefix='/auth')


class BlogForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    summary = StringField('Summary', validators=[Length(min=1, max=150), DataRequired()])
    blog_pic = FileField("Blog Photo")
    description = StringField('Blog away...', validators=[Length(min=50, max=800), DataRequired()])
    submit = SubmitField("Submit")


class AddressForm(FlaskForm):
    block = StringField('Block', validators=[DataRequired()])
    unitno = StringField('Unit No.', validators=[DataRequired()])
    street = StringField('Street', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UserForm(FlaskForm):
    username = StringField("Username")
    email = EmailField('Email')
    # phone_no = IntegerField("Phone Number", [validators.Length(min=8, max=8)])
    phone_no = IntegerField("Phone Number", validators=[
       validators.NumberRange(min=10000000, max=99999999, message="Phone number must be 8 digits!")])
    dob = DateField("Date Of Birth")
    gender = RadioField("Gender", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    profile_pic = FileField("Profile Picture", validators=[DataRequired()])
    submit = SubmitField("Submit")


class TradeInForm(FlaskForm):
    no_of_clothes = SelectField("Number Of Clothes", choices=[1, 2, 3, 4, 5, 6], validators=[DataRequired()])
    tradein_pic = FileField("Picture Of Clothing Item", validators=[DataRequired()])
    description = TextAreaField("Description Of Clothing Item", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ProductForm(FlaskForm):
    product_name = StringField("Product Name")
    shop = RadioField("Product for Eco or Trade-In", choices=[('Eco', 'Eco'), ('Trade-In', 'Trade-In')])
    product_price = IntegerField("Product Price", validators=[Length(min=0, max=8)])
    product_image = FileField("Product Images")
    product_description = TextAreaField("Description Of Product")
    product_quantity = IntegerField('Product Quantity')
    submit = SubmitField("Submit")


class VoucherForm(FlaskForm):
    voucher_name = StringField("Voucher Name")
    discount = IntegerField('Discount')
    condition = TextAreaField('Condition')
    submit = SubmitField("Submit")


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['psw']
        db = get_db()

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        if user is None:
            error = 'Incorrect Credentials.'
        elif not check_password_hash(user[3], password):
            error = 'Incorrect Credentials.'
        if error is None:
            session.clear()
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            # user[3] is their password
            session['phone_no'] = user[4]
            session['dob'] = user[5]
            session['gender'] = user[6]
            if user[7] is None:
                session['profile_pic'] = 'img_6.png'
            else:
                session['profile_pic'] = user[7]
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['psw']
        repeatpsw = request.form['psw-repeat']
        user = Users(username, email, password, repeatpsw)
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif password != repeatpsw:
            error = 'Confirm Password has to be the same.'
        if error is None:
            try:
                with sqlite3.connect('database.db') as con:
                    con.execute("INSERT INTO user (username, email, password) VALUES (?, ?, ?)",
                                (user.get_username(), user.get_email(), generate_password_hash(user.get_psw())))
                    con.commit()
                con.close()
            except con.IntegrityError as e:
                error_message = str(e)
                if "username" in error_message:
                    error = f"Username '{username}' is already registered."
                elif "email" in error_message:
                    error = f"Email '{email}' is already registered."
            else:
                return redirect(url_for("login"))
    return render_template('signup.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view


@app.route('/blog')
def blog():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM blog ORDER BY rowid DESC")

    rows = cur.fetchall()
    con.close()

    return render_template('blog.html', rows=rows)


@app.route('/addblog', methods=['GET', 'POST'])
@login_required
def addblog():
    form = BlogForm()
    poster = session['username']
    if request.method == 'POST':
        title = request.form['title']
        summary = request.form['summary']
        description = request.form['description']
        blog_pic = request.files['blog_pic']
        pic_filename = secure_filename(blog_pic.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        saver = request.files['blog_pic']
        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("INSERT INTO blog (username, title, summary, blog_pic, description) VALUES (?,?,?,?,?)",
                        (poster, title, summary, pic_name, description))

            con.commit()

            print("SUCCESSFUL")
        con.close()
        return redirect(url_for('blog'))

    else:
        return render_template('addblog.html', form=form)


@app.route('/editblog/<int:id>', methods=['GET', 'POST'])
@login_required
def editblog(id):
    form = BlogForm()
    poster = session['username']

    if request.method == 'POST':
        # Retrieve updated values from form fields
        new_title = request.form['title']
        new_summary = request.form['summary']
        new_description = request.form['description']

        if request.files['blog_pic']:
            # Save uploaded image in a specific folder
            blog_pic = request.files['blog_pic']
            pic_filename = secure_filename(blog_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            saver = request.files['blog_pic']
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

            # Remove previous image from folder
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute('SELECT blog_pic FROM blog where rowid = ?', (id,))
                blog_pic = cur.fetchone()
                for pic in blog_pic:
                    location = 'static/img/'
                    path = os.path.join(location, pic)
                    os.remove(path)

                # Update blog details in the database
                cur.execute(
                    "UPDATE blog SET username = ?, title = ?, summary = ?, blog_pic = ?, description = ?, datetime = CURRENT_TIMESTAMP WHERE rowid = ?",
                    (poster, new_title, new_summary, pic_name, new_description, id))
                con.commit()

            con.close()
            return redirect(url_for('blog'))
        else:
            # Update blog details in the database without changing the image
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE blog SET username = ?, title = ?, summary = ?, description = ?, datetime = CURRENT_TIMESTAMP WHERE rowid = ?",
                    (poster, new_title, new_summary, new_description, id))

                con.commit()

            con.close()
            return redirect(url_for('blog'))
    else:
        # Retrieve blog details from the database
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM blog WHERE rowid = ?", (id,))
        userblogs = cur.fetchall()
        con.commit()
        con.close()

        return render_template('editblog.html', userblogs=userblogs, id=id, form=form)


@app.route('/deleteblog/<int:id>')
@login_required
def deleteblog(id):
    # Connect to database
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    # Retrieve the blog post's picture filename
    cur.execute('SELECT blog_pic FROM blog where rowid = ?', (id,))
    blog_pic = cur.fetchone()
        # Delete the picture from the directory
    for pic in blog_pic:
        location = 'static/img/'
        path = os.path.join(location, pic)
        try:
            os.remove(path)
        except OSError as e:
            if e.errno and e.errno == 2: # File not found error
                cur.execute("DELETE FROM blog WHERE rowid = ?", (id,))
                con.commit()
                return redirect(url_for('blog'))
            else:
                cur.execute("DELETE FROM blog WHERE rowid = ?", (id,))
                con.commit()    # Delete the blog post from the database
                return redirect(url_for('blog'))


@app.route('/admindashboard')
@login_required
def dashbboard():
    return render_template('admindashboard.html')


@app.route('/users')
@login_required
def users():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM user")

    rows = cur.fetchall()
    con.close()

    return render_template('users.html', rows=rows)


@app.route('/delete_user/<int:user_id>/<user>')
@login_required
def delete_user(user_id, user):
    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("DELETE FROM blog WHERE username = ?", (user,))
        cur.execute("DELETE FROM user WHERE user_id = ?", (user_id,))
        con.commit()
        con.close()
    except:
        msg = 'An Error has occurred!'
        flash(msg)
        return redirect(url_for('users'))
    finally:
        msg = f'User {user} has been deleted!'
        flash(msg)
        return redirect(url_for('users'))


@app.route('/forms')
@login_required
def forms():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM tradeinentries")
    rows = cur.fetchall()
    con.close()
    return render_template('forms.html', rows=rows)


@app.route('/approveform/<form_id>')
@login_required
def approveform(form_id):
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('UPDATE tradeinentries SET status = ? WHERE tradein_id = ?', (1, form_id))
        con.commit()
    con.close()
    return redirect(url_for('forms'))


@app.route('/rejectform/<form_id>')
@login_required
def rejectform(form_id):
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('UPDATE tradeinentries SET status = ? WHERE tradein_id = ?', (0, form_id))
        con.commit()
    con.close()
    return redirect(url_for('forms'))


@app.route('/retrieveform/<id>/<user>')
def retrieveform(id, user):
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('SELECT rowid, * FROM tradeinform WHERE tradein_id = ?', (id,))
    rows = cur.fetchall()
    cur.execute('SELECT rowid, * FROM user WHERE username = ?', (user,))
    user = cur.fetchall()
    con.close()
    return render_template('retrieveform.html', rows=rows, id=id, user=user)


@app.route('/admin_inventory')
@login_required
def admin_inventory():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM inventory GROUP BY product_name")
    rows = cur.fetchall()

    con.close()

    return render_template('admin_inventory.html', rows=rows)


@app.route('/add_inventory', methods=['GET', 'POST'])
@login_required
def add_inventory():
    form = ProductForm()
    if request.method == 'POST':
        try:
            shop = request.form['shop']
            product_name = request.form['product_name']
            product_price = request.form['product_price']
            product_image = request.files['product_image']
            product_description = request.form['product_description']
            product_size = request.form.getlist('product_size')
            product_quantity = request.form['product_quantity']

            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                for size in product_size:
                    cur.execute('INSERT INTO inventorysize (product_name, product_size) VALUES (?,?)',
                                (product_name, size))
                    con.commit()

                pic_filename = secure_filename(product_image.filename)
                if pic_filename != '':
                    pic_name = str(uuid.uuid1()) + "_" + pic_filename
                    saver = product_image
                    saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                    product_id, price_id = create_product_and_price(product_name, product_price, 'sgd', pic_name,
                                                                    product_quantity, product_size)
                    cur.execute(
                        "INSERT INTO inventory (shop, product_name, product_price, product_image, product_description, product_quantity, product_id, price_id) VALUES (?,?,?,?,?,?,?,?)",
                        (shop, product_name, product_price, pic_name, product_description, product_quantity, product_id,
                         price_id))
                    con.commit()

                # for colour in product_colour:
                #     cur.execute('INSERT INTO inventorycolour (product_name, product_colour) VALUES (?,?)',
                #                 (product_name, colour))
                #     con.commit()
            con.close()

        except:
            msg = 'An error has occurred, please try again.'
            flash(msg)
            return redirect(url_for('admin_inventory'))
        finally:
            return redirect(url_for('admin_inventory'))
    return render_template('add_inventory.html', form=form)


@app.route('/admin_product/<product_name>')
@login_required
def admin_product(product_name):
    try:
        with sqlite3.connect('database.db') as con:
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute('SELECT rowid, * FROM inventory WHERE product_name = ?', (product_name,))
            rows = cur.fetchall()
            cur.execute('SELECT rowid, * FROM inventorysize WHERE product_name = ?', (product_name,))
            sizes = cur.fetchall()
            cur.execute('SELECT rowid, * FROM reviews WHERE product_name = ?', (product_name,))
            reviews = cur.fetchall()
        con.close()
    except:
        msg = 'An error has occurred, please try again.'
        flash(msg)
        return redirect(url_for('admin_inventory'))
    finally:
        return render_template('admin_product.html', rows=rows, sizes=sizes, reviews=reviews)


@app.route('/delete_inventory/<product_name>')
@login_required
def delete_inventory(product_name):
    try:
        with sqlite3.connect('database.db') as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute('SELECT product_image FROM inventory WHERE product_name = ?', (product_name,))
            images = cur.fetchall()
            for pic in images:
                location = 'static/img/'
                path = os.path.join(location, pic['product_image'])
                os.remove(path)
            cur.execute("DELETE FROM inventory WHERE product_name = ?", (product_name,))
            cur.execute("DELETE FROM inventorysize WHERE product_name = ?", (product_name,))
            cur.execute("DELETE FROM wishlist WHERE product_name = ?", (product_name,))
            cur.execute("DELETE FROM reviews WHERE product_name = ?", (product_name,))
            con.commit()
        con.close()
    except:
        msg = 'An Error hac occurred!'
        flash(msg)
        return redirect(url_for('admin_inventory'))
    finally:
        return redirect(url_for('admin_inventory'))


@app.route('/edit_inventory/<product_name>', methods=['GET', 'POST'])
@login_required
def edit_inventory(product_name):
    form = ProductForm()
    if request.method == 'POST':
        new_product_name = request.form['product_name']
        product_price = request.form['product_price']
        product_quantity = request.form['product_quantity']
        if request.form['product_description']:
            product_description = request.form['product_description']
            try:
                with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute(
                        "UPDATE inventory SET product_name = ?, product_price = ?, product_description = ?, product_quantity = ? WHERE product_name = ?",
                        (new_product_name, product_price, product_description, product_quantity, product_name))
            except:
                msg = 'Error in updating inventory'
                flash(msg)
                return redirect(url_for('admin_inventory'))
            finally:
                return redirect(url_for('admin_inventory'))
        else:
            try:
                with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute(
                        "UPDATE inventory SET product_name = ?, product_price = ?, product_quantity = ? WHERE product_name = ?",
                        (new_product_name, product_price, product_quantity, product_name))
            except:
                msg = 'Error in updating inventory'
                flash(msg)
                return redirect(url_for('admin_inventory'))
            finally:
                return redirect(url_for('admin_inventory'))
    else:
        with sqlite3.connect('database.db') as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(
                'SELECT product_price, product_description, product_quantity FROM inventory WHERE product_name = ? GROUP BY product_name',
                (product_name,))
            rows = cur.fetchall()
            for row in rows:
                product_price = row[0]
                product_description = row[1]
                product_quantity = row[2]
    return render_template('edit_inventory.html', form=form, product_price=product_price,
                           product_description=product_description, product_quantity=product_quantity,
                           product_name=product_name)


"""
@app.route('/add_vouchers')
@login_required
def addvouchers():
    pass
    voucher1 = ['$5 OFF DELIVERY', 5, 'Minimum purchase of $30']
    voucher2 = ['$10 DISCOUNT', 10, 'Minimum purchase of $40']
    voucher3 = ['$15 DISCOUNT', 15, 'Minimum purchase of $50']
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM user")

    rows = cur.fetchall()
    con.close()
    return render_template('add_vouchers.html', voucher1=voucher1, voucher2=voucher2, voucher3=voucher3, rows=rows)
"""


@app.route('/add_vouchers')
@login_required
def addvouchers():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM user")

    rows = cur.fetchall()
    con.close()
    return render_template('add_vouchers.html', rows=rows)


@app.route('/retrieve_vouchers/<username>')
@login_required
def retrieve_vouchers(username):
    with sqlite3.connect('database.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT rowid, * FROM addvouchers WHERE username = ?", (username,))

        rows = cur.fetchall()
        con.commit()
    con.close()
    return render_template('retrieve_vouchers.html', rows=rows, username=username)


@app.route('/delete_vouchers/<code>')
@login_required
def delete_vouchers(code):
    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("DELETE FROM addvouchers WHERE code = ?", (code,))  # addvouchers is a table
        con.commit()
        con.close()
    except:
        msg = 'An Error has occurred!'
        flash(msg)
        return redirect(url_for('addvouchers'))
    finally:
        msg = f'Voucher has been deleted!'
        flash(msg)
        return redirect(url_for('addvouchers'))


@app.route('/create_vouchers', methods=['GET', 'POST'])
@login_required
def create_vouchers():
    form = VoucherForm()
    with sqlite3.connect('database.db') as con:
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT rowid, * FROM user")
        users = cur.fetchall()
        if request.method == 'POST':
            username = request.form['user']
            voucher_name = request.form['voucher_name']
            discount = request.form['discount']
            condition = request.form['condition']
            with sqlite3.connect('database.db') as con:
                # def secure_rand(len=8):
                #     token = os.urandom(len)
                #     return base64.b64encode(token)
                voucher_code = str(shortuuid.uuid())
                cur = con.cursor()
                cur.execute("INSERT INTO addvouchers (username, title, value, condition, code) VALUES (?,?,?,?,?)",
                            (username, voucher_name, discount, condition, voucher_code))
                con.commit()

            con.close()
            msg = f"Voucher of {voucher_name} has been added to {username}'s account"
            flash(msg)
            return redirect(url_for('addvouchers'))
    return render_template('create_vouchers.html', form=form, users=users)


@app.route('/update_vouchers/<code_name>', methods=['GET', 'POST'])  # <code_name> is to pass in parameter
@login_required
def update_vouchers(code_name):
    form = VoucherForm()
    if request.method == 'POST':  # check if form is posted
        title = request.form['voucher_name']  # Get information from form
        value = request.form['discount']
        if request.form['condition']:  # If statement to check if data is passed in
            condition = request.form['condition']
            try:
                with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute(
                        "UPDATE addvouchers SET title = ?, value = ?, condition = ? WHERE code = ?",
                        (title, value, condition, code_name))  # Use from 705-707
            except:
                msg = 'Failed to change code'
                flash(msg)
                return redirect(url_for('addvouchers'))
            finally:
                return redirect(url_for('addvouchers'))
        else:
            try:
                with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute(
                        "UPDATE addvouchers SET title = ?, value = ? WHERE code = ?",
                        (title, value, code_name))
            except:
                msg = 'Failed to change code'
                flash(msg)
                return redirect(url_for('addvouchers'))
            finally:
                return redirect(url_for('addvouchers'))
    with sqlite3.connect('database.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            'SELECT title, value FROM addvouchers WHERE code = ?',
            (code_name,))  # code_name is the passed in argument
        rows = cur.fetchall()
        for row in rows:
            voucher_name = row[0]
            discount = row[1]
    return render_template('update_vouchers.html', form=form, voucher_name=voucher_name, discount=discount,
                           code_name=code_name)  # form=form passes in into updatevoucher.html


"""
def edit_inventory(product_name):
    form = ProductForm()
    if request.method == 'POST':
        new_product_name = request.form['product_name']
        product_price = request.form['product_price']
        product_quantity = request.form['product_quantity']
        if request.form['product_description']:
            product_description = request.form['product_description']
            try:
                with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute(
                        "UPDATE inventory SET product_name = ?, product_price = ?, product_description = ?, product_quantity = ? WHERE product_name = ?",
                        (new_product_name, product_price, product_description, product_quantity, product_name))
            except:
                msg='Error in updating inventory'
                flash(msg)
                return redirect(url_for('admin_inventory'))
            finally:
                return redirect(url_for('admin_inventory'))
        else:
            try:
                with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute(
                        "UPDATE inventory SET product_name = ?, product_price = ?, product_quantity = ? WHERE product_name = ?",
                        (new_product_name, product_price, product_quantity, product_name))
            except:
                msg='Error in updating inventory'
                flash(msg)
                return redirect(url_for('admin_inventory'))
            finally:
                return redirect(url_for('admin_inventory'))
    else:
        with sqlite3.connect('database.db') as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute('SELECT product_price, product_description, product_quantity FROM inventory WHERE product_name = ? GROUP BY product_name', (product_name,))
            rows = cur.fetchall()
            for row in rows:
                product_price = row[0]
                product_description = row[1]
                product_quantity = row[2]
    return render_template('edit_inventory.html', form=form, product_price=product_price, product_description=product_description, product_quantity=product_quantity, product_name=product_name)
"""


# @app.route('/voucher/<username>/<int:voucher>')
# @login_required
# def voucher(username, voucher):
#     vouchers = [('$5 OFF DELIVERY', 5, 'Minimum purchase of $30'), ('$10 DISCOUNT', 10, 'Minimum purchase of $40'),
#                 ('$15 DISCOUNT', 15, 'Minimum purchase of $50')]
#
#     with sqlite3.connect('database.db') as con:
#         def secure_rand(len=8):
#             token = os.urandom(len)
#             return base64.b64encode(token)
#
#         voucher_code = secure_rand()
#         cur = con.cursor()
#         cur.execute("INSERT INTO validvouchers (code) VALUES (?)", (voucher_code,))
#         cur.execute("INSERT INTO addvouchers (username, title, value, condition, code) VALUES (?,?,?,?,?)",
#                     (username, vouchers[voucher][0], vouchers[voucher][1], vouchers[voucher][2], voucher_code))
#         con.commit()
#
#     con.close()
#     msg = f"Voucher of {vouchers[voucher][0]} has been added to {username}'s account"
#     flash(msg)
#     return redirect(url_for('addvouchers'))


@app.route('/view_vouchers/<username>')
@login_required
def view_vouchers(username):
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM addvouchers WHERE username = ?", (username,))
    rows = cur.fetchall()
    con.close()
    return render_template('view_vouchers.html', rows=rows)


@app.route('/view_tradeins/<username>')
@login_required
def view_tradeins(username):
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT status FROM tradeinentries WHERE username = ?", (username,))
    rows = cur.fetchall()
    cur.execute("SELECT rowid, * FROM tradeinform WHERE username = ? GROUP BY tradein_id", (username,))
    tradeins = cur.fetchall()
    con.close()
    return render_template('view_tradeins.html', rows=rows, tradeins=tradeins)


@app.route('/user_retrieveform/<tradein_id>')
@login_required
def user_retrieveform(tradein_id):
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('SELECT rowid, * FROM tradeinform WHERE tradein_id = ?', (tradein_id,))
    rows = cur.fetchall()
    cur.execute('SELECT rowid, * FROM tradeinform WHERE tradein_id = ?', (tradein_id,))
    rows = cur.fetchall()

    con.close()
    return render_template('user_retrieveform.html', rows=rows)


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/tradein')
def tradein():
    with sqlite3.connect('database.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('SELECT rowid, * FROM inventory WHERE shop = ? GROUP BY product_name', ('Trade-In',))
        rows = cur.fetchall()
    con.close()
    return render_template('tradein.html', rows=rows)


@app.route('/tradeinno', methods=['GET', 'POST'])
@login_required
def tradeinno():
    form = TradeInForm()
    if request.method == 'POST':
        no_of_clothes = int(request.form['no_of_clothes'])
        return render_template('tradeinform.html', no_of_clothes=no_of_clothes, form=form)
    return render_template('tradeinno.html', form=form)


@app.route('/tradeinform/<int:id>', methods=['GET', 'POST'])
@login_required
def tradein_form(id):
    form = TradeInForm()
    username = session['username']
    if request.method == 'POST':
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            tradein_pic = request.files.getlist('tradein_pic')
            descriptions = request.form.getlist('description')
            tradeinid = Tradeinform()
            tradein_id = str(tradeinid.generate_uuid())
            tradein_id = tradein_id[:8]
            cur.execute(
                "INSERT INTO tradeinentries (username, no_of_clothes, tradein_id) VALUES (?,?,?)",
                (username, id, tradein_id))
            con.commit()

            for i in range(id):
                pic = tradein_pic[i]
                description = descriptions[i]
                pic_filename = secure_filename(pic.filename)
                pic_name = str(uuid.uuid1()) + "_" + pic_filename
                saver = tradein_pic[i]
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

                cur.execute(
                    "INSERT INTO tradeinform (username, no_of_clothes, tradein_pic, description, tradein_id) VALUES (?,?,?,?,?)",
                    (username, id, pic_name, description, tradein_id))
                con.commit()

        con.close()
        return redirect(url_for('tradein'))

    return render_template('tradeinform.html', form=form)


@app.route('/deletetradein/<id>')
def deletetradein(id):
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT tradein_pic FROM tradeinform WHERE tradein_id = ?", (id,))
    tradein_pic = cur.fetchall()
    for picture in tradein_pic:
        location = "static/img/"
        path = os.path.join(location, picture['tradein_pic'])
        os.remove(path)
    cur.execute("DELETE FROM tradeinform WHERE tradein_id = ?", (id,))
    cur.execute('DELETE FROM tradeinentries WHERE tradein_id = ?', (id,))
    con.commit()
    con.close()
    return redirect(url_for('forms'))


@app.route('/eco')
def eco():
    with sqlite3.connect('database.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('SELECT rowid, * FROM inventory WHERE shop = ? GROUP BY product_name', ('Eco',))
        rows = cur.fetchall()
    con.close()

    return render_template('eco.html', rows=rows)


@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
    error = None
    form = UserForm()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone_no = request.form['phone_no']
        dob = request.form['dob']
        gender = None
        if request.form['gender']:
            gender = request.form['gender']
            session['gender'] = gender
        session['username'] = username
        session['email'] = email
        if len(phone_no) == 8 and phone_no.isdigit():
            session['phone_no'] = phone_no
        else:
           error = "Invalid phone number"
        if request.form['dob'] == '':
            session['dob'] = None
        else:
            session['dob'] = dob
        if error is None:
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE user SET username = ?, email = ?, phone_no = ?, dob = ?, gender = ? WHERE username = ?",
                    (username, email, phone_no, dob, gender, session['username']))

                con.commit()

            con.close()
        return redirect(url_for('profile'))
    else:
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM user WHERE username = ?', (session['username'],))
            details = cur.fetchone()
    return render_template('editprofile.html', form=form, details=details)


@app.route('/editprofilepic/<username>', methods=['GET', 'POST'])
@login_required
def editprofilepic(username):
    form = UserForm()
    if request.method == 'POST':
        profile_pic = request.files['profile_pic']
        pic_filename = secure_filename(profile_pic.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        saver = request.files['profile_pic']
        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        if session['profile_pic'] != 'img_6.png':
            location = 'static/img/'
            path = os.path.join(location, session['profile_pic'])
            os.remove(path)
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('UPDATE user SET profile_pic = ? WHERE username = ?', (pic_name, username))
            cur.close()
        session['profile_pic'] = pic_name
        return redirect(url_for('profile'))
    else:

        return render_template('editpfp.html', form=form)


@app.route('/add_to_cart/<product_name>/<username>')
def add_to_cart(product_name, username):
    try:
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("INSERT INTO cart (username, product_name) VALUES (?, ?)", (username, product_name))
    except:
        msg = 'An Error has occurred'
        flash(msg)
        return redirect(url_for('shop'))
    finally:
        msg = 'Added to cart'
        flash(msg)
        return redirect(url_for('eco'))


@app.route('/cart/<username>')
@login_required
def cart(username):
    try:
        product_list = []
        rows = []
        lists = []
        total = 0
        with sqlite3.connect('database.db') as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT product_name FROM cart WHERE username = ?", (username,))
            products = cur.fetchall()
            for product in products:
                product_list.append(product['product_name'])

            for l in product_list:
                cur.execute("SELECT rowid, * FROM inventory WHERE product_name = ? GROUP BY product_name", (l,))
                row = cur.fetchall()
                rows.append(row)

            for i in rows:
                list_1 = {
                    'name': i[0][1],
                    'price': i[0][2],
                    'image': i[0][3],
                }
                total = total + i[0][2]
                lists.append(list_1)

            cur.execute("SELECT rowid, * FROM addvouchers WHERE username = ?", (username,))
            vouchers = cur.fetchall()
    except:
        msg = 'An Error has occurred'
        flash(msg)
        return redirect(url_for('shop'))
    finally:
        return render_template('cart.html', products=products, rows=rows, lists=lists, total=total, vouchers=vouchers)


@app.route('/delete_cart/<product_name>/<username>')
@login_required
def delete_cart(product_name, username):
    try:
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('DELETE FROM cart WHERE username = ? AND product_name = ?', (username, product_name))
            con.commit()
        con.close()
    except:
        msg = 'An Error has occurred'
        flash(msg)
        return redirect(url_for('cart', username=username))
    finally:
        return redirect(url_for('cart', username=username))


@app.get("/chatbot")
def index_get():
    return render_template("chatbot.html")


@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)


if __name__ == '__main__':
    app.run(debug=True)
