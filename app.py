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

load_dotenv()

# Configure app
app = Flask(__name__)
app.config['DEBUG'] = True  # Enable debug mode


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.getenv("SECRET_KEY")

Session(app)


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

with app.app_context():
    print("Creating tables...")
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

@app.route("/")
# TODO make login required
def index():
    """Show each section overview, homepage"""
    return render_template("index.html")

@app.route("/login")
def login():
    # Forget user info
    session.clear()

    if request.method == "POST":
        

    return render_template("login.html")

@app.route("/signup", methods = ["GET", "POST"])
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

        if check_spaces(username):
            flash("Spaces not allowed in username", "danger")
            return redirect("/signup")
        
        if check_spaces(password):
            flash("Spaces not allowed in password", "danger")
            return redirect("/signup")
        
        if password != confirm:
            flash("Passwords don't match", "danger")
            return redirect("/signup")
        
        if len(password) < 10:
            flash("Password length must be 10+", "danger")
            return redirect("/signup")
        
        try:
            user = User(name=name, username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            flash("Registration success!")
            return redirect("/")
        
        except IntegrityError:
            flash("Username already exists, try logging in instead")
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