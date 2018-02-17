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


def mealProcess(mealId, community, userID):
    rows = db.execute("insert into  mealProcess (mealId, community, userId) values (:mealId, :community, :userId)",
                      mealId=mealId, community=community ,userId=userID)
    return rows


def isParticipant(mealId, userID):
    rows = db.execute("select count(*) as Counts  from mealProcess where  mealId = :mealId and  userId = :userId",
                      mealId = mealId, userId=userID)
    return rows[0]["Counts"]


def getOwner(mealId):
        owner = db.execute("select users.username from  mealProcess , users   where mealId= :mealId and users.id = mealProcess.userId and community = 1 " , mealId = mealId)
        if len(owner) !=0 :
                return   owner[0]["username"]
        else:
                return  ""



def getParticipantKind(mealId, userID):
    rows = db.execute("select community from   mealProcess where  mealId = :mealId and  userId = :userId",
                      mealId = mealId, userId=userID)
    if len(rows) != 0:
        return rows[0]["community"]
    else:
        return 0






def getCommunities():
        communities = db.execute("select * from community where id <>1 ")
        return communities