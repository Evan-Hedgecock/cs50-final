import os

from flask import Flask, flash, get_flashed_messages, redirect, render_template, url_for, request, session, g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv_vault import load_dotenv
import sqlalchemy as sa
from sqlalchemy import Integer, String, insert, select
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.exc import IntegrityError
from typing import List

from helpers import login_required, usd, percent, decimal

load_dotenv()

# Configure app
app = Flask(__name__)
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["percent"] = percent
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

# class User(db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str]
#     username: Mapped[str] = mapped_column(unique=True)
#     password: Mapped[str]
#     loans: Mapped[List['Loans']] = relationship('Loans', back_populates='user', cascade='all, delete-orphan')

# class Loans(db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str]
#     amount: Mapped[int]
#     interest: Mapped[int]
#     principal: Mapped[int]
#     user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
#     user: Mapped['User'] = relationship('User', back_populates='loans')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    loans = relationship('Loans', back_populates='user', cascade='all, delete-orphan')

class Loans(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    interest = db.Column(db.Integer, nullable=False)
    monthly_interest = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship('User', back_populates='loans')

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

@app.route("/manage-loans", methods=["GET"])
@login_required
def manage_loans():
    set_form_name("s-m")
    if request.method == "GET":
        loans = db.session.scalars(select(Loans).where(Loans.user_id == session["user_id"])).all()
        total = 0
        interest = 0

        for loan in loans:
            total += loan.amount
            interest += loan.monthly_interest

        return render_template("manage-loans.html", loans=loans, usd=usd, percent=percent, decimal=decimal, total=total, interest=interest)


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
    set_form_name("login-form")
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

@app.route("/account", methods=["GET"])
@login_required
def account():
    name = get_name(session["user_id"])
    username = get_username(session["user_id"])
    return render_template("account.html", name=name, username=username)

@app.route("/update-password", methods=["POST"])
@login_required
def update_password():
    flash("Password updated", "success")
    set_form_name("update-password-form")
    return redirect("/account")

@app.route("/update-username", methods=["POST"])
@login_required
def update_username():
    flash("Username updated", "success")
    set_form_name("update-username-form")
    return redirect("/account")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    session.clear()
    set_form_name("signup-form")

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

@app.route("/add-loan", methods=["POST", "GET"])
def add_loan():

    if request.method == "POST":
        loan = get_loan("add", session["user_id"])
        set_form_name("add-loan-form")
        print("Session form_name:", session["form_name"])
        if isinstance(loan, Loans):
            db.session.add(loan)
            db.session.commit()
            flash("Loan added successfully!", "success")
            return redirect("/manage-loans")
        else:
            url = loan
            return redirect(url)
    
    else:
        loans = get_loans(session["user_id"])
        return render_template("manage-loans-add-form.html", usd=usd, loans=loans, percent=percent, total=get_total(loans), interest=get_interest(loans), decimal=decimal)


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

def get_loans(user_id):
    loans = db.session.scalars(select(Loans).where(Loans.user_id == user_id)).all()
    return loans

def get_total(loans):
    total = 0

    for loan in loans:
        total += loan.amount
    
    return total

def get_interest(loans):
    interest = 0
    for loan in loans:
        interest += loan.monthly_interest
    
    return interest

def get_loan(form, user_id):
    response = "/" + form + "-loan"
    responding = True
    while responding:            
        if not request.form.get(form + "-name") or not request.form.get(form + "-amount") or not request.form.get(form + "-interest"):
            flash("All fields required", "danger")
            responding = False
            break
            
        name = request.form.get(form + "-name")
        amount = request.form.get(form + "-amount")
        interest = request.form.get(form + "-interest")

        try:
            amount = int(amount)
            interest = int(interest)
            monthly_interest = ((amount * (interest / 100)) / 12)
        
        except ValueError:
            if type(amount) != int:
                flash("Enter dollar amount of loan", "danger")  
                responding = False              
                break            
            if type(interest) != int:
                flash("Enter interest percentage of loan", "danger")
                responding = False
                break 
            else:
                flash("Unexpected input value", "danger")
                responding = False
                break
        
        loan = Loans(name=name, amount=amount, interest=interest, monthly_interest=monthly_interest, user_id=user_id)
        response = loan
        responding = False
        break
    return response

def set_form_name(form_name):
    session["form_name"] = form_name