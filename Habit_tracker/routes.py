import datetime
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
import sys
import uuid

pages = Blueprint("habits",__name__, template_folder="templates", static_folder="static")



@pages.context_processor
def add_cal():
    def date_range(start: datetime.date):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3 ,4)]
        return dates
    return {"date_range":date_range}

def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)    
def start_at_midnight(starting):
    start = datetime.datetime.fromisoformat(starting)
    return start 
@pages.route("/")
def index():
    date_str=request.args.get("date")
    if date_str:
        selected_date= datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()
    habits_on_date = current_app.db.habits.find({"$and": [{"started": {"$lte": selected_date}}, {"ended":{"$gte": selected_date}}]})    
    completions = [
            habit["habit"]
            for habit in current_app.db.completions.find({"date":selected_date})
        ]
    
    return render_template("index.html", 
                        habits=habits_on_date, 
                        title="Habit Tracker - Home", 
                        selected_date=selected_date,
                        completions=completions,
                        )

@pages.route("/add", methods=["GET","POST"])
def add_habit():
    today = today_at_midnight()
    dt= today.strftime('%Y-%m-%d')
    if request.form:
        if len(request.form.get('habit').split())==0: #check if the string that is entered empty
            flash("Empty text is invalid input.") #use flash to pop up the error message and redirect
        else:
            startd=start_at_midnight(request.form.get("startdate"))
            print(request.form.get("startdate"))
            endd=start_at_midnight(request.form.get("enddate"))
            current_app.db.habits.insert_one(
                {"_id": uuid.uuid4().hex, "started": startd, "ended": endd, "name": request.form.get("habit")}
        )
            return redirect(url_for("habits.index", date=today)) 
    
    
    return render_template("add_habit.html", 
                        title="Habit Tracker - Add Habit", 
                        selected_date=today,dt=dt,)


#add new edit page 
@pages.route("/edit", methods=["POST"])
def edit():
    today = today_at_midnight()
    dt= today.strftime('%Y-%m-%d')
    date_string= request.form.get("date")
    habitId = request.form.get("habitId")
    date= datetime.datetime.fromisoformat(date_string)
    habitname = request.form.get("habitname")
    d=current_app.db.habits.find_one({'_id':habitId}) #added the functionality of getting the starting date.
    startdate= d["started"].strftime('%Y-%m-%d') #I should change the index function to store ending date of habit initially.
    enddate=d["ended"].strftime('%Y-%m-%d')
    if request.method == "POST":
        if request.form.get("delete"):
            current_app.db.habits.delete_one({"_id": habitId})
        if request.form.get("habit"):
            startd=start_at_midnight(request.form.get("startdat"))
            endd=start_at_midnight(request.form.get("enddat"))
            current_app.db.habits.update_one(
                {"_id":habitId}, {"$set":{"started":startd, "ended": endd}}
                )
            if len(request.form.get('habit').split())==0: #check if the string that is entered empty
                flash("Empty text is invalid input.") #use flash to pop up the error message and redirect
            else:
                current_app.db.habits.update_one(
                    {"_id": habitId}, {"$set":{"name":request.form.get("habit")}})
                

            return redirect(url_for("habits.index", date=date_string)) 



    return render_template("edit.html", selected_date=date, startdate=startdate,dt=dt, enddate=enddate, date=date_string, habitId=habitId,habitname=habitname,)
    
    


@pages.route("/complete", methods=["POST"])
def complete():
    date_string= request.form.get("date")
    habit = request.form.get("habitId")
    date= datetime.datetime.fromisoformat(date_string)
    current_app.db.completions.insert_one({"date":date, "habit": habit})
    return redirect(url_for("habits.index", date=date_string))


#add new route to cancel the check mark
@pages.route("/incomplete", methods=["POST"])
def incomplete():
    date_string=request.form.get("date")
    habitname= request.form.get("habitId")
    date= datetime.datetime.fromisoformat(date_string)
    current_app.db.completions.delete_one({"habit": habitname})
    return redirect(url_for("habits.index", date=date_string))
    
    
    
###Features that I want to add more
#make able to cancel the checkmark -> delete the database ----complete 2/15/23
#make the whole block clickable ------complete 2/14/23
#make habit deleteable --complete 2/19/23 
#make add habits to not receive empty string --complete 2/15/23
#make to add habits with date range ex: from 2022/2/2~2022/2/10 the most hard part. --complete 2/19/23


####------------new plan added------- 2023/2/15
#make it able to check it ONLY in checkbox ---complete 2/16/23
#add new endpoint to make it editable & deleteable plus add ability to add habits with date range --complete 2/19/23
#-add new ednpoint --completed 2/17/23
#-make it editable --completed 2/18/23
#make the date added editable -- completed 2/18/23
#change add_habit to make functionality to add startdate&enddate of the habit. --complete 2/19/23
#change index function to show the habits in startdate&enddate --complete 2/19/23