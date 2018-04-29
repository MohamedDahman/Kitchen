import csv
import urllib.request
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
import smtplib
import os
from email.mime.text import MIMEText
from apscheduler.scheduler import Scheduler
from flask import redirect, render_template, request, session
from functools import wraps
import application


# Configure application
app = Flask(__name__)



cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    cron.start()


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
    rows = application.db.execute("insert into  mealProcess (mealId, community, userId) values (:mealId, :community, :userId)",
                      mealId=mealId, community=community ,userId=userID)
    return rows


def isParticipant(mealId, userID):
    rows = application.db.execute("select count(*) as Counts  from mealProcess where  mealId = :mealId and  userId = :userId",
                      mealId = mealId, userId=userID)
    return rows[0]["Counts"]


def getOwner(mealId):
        owner = application.db.execute("select users.username from  mealProcess , users   where mealId= :mealId and users.id = mealProcess.userId and community = 1 " , mealId = mealId)
        if len(owner) !=0 :
                return   owner[0]["username"]
        else:
                return  ""



def getParticipantKind(mealId, userID):
    rows = application.db.execute("select community from   mealProcess where  mealId = :mealId and  userId = :userId",
                      mealId = mealId, userId=userID)
    if len(rows) != 0:
        return rows[0]["community"]
    else:
        return 0


def getCommunities():
        communities = application.db.execute("select * from community where id <>1 ")
        return communities


def getUnits():
    unitsrows = application.db.execute("SELECT * FROM units")
    return unitsrows


def getMealParticipant(mealId):
    MealParticipant = application.db.execute("select users.username from  mealProcess , users   where mealId= :mealId and users.id = mealProcess.userId " , mealId = mealId )
    return MealParticipant

def getParticipantCount(mealId):

    ParticipantCount = application.db.execute("select count(distinct userId) as userCount from  mealProcess where  mealId = :mealId",
                                   mealId=mealId)
    return ParticipantCount


def getAllMealsAfterToday():
        rowData = {}  # this is a dict
        listRowData = []  # this is list
        now = datetime.datetime.now()
        # in this function to get all shares with current price and put it in the list of dict
        rows = application.db.execute("select * from  meals  where date >= :date order by date asc", date = str(now))

        currentRow = 0
        while currentRow <= len(rows) - 1:
            rowData = {}
            rowData['id'] = rows[currentRow]["id"]
            rowData['name'] = rows[currentRow]["name"]
            rowData['date'] = rows[currentRow]["date"]
            rowData['ParticipateCount'] = getParticipantCount(rows[currentRow]["id"])
            rowData['username'] = getOwner(rows[currentRow]["id"] )
            rowData['isParticipant'] = getParticipantKind(rows[currentRow]["id"], session["user_id"])
            print(rowData['isParticipant'])
            listRowData.append(rowData)
            currentRow = currentRow + 1

        return listRowData


def addUser(first_name,last_name,email,phone_number,username,hashed_password):
    rows = application.db.execute("INSERT INTO users (firstName, lastName, eMail, phoneNumber, username, hash) VALUES (:firstName, :lastName, :eMail, :phoneNumber, :username, :hash)",
                      firstName=first_name, lastName=last_name, eMail=email, phoneNumber=phone_number, username=username, hash=hashed_password)
    return rows


def sendWellcomdeMail(email,username):
    time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = Message(' Kitchen App Service !! ' + time,sender=getMailName(), recipients =[email])
    msg.html=render_template('/welcomeuser.html',user_name=username)
    application.mail.send(msg)


def addMeals(mealName, mealDes, mealDate , userId):
    suggestion = application.db.execute("INSERT INTO meals (name, description, date, userId) VALUES (:name, :description, :mealDate ,:userId)",
                            name = mealName, description = mealDes, mealDate = mealDate , userId = userId )

def getMeal(mealId):
    meal = application.db.execute("select * from meals where id = :id",id=mealId)
    return meal[0]

def addmealsDetails(mealId , material , quntity, unit):
    maxId = application.db.execute("SELECT max(id) as maxvalue from mealsDetails")
    maxIdValue = maxId[0]["maxvalue"]
    meal = application.db.execute("INSERT INTO mealsDetails (id ,mealId,material,quntity,unit) VALUES (:id1 ,:mealId,:material,:quntity,:unit)",
                                id1 = maxIdValue+1 ,mealId = mealId ,material=material,quntity=quntity ,unit=unit)
    return meal

def getMaxMealId():
    mealId = application.db.execute("select max(id) as maxId, count(*) as counts from meals")
    if (mealId[0]["counts"]==0) :
        maxId = 0
    else:
        maxId = mealId[0]["maxId"]

    return maxId


def sendMailInvitation(mealId, mealName, mealDes , mealDate , newfilename):
       cook_user = getOwner(mealId)
       users = application.db.execute("SELECT * FROM users")
       a_users =[]
       allUsers =''
       for i in range(len(users)):
           allUsers = str(users[i]['eMail'])
           print(allUsers)
           with application.mail.connect() as conn:
               message = render_template("sug_email.html",mealName=mealName,mealDes=mealDes,mealDate=mealDate,cook=cook_user,newfilename=newfilename)
               subject = "hello, %s" % "all"
               msg = Message(sender=getMailName(),recipients=[allUsers], html=message,subject=subject)
               application.mail.send(msg)

def getMealNotRatet(userId):
    rowData = {}  # this is a dict
    listRowData = []  # this is list

    rows = application.db.execute("select * from Meals where id not in (select mealid from mealRating where userId =:userId)", userId=userId)

    currentRow = 0
    sumtotal = 0
    while currentRow <= len(rows) - 1:
            rowData = {}
            rowData['id'] = rows[currentRow]["id"]
            rowData['name'] = rows[currentRow]["name"]
            rowData['date'] = rows[currentRow]["date"]
            rowData['cooker'] = getOwner(rows[currentRow]["id"])
            listRowData.append(rowData)
            currentRow = currentRow + 1

    return listRowData


def getMealDetails(mealId):
    mealDetails = application.db.execute("select m.id,material,mealId,quntity,unit,description from  mealsDetails m,units u where mealId = :mealId and m.unit = u.id",mealId = mealId )
    return mealDetails

def getMailName():
        rows = application.db.execute("select * from mailconfigration ")
        return rows[0]["MAIL_USERNAME"]

def initilizeMail():
    print("**************************initialize mail configration********************************")
    rows = application.db.execute("SELECT * FROM mailconfigration")
    if len(rows) ==1 :
        app.config['MAIL_SERVER'] = rows[0]['MAIL_SERVER'] #'smtp.gmail.com'
        app.config['MAIL_PORT'] = rows[0]['MAIL_PORT']
        app.config['MAIL_USE_SSL'] = rows[0]['MAIL_USE_SSL']
        app.config['MAIL_USERNAME'] = rows[0]['MAIL_USERNAME']
        app.config['MAIL_PASSWORD'] = rows[0]['MAIL_PASSWORD']
        application.mail = Mail(app)
    print("**************************initialize mail configration********************************")
