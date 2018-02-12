from cs50 import SQL
import urllib.request
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology
import os
from helpers import login_required


# Configure application
app = Flask(__name__)


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
@login_required
def listmeal():
        rowData = {}  # this is a dict
        listRowData = []  # this is list

        # in this function to get all shares with current price and put it in the list of dict
        rows = db.execute("select * from  meals order by date")
        currentRow = 0
        while currentRow <= len(rows) - 1:
            rowData = {}
            rowData['id'] = rows[currentRow]["id"]
            rowData['name'] = rows[currentRow]["name"]
            rowData['date'] = rows[currentRow]["date"]


            helper = db.execute("select count(*) as Counts,userId as helper from  mealProcess where community =2 and mealId = :mealId group by userId",
                               mealId=rows[currentRow]["id"])
            if len(helper) == 1:
                    users = db.execute("select userName from  users where id = :userid",
                                userid=helper[0]["helper"])
                    rowData['helper'] = users[0]["username"]
            else:
                    rowData['helper'] =0



            Shopper = db.execute("select count(*) as Counts,userId as helper from  mealProcess where community =4 and mealId = :mealId group by userId",
                               mealId=rows[currentRow]["id"])
            if len(Shopper) == 1:
                    users = db.execute("select userName from  users where id = :userid",
                                userid=Shopper[0]["helper"])
                    rowData['Shopper'] = users[0]["username"]
            else:
                    rowData['Shopper'] =0


            Cleaner = db.execute("select count(*) as Counts,userId as helper from  mealProcess where community =3 and mealId = :mealId group by userId",
                               mealId=rows[currentRow]["id"])
            if len(Cleaner) == 1:
                    users = db.execute("select userName from  users where id = :userid",
                                userid=Cleaner[0]["helper"])
                    rowData['Cleaner'] = users[0]["username"]
            else:
                    rowData['Cleaner'] =0



            Participate = db.execute("select count(*) as Counts,userId as helper from  mealProcess where community =5 and mealId = :mealId group by userId",
                               mealId=rows[currentRow]["id"])
            if len(Participate) == 1:
                    users = db.execute("select userName from  users where id = :userid",
                                userid=Participate[0]["helper"])
                    rowData['Participate'] = users[0]["username"]
            else:
                    rowData['Participate'] =0


            ParticipateCount = db.execute("select count(*) as Counts from  mealProcess where community =5 and mealId = :mealId ",
                               mealId=rows[currentRow]["id"])
            count =  ParticipateCount[0]["Counts"]

            workerCount = db.execute("select count(distinct userId) as userCount from  mealProcess where  mealId = :mealId",
                               mealId=rows[currentRow]["id"])
            count +=  workerCount[0]["userCount"]

            rowData['ParticipateCount'] = count

            listRowData.append(rowData)
            currentRow = currentRow + 1



        return render_template("master.html", meals = listRowData)


@app.route("/addsug", methods=["GET", "POST"])
@login_required
def addsug():

   if request.method == "POST":
       mealName = request.form.get("name")
       mealDes = request.form.get("description")
       mealDate = request.form.get("date")


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
       unitsrows = db.execute("SELECT description FROM units")
       return render_template("materialdetails.html",units =unitsrows ,mealid=Maxid, mealName=mealName,mealDes=mealDes,mealDate=mealDate,cook=session["user_id"])
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

        # Ensure username not exists
        if len(rows) == 1:
            return apology("username taken", 400)

        # Ensure password and password confirmation are matching
        if password != password_confirmation:
            return apology("passwords don't match", 400)

        # Add the user into the users table in database
        rows = db.execute("INSERT INTO users (firstName, lastName, eMail, phoneNumber, username, hash) VALUES (:firstName, :lastName, :eMail, :phoneNumber, :username, :hash)",
                          firstName=first_name, lastName=last_name, eMail=email, phoneNumber=phone_number, username=username, hash=hashed_password)

        # Remember which user has logged in
        session["user_id"] = rows

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

