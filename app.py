import os
import uuid
from datetime import date, datetime
import functools

from flask import Flask, render_template, request, redirect, url_for, Blueprint, flash, g, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, logout_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import Length, ValidationError, DataRequired
import sqlite3
import stripe


app = Flask(__name__)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'sbufbv8829gf2k'
UPLOAD_FOLDER = 'static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db.init_app(app)
# Secret API key
stripe.api_key = 'sk_test_51OPSVaIGppHzuUaIImziYC43tisQhhhwNwjgcFtY1yltxTHYQrQRykjkHpBpGEHaUwmAH7Dbb3RwhuhZhMqztw1S00d7rsLUVF'
YOUR_DOMAIN = 'http://127.0.0.1:5000/'

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


bp = Blueprint('auth', __name__, url_prefix='/auth')


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String[20], nullable=False, unique=True)
    email = db.Column(db.String[50], nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String(), nullable=True)


class BlogForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    summary = StringField('Summary', validators=[Length(min=1, max=150), DataRequired()])
    blog_pic = FileField("Blog Photo")
    description = StringField('Blog away...', validators=[Length(min=50, max=800), DataRequired()])
    submit = SubmitField("Submit")


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    title = db.Column(db.String(255))
    summary = db.Column(db.Text)
    blog_pic = db.Column(db.String(), nullable=True)
    description = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)


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
            return redirect(url_for('home'))

    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['psw']
        repeatpsw = request.form['psw-repeat']
        db = get_db()
        error = None
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
        flash(error)
    return render_template('signup.html')


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
    cur.execute("SELECT rowid, * FROM blog")

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
        new_title = request.form['title']
        new_summary = request.form['summary']
        new_description = request.form['description']
        if request.files['blog_pic']:
            blog_pic = request.files['blog_pic']
            pic_filename = secure_filename(blog_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            saver = request.files['blog_pic']
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("UPDATE blog SET username = ?, title = ?, summary = ?, blog_pic = ?, description = ?, datetime = CURRENT_TIMESTAMP WHERE rowid = ?", (poster, new_title, new_summary, pic_name, new_description, id))

                con.commit()

            con.close()
            return redirect(url_for('blog'))
        else:
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE blog SET username = ?, title = ?, summary = ?, description = ?, datetime = CURRENT_TIMESTAMP WHERE rowid = ?",
                    (poster, new_title, new_summary, new_description, id))

                con.commit()

            con.close()
            return redirect(url_for('blog'))
    else:
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
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("DELETE FROM blog WHERE rowid = ?", (id,))
    con.commit()
    con.close()
    return redirect(url_for('blog'))


@app.route('/admindashboard')
def dashbboard():
    return render_template('admindashboard.html')


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/tradein')
def tradein():
    return render_template('tradein.html')


@app.route('/tradeinform')
@login_required
def tradeinform():
    return render_template('tradeinform.html')


@app.route('/eco')
def eco():
    return render_template('eco.html')


@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route("/create-checkout-session", methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': '{{PRICE_ID}}',
                    'quantity': 1,
                },
            ],
            mode='payment',
            ui_mode='embedded',
            return_url=YOUR_DOMAIN + '/return'
        )
    except Exception as e:
        return str(e)

    return jsonify(clientSecret=session.client_secret)


if __name__ == '__main__':
    app.run(debug=True)

if __name__ == "__main__":
    app.run(port=5000)
