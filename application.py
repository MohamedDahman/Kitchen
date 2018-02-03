from cs50 import SQL
import urllib.request
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology
import cgi, cgitb
from helpers import login_required,mealProcess
from helpers import isUserExsist , getUserHash ,isPasswordFormated , changeUserHash
from helpers import addUser


# Configure application
app = Flask(__name__)

# Ensure responses aren't cached


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


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///kitchen.db")


@app.route("/shopping", methods=["GET", "POST"])
def shopping():
    """shopping"""
    if request.method == "POST":
        if not request.form.get("price"):
            return apology("must provide Total-price", 403)

        Total = request.form.get("price")
        Total_Paid = db.execute("INSERT INTO cost (amount) VALUES(:amount)",
                          Total=request.form.get("price"))

        return redirect("/")
    else:
         mealsRow = db.execute("""SELECT * FROM mealProcess, meals WHERE
                                mealProcess.mealId = meals.id AND mealProcess.userId = :userid AND mealProcess.community = 4""",
                                userid = session["user_id"]    )

         return render_template("shopping.html", meals = mealsRow)


@app.route("/")
def index():
    if session.get("user_id") is None:
        return render_template("image.html")
    else:

        rowData = {}  # this is a dict
        listRowData = []  # this is list

        # in this function to get all shares with current price and put it in the list of dict
        rows = db.execute("select * from  meals order by date")
        currentRow = 0
        while currentRow <= len(rows) - 1:
            rowData = {}
            rowData['name'] = rows[currentRow]["name"]
            rowData['date'] = rows[currentRow]["date"]

            listRowData.append(rowData)
            currentRow = currentRow + 1

        return render_template("index.html", meals = listRowData)



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


@app.route("/changePassword", methods=["GET", "POST"])
def changePassword():
    """change user Password"""

    if request.method == "POST":
        if request.form.get("oldpassword") == '':
            return apology("Please enter old Password", 400)

        if request.form.get("password") == '':
            return apology("Please enter the new Password", 400)

        if request.form.get("confirmation") == '':
            return apology("Please enter the Confirmation", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Password and confirmation not match", 400)

        currentUserId = session["user_id"]

        if check_password_hash(getUserHash(currentUserId), generate_password_hash(request.form.get("oldpassword"))):
            return apology("the old Password not correct", 400)

        hashp = generate_password_hash(request.form.get("password"))
        changeUserHash(currentUserId, hashp)

        flash("Password changed!")
        return redirect("/")
    else:
        flash("Please Password must include Numbers & Lowercase & Uppercase charchter...!")
        return render_template("changePassword.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
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
        return render_template("layout.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        if request.form.get("username") == '':
            return apology("Please enter User Name", 400)

        if request.form.get("password") == '':
            return apology("Please enter User Name", 400)

        if request.form.get("confirmation") == '':
            return apology("Please enter User Name", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Password and confirmation not match")

        if isUserExsist(request.form.get("username")) == 1:
            return apology("username already exsist", 400)

        passowrd = request.form.get("password")

        if isPasswordFormated(passowrd) == False:
                return apology("Please Password must include Numbers & Lowercase & Uppercase charchter...!", 400)


        hashPassword = generate_password_hash(request.form.get("password"))

        addUser(request.form.get("username"), hashPassword)
        flash("Registered!")
        return redirect("/")
    else:
        flash("Please Password must include Numbers & Lowercase & Uppercase charchter...!")
        return render_template("register.html")


@app.route("/addsug", methods=["GET", "POST"])
@login_required
def addsug():

    if request.method == "POST":
        mealName = request.form.get("name")
        mealDes = request.form.get("description")
        mealDate = request.form.get("date")

        suggestion = db.execute("INSERT INTO meals (name, description, date, userId) VALUES (:mName, :mDescription, :mDate ,:user_id)",
                            mName=mealName, mDescription=mealDes, mDate=mealDate , user_id=session["user_id"]  )



        return redirect("/")
    else:
        return render_template("addsug.html")

@app.route("/addrecord", methods=["GET", "POST"])
@login_required
def addrecord():

    if request.method == "POST":
        mealName = request.form.get("material")
        mealDes = request.form.get("quantity")
        mealDate = request.form.get("unit")


        suggestion = db.execute("INSERT INTO meals (name, description, date, userId) VALUES (:mName, :mDescription, :mDate ,:user_id)",
                            mName=mealName, mDescription=mealDes, mDate=mealDate , user_id=session["user_id"]  )
        username = db.execute("SELECT username FROM users WHERE id=:user_id;",
                             user_id=session["user_id"])



        return render_template("materialdetails.html",mealName=mealName,mealDes=mealDes,mealDate=mealDate,cook=username[0]['username'])
    else:
        return render_template("materialdetails.html")


@app.route("/units", methods=["GET", "POST"])
@login_required
def units():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        units = request.form.get("description")

        # Ensure units were entered
        if not units:
            return apology("must provide valid units", 400)

        # Insert the units into units table
        db.execute("INSERT INTO units (description) VALUES (:description)",
                   description=units)

        # Render template and pass data to quoted result page
        return render_template("/units.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("units.html")

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
