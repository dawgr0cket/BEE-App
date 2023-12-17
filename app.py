from flask import Flask, render_template, request, redirect, url_for
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
    return render_template('home.html')


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)


@app.route('/signup')
def signup():
    form = Signupform()
    return render_template('signup.html', form=form)


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


if __name__ == '__main__':
    app.run(debug=True)
