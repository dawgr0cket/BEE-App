import os
import uuid
import base64
import functools
import stripe
from tradeinform import Tradeinform
from flask import Flask, render_template, request, redirect, url_for, Blueprint, flash, g, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, logout_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, FileField, EmailField, IntegerField, DateField, RadioField, SelectField, TextAreaField
from wtforms.validators import Length, ValidationError, DataRequired
import sqlite3


app = Flask(__name__)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'sbufbv8829gf2k'
stripe.api_key = os.environ.get('sk_test_51OPSVaIGppHzuUaIImziYC43tisQhhhwNwjgcFtY1yltxTHYQrQRykjkHpBpGEHaUwmAH7Dbb3RwhuhZhMqztw1S00d7rsLUVF') # add in secret key
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51OPSVaIGppHzuUaIIJsjb08I1RVMYwSN1IinmZ5TcUrqhi1xSlFnDAlbW1hw046EfdSnCvneXtf6n3hVvFfTcDgX00WfET7pNV'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51OPSVaIGppHzuUaIImziYC43tisQhhhwNwjgcFtY1yltxTHYQrQRykjkHpBpGEHaUwmAH7Dbb3RwhuhZhMqztw1S00d7rsLUVF'


UPLOAD_FOLDER = 'static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db.init_app(app)


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'sgd',
                'product_data': {
                    'name': 'T-shirt',
                },
                'unit_amount': 2000,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('success', _external=True),
        cancel_url=url_for('cancel', _external=True),
    )
    return {'id': session.id}


@app.route('/success')
def success():
    return render_template('success.html')


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


class UserForm(FlaskForm):
    username = StringField("Username")
    email = EmailField('Email')
    phone_no = IntegerField("Phone Number", validators=[Length(min=8, max=8)])
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
        db = get_db()

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif password != repeatpsw:
            error = 'Confirm Password has to be the same.'
        if error is None:
            try:
                db.execute("INSERT INTO user (username, email, password) VALUES (?, ?, ?)", (username, email, generate_password_hash(password)))
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
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
            cur.execute("INSERT INTO blog (username, title, summary, blog_pic, description) VALUES (?,?,?,?,?)", (poster, title, summary, pic_name, description))

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
                cur.execute("UPDATE blog SET username = ?, title = ?, summary = ?, blog_pic = ?, description = ?, datetime = CURRENT_TIMESTAMP WHERE rowid = ?", (poster, new_title, new_summary, pic_name, new_description, id))
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
        os.remove(path)

    # Delete the blog post from the database
    cur.execute("DELETE FROM blog WHERE rowid = ?", (id,))
    con.commit()
    con.close()

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
            product_image = request.files.getlist('product_image')
            product_description = request.form['product_description']
            product_size = request.form.getlist('product_size')
            product_colour = request.form.getlist('product_colour')
            product_quantity = request.form['product_quantity']
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                for image in product_image:
                    pic = image

                    pic_filename = secure_filename(pic.filename)
                    if pic_filename != '':
                        pic_name = str(uuid.uuid1()) + "_" + pic_filename
                        saver = image
                        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

                        cur.execute(
                            "INSERT INTO inventory (shop, product_name, product_price, product_image, product_description, product_quantity) VALUES (?,?,?,?,?,?)",
                            (shop, product_name, product_price, pic_name, product_description, product_quantity))
                        con.commit()
                for size in product_size:
                    cur.execute('INSERT INTO inventorysize (product_name, product_size) VALUES (?,?)', (product_name, size))
                    con.commit()
                for colour in product_colour:
                    cur.execute('INSERT INTO inventorycolour (product_name, product_colour) VALUES (?,?)', (product_name, colour))
                    con.commit()
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
            cur.execute('SELECT rowid, * FROM inventorycolour WHERE product_name = ?', (product_name,))
            colours = cur.fetchall()
            cur.execute('SELECT rowid, * FROM reviews WHERE product_name = ?', (product_name,))
            reviews = cur.fetchall()
        con.close()
    except:
        msg = 'An error has occurred, please try again.'
        flash(msg)
        return redirect(url_for('admin_inventory'))
    finally:
        return render_template('admin_product.html', rows=rows, sizes=sizes, colours=colours, reviews=reviews)


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
            cur.execute("DELETE FROM inventorycolour WHERE product_name = ?", (product_name,))
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


@app.route('/voucher/<username>/<int:voucher>')
@login_required
def voucher(username, voucher):
    vouchers = [('$5 OFF DELIVERY', 5, 'Minimum purchase of $30'), ('$10 DISCOUNT', 10, 'Minimum purchase of $40'),
                ('$15 DISCOUNT', 15, 'Minimum purchase of $50')]

    with sqlite3.connect('database.db') as con:
        def secure_rand(len=8):
            token = os.urandom(len)
            return base64.b64encode(token)

        voucher_code = secure_rand()
        cur = con.cursor()
        cur.execute("INSERT INTO validvouchers (code) VALUES (?)", (voucher_code,))
        cur.execute("INSERT INTO addvouchers (username, title, value, condition, code) VALUES (?,?,?,?,?)",
                    (username, vouchers[voucher][0], vouchers[voucher][1], vouchers[voucher][2], voucher_code))
        con.commit()

    con.close()
    msg = f"Voucher of {vouchers[voucher][0]} has been added to {username}'s account"
    flash(msg)
    return redirect(url_for('addvouchers'))


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

                cur.execute("INSERT INTO tradeinform (username, no_of_clothes, tradein_pic, description, tradein_id) VALUES (?,?,?,?,?)", (username, id, pic_name, description, tradein_id))
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
        if request.form['phone_no'] == '':
            session['phone_no'] = None
        else:
            session['phone_no'] = phone_no
        if request.form['dob'] == '':
            session['dob'] = None
        else:
            session['dob'] = dob
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
        with sqlite3.connect('database.db') as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT product_name FROM cart WHERE = ?", (username,))
            products = cur.fetchall()
            for product in products:
                cur.execute("SELECT * FROM inventory WHERE product_name = ? GROUP BY product_name", (product,))
                row = cur.fetchall()
                product_list.append(row)
    except:
        msg = 'An Error has occurred'
        flash(msg)
        return redirect(url_for('shop'))
    finally:
        return render_template('cart.html', product_list=product_list)


@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


if __name__ == '__main__':
    app.run(debug=True)
