import os

from flask import Flask, flash, get_flashed_messages, redirect, render_template, url_for, request, session, g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import dotenv_values


# Configure app
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# TODO Set secret key
Session(app)


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
    return render_template("login.html")
