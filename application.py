from cs50 import SQL
import urllib.request
from flask import Flask, flash, redirect, render_template, request, session,jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology
import os
import datetime
from helpers import login_required
from tempfile import mkdtemp
import atexit
from apscheduler.scheduler import Scheduler
from flask_mail import Mail, Message
import smtplib
from email.mime.text import MIMEText
from helpers import *


# Configure application
app = Flask(__name__)


cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    cron.start()


UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = SQL("sqlite:///kitchen.db")

mail = Mail(app)


@app.before_first_request
def _run_on_start():
    initilizeMail()

class initial :
    def __init__ (self):
        global db
        global mail

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




@app.route("/searchMealName")
@login_required
def searchMealName():
    """Search for places that match query """

    value = request.args.get("q")
    value = "%" + str(value) + "%"
    value = str(value)

    rows = db.execute("""select * from meals  where (name like :value ) """,
                      value = value)

    return jsonify(rows)



@app.route("/")
def index():
        return render_template("index.html")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "GET":
        return render_template("search.html", meals=getMealNotRatet(session["user_id"]))
    else:
        mealName=request.form.get("q")
        searchingRows = db.execute("SELECT * FROM meals WHERE name like :mealName",
                          mealName=mealName + "%")
        ownername= db.execute("SELECT * FROM users WHERE id=:name",name = searchingRows[0]["userId"])

     #   print(searchingRows)
        return render_template("searched.html",searchingRows=searchingRows,ownername =ownername[0]["username"],communities = getCommunities())

@app.route("/addRate", methods=["GET", "POST"])
@login_required
def addRate():
    if request.method == "GET":
        return render_template("addRate.html", meals=getMealNotRatet(session["user_id"]))

@app.route("/ratingMeal", methods=["GET", "POST"])
@login_required
def ratingMeal():
            meailId = request.form.get("addRate")
            rows = db.execute("select * from Meals where id= :mealId ", mealId= meailId);
            return render_template("rating1.html",mealname=rows[0]['name'], mealdate = rows[0]['date'],mealcooker =getOwner(meailId),meilId=meailId)


        #first_name = request.form.get("firstName")
        #last_name = request.form.get("lastName")

@app.route("/rating", methods=["GET", "POST"])
@login_required
def ratingMealone():
        meailId = request.form.get("rating")
        return redirect("/")



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


@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")

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
@login_required
def listmeal():
        return render_template("master.html", meals =getAllMealsAfterToday() , communities = getCommunities())


@app.route("/participant", methods=["GET", "POST"])
@login_required
def participant():
        # print(request.args)
        mealId = request.args.get("mealId")
        MealParticipant = getMealParticipant(mealId)
        return jsonify(MealParticipant)


@app.route("/addsug", methods=["GET", "POST"])
@login_required
def addsug():
   if request.method == "POST":
       mealName = request.form.get("name")
       mealDes = request.form.get("description")
       mealDate = request.form.get("date")


       mealId = getMaxMealId()
       maxId = mealId + 1;
       currentUserId = session["user_id"]
       community = 1 # 	Cooker
       mealProcess(mealId, community, currentUserId)
       addMeals(mealName, mealDes, mealDate , session["user_id"])
       file = request.files['image']
       f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
       file.save(f)

       newfilename = UPLOAD_FOLDER+"/"+str(maxId) +".jpg"
       os.rename(f,newfilename)

       sendMailInvitation(mealId, mealName, mealDes , mealDate ,newfilename)

       return render_template("materialdetails.html",units = getUnits() ,mealid=maxId, mealName=mealName,mealDes=mealDes,mealDate=mealDate,cook=getOwner(mealId))
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


@app.route("/units", methods=["GET", "POST"])
@login_required
def units():
      if request.method == "POST":
        units = request.form.get("description")
        if not units:
                return apology("must provide valid units", 400)
        db.execute("INSERT INTO units (description) VALUES (:description)",
                   description=units)
        units = db.execute("SELECT * FROM units")

        return render_template("units.html", units=units)

      else:
        units = db.execute("SELECT * FROM units")
        return render_template("units.html", units=units)


@app.route("/addrecord", methods=["GET", "POST"])
@login_required
def addrecord():
      if request.method == "POST":
        mealid = request.form.get("mealid")

        material =request.form.get("name")
        print(material)
        quntity =request.form.get("quantity")
        print(quntity)
        unit = request.form.get("unit")
        print(unit)
        meal = getMeal(mealid)
        addmealsDetails(mealid,material,quntity,unit)

        return render_template("materialdetails.html",units = getUnits() ,materials=getMealDetails(mealid),mealid=mealid, mealName=meal["name"],meailmealDes=meal["description"],mealDate=meal["date"],cook=getOwner(mealid))


@app.route("/configer", methods=["GET", "POST"])
@login_required
def configer():
    """configer user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        Mail_Server = request.form.get("MailServer")
        Mail_Port = request.form.get("MailPort")
        Mail_Use_Ssl = request.form.get("MailUseSsl")
        Mail_Username = request.form.get("MailUsername")
        Mail_Password = request.form.get("MailPassword")

        hashed_password = generate_password_hash(Mail_Password)

        # Ensure mail server was submitted
        if not Mail_Server:
            return apology("must provide mail server", 400)

        # Ensure mail port was submitted
        if not Mail_Port:
            return apology("must provide mail port", 400)

        # Ensure mail Use Ssl was submitted
        if not Mail_Use_Ssl:
            return apology("must provide mail use ssl", 400)

        # Ensure mail username was submitted
        if not Mail_Username:
            return apology("must provide mail username", 400)

        # Ensure mail password was submitted
        if not Mail_Password:
            return apology("must provide mail password", 400)


        rows = db.execute("SELECT * FROM mailconfigration")
        if (len(rows)==0):
               db.execute("INSERT INTO mailconfigration(Mail_Server,Mail_Port,Mail_Use_Ssl,Mail_Username,Mail_Password)values(:MailServer, :MailPort, :MailUseSsl, :MailUsername, :MailPassword)",
                                  MailServer = request.form.get("MailServer"),MailPort = request.form.get("MailPort"),MailUseSsl = request.form.get("MailUseSsl"),  MailUsername = request.form.get("MailUsername"), MailPassword = hashed_password)
        else:
            db.execute("UPDATE mailconfigration SET Mail_Server= :MailServer ,Mail_Port=:MailPort,Mail_Use_Ssl=:MailUseSsl,Mail_Username=:MailUsername,Mail_Password=:MailPassword ",
                                  MailServer = request.form.get("MailServer"),MailPort = request.form.get("MailPort"),MailUseSsl = request.form.get("MailUseSsl"),  MailUsername = request.form.get("MailUsername"), MailPassword = hashed_password)
        # User reached route via GET (as by clicking a link or via redirect)
        return redirect("/")
    else:
        rows = db.execute("SELECT * FROM mailconfigration")
        if (len(rows)!=0):
            return render_template("mailConfigration.html", Mail_Server = rows[0]["MAIL_SERVER"] ,  Mail_Port = rows[0]["MAIL_PORT"], Mail_Use_Ssl = rows[0]["MAIL_USE_SSL"] , Mail_Username = rows[0]["MAIL_USERNAME"] , Mail_Password = rows[0]["MAIL_PASSWORD"])
        else:
            return render_template("mailConfigration.html", Mail_Server = "" ,  Mail_Port = "" , Mail_Use_Ssl = "" , Mail_Username = "" , Mail_Password = "")
