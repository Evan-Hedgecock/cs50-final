import os

from flask import Flask, flash, get_flashed_messages, redirect, render_template, url_for, request, session, g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv_vault import load_dotenv
import sqlalchemy as sa
from sqlalchemy import Integer, String, insert, select
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import IntegrityError

from helpers import login_required

load_dotenv()

# Configure app
app = Flask(__name__)
app.config['DEBUG'] = True  # Enable debug mode


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.getenv("SECRET_KEY")

Session(app)

if __name__ == "__main__":
    app.run(debug=True)

# Configure SQL database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wisp.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

class Loans(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    amount: Mapped[int]
    interest: Mapped[int]
    principal: Mapped[int]


with app.app_context():
    db.create_all()
    
@app.before_request
def before_request():
    session.modified = True
    g.flashed_messages = get_flashed_messages(with_categories=True)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show each section overview, homepage"""
    if request.method == "GET":
        name = get_name(session["user_id"])
    return render_template("index.html", name=name)

@app.route("/loans", methods=["GET", "POST"])
@login_required
def loans():
    return render_template("loans.html")

@app.route("/manage-loans", methods=["GET", "POST"])
@login_required
def loans_manage():
    if request.method == "GET":
        
        return render_template("manage-loans.html")


@app.route("/budget", methods=["GET", "POST"])
@login_required
def budget():
    return render_template("budget.html")

@app.route("/progress", methods=["GET", "POST"])
@login_required
def progress():
    return render_template("progress.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    print(f"Request method: {request.method}")
    if request.method == "POST":
        
        if not request.form.get("username"):
            flash("Enter username", "danger")
            return redirect("/login")
        elif not request.form.get("password"):
            flash("Enter password", "danger")
            return redirect("/login")
        
        username = request.form.get("username")
        entered_password = request.form.get("password")
        result = db.session.execute(select(User).where(User.username == username))
        copies = 0
        username_real = False
        for user_obj in  result.scalars():
            if username == user_obj.username:
                # Username exists
                username_real = True
                copies += 1
        if not username_real:
            flash("Username doesn't exist", "danger")
            return redirect("/login")
        hash = db.session.scalar(select(User.password).where(User.username == username))

        if username_real and copies == 1 and check_password_hash(hash, entered_password):
            session["user_id"] = db.session.scalar(select(User.id).where(User.username == username and User.password == hash))
            flash("Login success", "success")
            return redirect("/")
        else:
            flash("Password incorrect", "danger")
            return redirect("/login")

    else:
        return render_template("login.html")

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    name = get_name(session["user_id"])
    username = get_username(session["user_id"])
    if request.method == "GET":
        return render_template("account.html", name=name, username=username)

@app.route("/signup", methods=["GET", "POST"])
def signup():

    session.clear()

    if request.method == "POST":

        if not request.form.get("username") or not request.form.get("name") or not request.form.get("password") or not request.form.get("confirm"):
            flash("Please enter all fields", "danger")
            return redirect("/signup")
        
        username = request.form.get("username")
        name = request.form.get("name")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        name = name.capitalize()
        username = username.lower()

        if check_spaces(username):
            flash("Spaces not allowed in username", "danger")
            return redirect("/signup")
        
        if check_spaces(password):
            flash("Spaces not allowed in password", "danger")
            return redirect("/signup")
        
        if password != confirm:
            flash("Passwords don't match", "danger")
            return redirect("/signup")
        
        # if len(password) < 10:
        #     flash("Password length must be 10+", "danger")
        #     return redirect("/signup")
        
        try:
            user = User(name=name, username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            flash("Registration success!", "success")
            session["user_id"] = db.session.scalar(select(User.id).where(User.username == username))
            return redirect("/")
        
        except IntegrityError:
            flash("Username already exists, try logging in instead", "danger")
            return redirect("/login")

    return render_template("signup.html")

@app.route("/signout")
def signout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)



def check_spaces(string):
    if " " in string:
        return True
    else:
        return False
    

def get_name(user_id):
    name = db.session.execute(select(User.name).where(user_id == User.id)).scalar()
    return name

def get_username(user_id):
    username = db.session.execute(select(User.username).where(user_id == User.id)).scalar()
    return username