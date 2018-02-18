from cs50 import SQL
import urllib.request
from flask import Flask, flash, redirect, render_template, request, session,jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology
import os
from helpers import login_required,getOwner,mealProcess,isParticipant,getParticipantKind , getCommunities, getUnits,getMealParticipant
from helpers  import getParticipantCount, getAllMealsAfterToday, addUser, sendWellcomdeMail
import datetime
from helpers import login_required
from tempfile import mkdtemp
import atexit
from apscheduler.scheduler import Scheduler
from flask_mail import Mail, Message
import smtplib
from email.mime.text import MIMEText


# Configure application
app = Flask(__name__)

cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    cron.start()
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'it.diaaa@gmail.com'
app.config['MAIL_PASSWORD'] = 'd123321d'

mail = Mail(app)


UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = SQL("sqlite:///kitchen.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)




@app.route("/")
def index():
        return render_template("index.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")





@app.route("/listmeal", methods=["GET", "POST"])
def listmeal():
        return render_template("master.html", meals =[getAllMealsAfterToday()] , communities = [getCommunities()])


@app.route("/participant", methods=["GET", "POST"])
def participant():
        # print(request.args)
        mealId = request.args.get("mealId")
        MealParticipant = getMealParticipant(mealId)
        return jsonify(MealParticipant)


@app.route("/addsug", methods=["GET", "POST"])
def addsug():

   if request.method == "POST":
       mealName = request.form.get("name")
       mealDes = request.form.get("description")
       mealDate = request.form.get("date")

       mealId = db.execute("select max(id) as maxId from meals")
       maxId = mealId[0]["maxId"] + 1
       currentUserId = session["maxId"]
       community = 1 # 	Cooker
       mealProcess(mealId, community, currentUserId)


       file = request.files['image']
       f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

       # add your custom code to check that the uploaded file is a valid image and not a malicious file (out-of-scope for this post)
       file.save(f)


       suggestion = db.execute("INSERT INTO meals (name, description, date, userId) VALUES (:mName, :mDescription, :mDate ,:user_id)",
                           mName=mealName, mDescription=mealDes, mDate=mealDate , user_id=session["user_id"]  )
       Maxidrows = db.execute("SELECT max(id) as id FROM meals ")

       Maxid = Maxidrows[0]["id"]
       newfilename = UPLOAD_FOLDER+"/"+str(Maxid) +".jpg"
       os.rename(f,newfilename)
       ###########Diaa##########
       users = db.execute("SELECT * FROM users")
       cook_user = db.execute("SELECT username FROM users where id=:u_id",u_id=session["user_id"])
       a_users =[]
       allUsers =''
       for i in range(len(users)):
           allUsers = str(users[i]['eMail'])
           print(allUsers)
           with mail.connect() as conn:
               message = render_template("sug_email.html",mealName=mealName,mealDes=mealDes,mealDate=mealDate,cook=cook_user[0]['username'],newfilename=newfilename)
               subject = "hello, %s" % "all"
               msg = Message(sender='it.diaaa@gmail.com',recipients=[allUsers], html=message,subject=subject)
               mail.send(msg)
       ###########Diaa##########
       return render_template("materialdetails.html",units = getUnits() ,mealid=Maxid, mealName=mealName,mealDes=mealDes,mealDate=mealDate,cook=cook_user[0]['username'])
   else:
       return render_template("addsug.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        email = request.form.get("eMail")
        phone_number = request.form.get("phoneNumber")
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("confirmation")
        hashed_password = generate_password_hash(password)

        # Ensure first name was submitted
        if not first_name:
            return apology("must provide first name", 400)

        # Ensure last name was submitted
        if not last_name:
            return apology("must provide last name", 400)

        # Ensure email was submitted
        if not email:
            return apology("must provide email", 400)

        # Ensure phone number was submitted
        if not phone_number:
            return apology("must provide phone number", 400)

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not password_confirmation:
            return apology("must provide password confirmation", 400)

        # Query if there is any similar username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)
        if len(rows) == 1:
            return apology("username taken", 400)

        # Ensure password and password confirmation are matching
        if password != password_confirmation:
            return apology("passwords don't match", 400)


        # Add the user into the users table in database
        session["user_id"] = addUser(first_name, last_name, email, phone_number, username, hashed_password)

        sendWellcomdeMail(email,username)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/removeParticipate", methods=["GET", "POST"])
@login_required
def removeParticipate():
    print("me")
    return redirect("/")


@app.route("/addParticipate", methods=["GET", "POST"])
@login_required
def addParticipate():
    mealId = request.form.get("addParticipate")
    currentUserId = session["user_id"]
    community = 5 # 	Cooker Helper
    mealProcess(mealId, community, currentUserId)
    return redirect("/")


@app.route("/addHellper", methods=["GET", "POST"])
@login_required
def addCokker():
    mealId = request.form.get("addHellper")
    currentUserId = session["user_id"]
    community = 2 # 	Cooker Helper
    mealProcess(mealId, community, currentUserId)
    return redirect("/")


@app.route("/addShopper", methods=["GET", "POST"])
@login_required
def addShopper():
    mealId = request.form.get("addShopper")
    currentUserId = session["user_id"]
    community = 4 # 	Cooker Helper
    mealProcess(mealId, community, currentUserId)
    return redirect("/")



@app.route("/addCleaner", methods=["GET", "POST"])
@login_required
def addCleaner():
    mealId = request.form.get("addCleaner")
    currentUserId = session["user_id"]
    community = 3 # 	Cooker Helper
    mealProcess(mealId, community, currentUserId)
    return redirect("/")


@app.route("/addComunity", methods=["GET", "POST"])
@login_required
def addComunity():
    Comunitytype = request.form.get("addComunity")
    mealId = request.form.get("addComunity")
    currentUserId = session["user_id"]
    community = request.form.get("community")
    if isParticipant(mealId, currentUserId) == 0:
        mealProcess(mealId, community, currentUserId)
    return redirect("listmeal")
