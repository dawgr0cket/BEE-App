import functools

from flask import Flask, render_template, request, redirect, url_for, Blueprint, flash, g, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, logout_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import sqlite3


app = Flask(__name__)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'sbufbv8829gf2k'
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


bp = Blueprint('auth', __name__, url_prefix='/auth')


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String[20], nullable=False, unique=True)
    email = db.Column(db.String[50], nullable=False)
    password = db.Column(db.String[80], nullable=False)
    date_added = db.Column(db.DateTime, default='utf-8')
    password_hash = db.Column(db.String(128))


class Signupform(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholders": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=80)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        existing_username = Users.query.filter_by(username=username.data).first()
        if existing_username:
            raise ValidationError("That username already exists.")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholders": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=80)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

class BlogForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    submit = SubmitField("Submit")



@app.route('/')
def home():
    if 'adminappdev' in session.values():
        return render_template('admindashboard.html')
    # elif 'username' in session:
    #     return f'Welcome, {session["username"]}!'

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
    if request.method == "POST":
        try:
            title = request.form['title']
            summary = request.form['summary']
            files = request.form['files']
            description = request.form['description']
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO blog (title, summary, files, description) VALUES (?,?,?,?)",(title, summary, files, description))

                con.commit()
        except:
            con.rollback()
        finally:
            con.close()
            return redirect(url_for('blog'))
    else:
        return render_template('addblog.html')


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


if __name__ == '__main__':
    app.run(debug=True)

