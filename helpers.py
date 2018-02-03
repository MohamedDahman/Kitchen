import csv
import urllib.request
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash


from flask import redirect, render_template, request, session
from functools import wraps


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///kitchen.db")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def apology(message, code=400):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def isUserExsist(userName):
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                      username=userName)
    # Ensure username exists and password is correct
    return len(rows)


def changeUserHash(currentUserId, newHash):
    rows = db.execute("update  users set hash = :newHash where id = :userId",
                      newHash=newHash, userId=currentUserId)
    return rows


def addUser(userName, userPassword):
    result = db.execute("INSERT INTO users (username , hash) VALUES (:username , :hash )",
                        username=userName,
                        hash=userPassword)
    if not result:
        return apology("something error when try to insert in DATABASE")
    else:
        rows = db.execute("SELECT id FROM users WHERE username = :username",
                          username=userName)
        session["user_id"] = rows[0]["id"]
    return 0

def isPasswordFormated(password):
    if len(password)<7:
        return False

    thereAreNum = 0
    thereAreUpperCase = 0
    thereAreLowerCase = 0
    for onechar in request.form.get("password"):
        if onechar.isdigit():
                thereAreNum = 1
        if onechar.isupper():
                thereAreUpperCase = 1
        if onechar.islower():
                thereAreLowerCase = 1
    if thereAreNum == 1 or thereAreUpperCase == 1 or thereAreLowerCase == 1 :
        return True
    else:
        return False


def getUserHash(currentUserId):
    rows = db.execute("select hash  from  users where id = :userId",
                      userId=currentUserId)
    userHash = rows[0]["hash"]
    return userHash

def changeUserCash(currentUserId, newCash):
    rows = db.execute("update  users set cash = :newCash where id = :userId",
                      newCash=newCash, userId=currentUserId)
    return rows

def mealProcess(mealId, community, userID):
    rows = db.execute("insert into  mealProcess (mealId, community, userId) values (:mealId, :community, :userId)",
                      mealId=mealId, community=community ,userId=userID)
    return rows





