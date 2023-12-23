import os
import uuid
from datetime import date, datetime
import functools

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
UPLOAD_FOLDER = 'static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db.init_app(app)


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
    profile_pic = FileField("Profile Picture")
    submit = SubmitField("Submit")


class TradeInForm(FlaskForm):
    no_of_clothes = SelectField("Number Of Clothes", choices=[1, 2, 3, 4, 5, 6], validators=[DataRequired()])
    tradein_pic = FileField("Picture Of Clothing Item", validators=[DataRequired()])
    description = TextAreaField("Description Of Clothing Item", validators=[DataRequired()])
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
                cur.execute('SELECT blog_pic FROM blog where rowid = ?', (id,))
                blog_pic = cur.fetchone()
                for pic in blog_pic:
                    location = 'static/img/'
                    path = os.path.join(location, pic)
                    os.remove(path)
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
    cur.execute('SELECT blog_pic FROM blog where rowid = ?', (id,))
    blog_pic = cur.fetchone()
    for pic in blog_pic:
        location = 'static/img/'
        path = os.path.join(location, pic)
        os.remove(path)
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


@app.route('/deleteuser/<int:id>')
@login_required
def deleteuser(id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("DELETE FROM user WHERE rowid = ?", (id,))
    con.commit()
    con.close()
    return redirect(url_for('users'))


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/tradein')
def tradein():
    return render_template('tradein.html')


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
def tradeinform(id):
    form = TradeInForm()
    if request.method == 'POST':
        username = session['username']
        tradein_pic = request.files['tradein_pic']
        description = request.form['description']
        return render_template('tradein.html', tradein_pic=tradein_pic, description=description)
        # with sqlite3.connect('database.db') as con:
        #     cur = con.cursor()
        #     for i in range(no_of_clothes):
        #         for l in tradein_pic:
        #             cur.execute("INSERT INTO tradeinform (username, no_of_clothes, tradein_pic, description) VALUES (?,?,?,?)", (username, no_of_clothes, l, ))
        #
        #             con.commit()
        #             con.close()
    return render_template('tradeinform.html', form=form)


@app.route('/eco')
def eco():
    return render_template('eco.html')


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


# if request.files['profile_pic']:
#     profile_pic = request.files['profile_pic']
#     pic_filename = secure_filename(profile_pic.filename)
#     pic_name = str(uuid.uuid1()) + "_" + pic_filename
#     saver = request.files['profile_pic']
#     saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
# else:
#     pic_name = 'img_6.png'
@app.route('/cart')
def cart():
    return render_template('cart.html')


if __name__ == '__main__':
    app.run(debug=True)
