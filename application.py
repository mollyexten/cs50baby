import os
import datetime

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

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
db = SQL("sqlite:///sleep.db")


@app.route("/")
@login_required
def index():
    """Show summary of sleep"""

    # Get naps from nap log
    sleeps = db.execute("SELECT date, numbernaps, avgnaplen, totalnaplen, totalovernight, wakes FROM sleep WHERE id=:id ORDER BY date desc", id=session["user_id"])
    
    sleep_log=[]
    
    for sleep in sleeps:
        date=sleep["date"]
        numbernaps=sleep["numbernaps"] if sleep["numbernaps"] != None else ""
        avgnaplen=sleep["avgnaplen"] if sleep["avgnaplen"] != None else ""
        totalnaplen=int(sleep["totalnaplen"]) if sleep["totalnaplen"] != 0 else "" 
        totalovernight=int(sleep["totalovernight"]) if sleep["totalovernight"] != 0 else ""
        wakes=sleep["wakes"] if sleep["wakes"] != None else ""
        if sleep["totalnaplen"] and sleep["totalovernight"] != 0:
            totalsleep = int(totalnaplen) + int(totalovernight)
        else:
            totalsleep = ""
        sleep_tuple=(date, numbernaps, avgnaplen, totalnaplen, totalovernight, wakes, totalsleep)
        sleep_log.append(sleep_tuple)

    # Plug in the variables on the index template
    return render_template("index.html", sleep_log=sleep_log)

@app.route("/overnight", methods=["GET", "POST"])
@login_required
def overnight():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
    
        # Create variables from the form elements
        date = request.form.get("date")
        bedtime = request.form.get("bedtime")
        wakeup = request.form.get("wakeup")
        wakes = request.form.get("wakes")
        wakelen = request.form.get("wakelen")
        
        # Ensure date has been selected:
        if date == None:
            return apology("You must select a date.", 403)
        
        # Ensure bedtime and wakeup have been selected:
        elif (bedtime == None) or (wakeup == None):
            return apology("You must enter a bedtime and wakeup time.", 403)
        
        # Ensure wakes variable is a number equal or greater than 0:
        elif wakes.isnumeric() == False:
            return apology("Enter a number for nighttime wakes.", 403)
        
        elif int(wakes) < 0:
            return apology("Enter a number equal to or greater than for nighttime wakes.", 403)
        
        # Ensure wakelen variable is a number equal or greater than 0:
        elif wakelen.isnumeric() == False:
            return apology("Enter a number for length of nightttime wake. (0 if none.)", 403)
        
        elif int(wakelen) < 0:
            return apology("Enter a number equal to or greater than 0 for wake length.", 403)
        
        # Add sleep time to the table:
        else:
            
            # Create the variable for total overnight sleep
            bedtime_hour = bedtime[:(bedtime.index(":"))]
            bedtime_minute = bedtime[(bedtime.index(":")+1):bedtime.index(" ")]
            if int(bedtime_minute) == 00:
                overnight1 = (12-int(bedtime_hour))*60
            else:
                overnight1 = (12-int(bedtime_hour))*60 - 30
            wakeup_hour = wakeup[:(wakeup.index(":"))]
            wakeup_minute = wakeup[(wakeup.index(":")+1):wakeup.index(" ")]
            overnight2 = int(wakeup_hour)*60 + int(wakeup_minute)
            wake_time = int(wakes) * int(wakelen)
            totalovernight = (overnight1 + overnight2) - wake_time
            
            # Check if a row already exists for this date in the sleep table:
            date_check = db.execute("SELECT * FROM sleep WHERE id = :id and date = :date", id = session["user_id"], date = date)
            
            # Create a new row if date does not exist in the table:
            if len(date_check) == 0:
                db.execute("INSERT INTO sleep (id, date, bedtime, wakeup, wakes, wakelen, totalovernight, totalnaplen) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], date, bedtime, wakeup, int(wakes), int(wakelen), int(totalovernight), 0)
            
            # Update row if date already exists in the table:
            else:
                db.execute("UPDATE sleep SET bedtime = :bedtime, wakeup = :wakeup, wakes = :wakes, wakelen = :wakelen, totalovernight = :totalovernight WHERE id = :id and date = :date", id=session["user_id"], date = date, bedtime = bedtime, wakeup = wakeup, wakes = int(wakes), wakelen = int(wakelen), totalovernight = int(totalovernight))
        
            return redirect ("/")

    else:
        return render_template("overnight.html")

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
        rows = db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))

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
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

            # Ensure username doesn't already exist
            rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
            if len(rows) != 0:
                return apology("username already exists in database", 403)

         # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password meets complexity requirements
        elif len(request.form.get("password")) < 6:
            return apology("password must be at least 6 characters", 403)

        # Ensure password confirmation was provided
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 403)

        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")

        # Redirect the user to the homepage and insert username and password into the database
        else:
            new_hash = generate_password_hash(request.form.get("password"))
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), new_hash)
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/naps", methods=["GET", "POST"])
@login_required
def naps():
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
    
        # Create variables from the form elements
        date = request.form.get("date")
        morningnap = request.form.get("morningnap")
        afternoonnap = request.form.get("afternoonnap")
        eveningnap = request.form.get("eveningnap")
        
        # Ensure date has been selected:
        if date == None:
            return apology("You must select a date.", 403)
        
        # Ensure no naps are blank:
        elif (morningnap == None) or (afternoonnap == None) or (eveningnap == None):
            return apology("Enter 0 if no nap occurred.", 403)
        
        # Ensure nap times are equal or greater than zero:
        elif (int(morningnap) < 0) or (int(afternoonnap) < 0) or (int(eveningnap) < 0):
            return apology("You must enter 0 or a positive integer.", 403)
        
        # Add naps to the table:
        else:
            
            # Create variables for nap analysis:
            numbernaps = int(morningnap != "0") + int(afternoonnap != "0") + int(eveningnap != "0")
            totalnaplen = int(morningnap) + int(afternoonnap) + int(eveningnap)
            rawavgnaplen = (float(totalnaplen)/numbernaps)
            avgnaplen = "{:.1f}".format(rawavgnaplen)
            
            
            # Check if a row already exists for this row in the sleep table:
            date_check = db.execute("SELECT * FROM sleep WHERE id = :id and date = :date", id = session["user_id"], date = date)
            
            # Create a new row if date does not exist in the table:
            if len(date_check) == 0:
                db.execute("INSERT INTO sleep (id, date, totalovernight, morningnap, afternoonnap, eveningnap, numbernaps, avgnaplen, totalnaplen) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], date, 0, int(morningnap), int(afternoonnap), int(eveningnap), numbernaps, avgnaplen, totalnaplen)
            
            # Update row if date already exists in the table:
            else:
                db.execute("UPDATE sleep SET morningnap = :morningnap, afternoonnap = :afternoonnap, eveningnap = :eveningnap, numbernaps = :numbernaps, avgnaplen = :avgnaplen, totalnaplen = :totalnaplen WHERE id = :id and date = :date", id=session["user_id"], date = date, morningnap = morningnap, afternoonnap = afternoonnap, eveningnap = eveningnap, numbernaps = numbernaps, avgnaplen = avgnaplen, totalnaplen = totalnaplen)
        
        return redirect ("/")
            
        
    # else:
    return render_template("naps.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
