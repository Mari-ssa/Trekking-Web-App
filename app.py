from flask import Flask,render_template,request,redirect,session
from database import db
from config import Config
from models import User,Trek,Booking
from datetime import datetime

app=Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form["name"]
        age=request.form["age"]
        email=request.form["email"]
        phone_no=request.form["phone_no"]
        password=request.form["password"]
        confirm_password=request.form["confirm_password"]
        role=request.form["role"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered!"

        if password!=confirm_password:
            return "Passwords do not match!"

        user=User(name=name,age=age,email=email,phone_no=phone_no,password=password,role=role)
        db.session.add(user)
        db.session.commit()
    

        return "Registration successful"

    return render_template("register.html")


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]

        user=User.query.filter_by(email=email,password=password).first()

        if user:
            if user.role=="admin":
                return redirect("/admin/dashboard")
            elif user.role=="staff":
                if user.blacklisted:
                    return "You are blacklisted and cannot access the staff dashboard."
                elif user.approved==False:
                    return "Your account is not approved yet. Please wait for approval."
                else:
                    return redirect("/staff/dashboard")
            elif user.role=="user":
                if user.blacklisted:
                    return "You are blacklisted and cannot access the user dashboard."
                else:
                    return redirect("/user/dashboard")
            else:
                return "Invalid credentials"
        else:
            return "Invalid credentials"

    return render_template("login.html")

# Dashboards -- 3 
@app.route("/admin/dashboard")
def admin_dashboard():
    number_of_treks=Trek.query.count()
    number_of_users=User.query.filter_by(role="user").count()
    number_of_staff=User.query.filter_by(role="staff").count()
    number_of_bookings=Booking.query.count()
    return render_template("admin_dashboard.html",number_of_treks=number_of_treks, number_of_users=number_of_users, number_of_staff=number_of_staff, number_of_bookings=number_of_bookings)


@app.route("/staff/dashboard")
def staff_dashboard():
    return render_template("staff_dashboard.html")


@app.route("/user/dashboard")
def user_dashboard():
    return render_template("user_dashboard.html")


# Admin Routes (Trek add/edit/delete)
@app.route("/admin/treks")
def admin_trek():
    treks = Trek.query.all()
    return render_template("admin_trek.html",treks=treks)

@app.route("/admin/treks/add",methods=["GET","POST"])
def add_trek():
    if request.method=="POST":
        trek_name=request.form["trek_name"]
        location=request.form["location"]
        duration=request.form["duration"]
        difficulty=request.form["difficulty"]
        price=request.form["price"]
        start_date = datetime.strptime(request.form["start_date"],"%Y-%m-%d").date()
        end_date = datetime.strptime(request.form["end_date"],"%Y-%m-%d").date()
        available_slots=request.form["available_slots"]
        description=request.form["description"]
        status=request.form["status"]

        trek = Trek(
            trek_name=trek_name,
            location=location,
            duration=duration,
            difficulty=difficulty,
            price=price,
            start_date=start_date,
            end_date=end_date,
            available_slots=available_slots,
            description=description,
            status=status
        )

        db.session.add(trek)
        db.session.commit()

        return redirect("/admin/treks")

    return render_template("add_trek.html")

@app.route("/admin/treks/<int:trek_id>/edit",methods=["GET","POST"])
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if request.method=="POST":
        trek.trek_name=request.form["trek_name"]
        trek.location=request.form["location"]
        trek.duration=request.form["duration"]
        trek.difficulty=request.form["difficulty"]
        trek.price=request.form["price"]
        trek.start_date = datetime.strptime(request.form["start_date"],"%Y-%m-%d").date()
        trek.end_date = datetime.strptime(request.form["end_date"],"%Y-%m-%d").date()
        trek.available_slots=request.form["available_slots"]
        trek.description=request.form["description"]
        trek.status=request.form["status"]
        assigned_staff_id = request.form["assigned_staff_id"]
        if assigned_staff_id == "":
            trek.assigned_staff_id = None
        else:
            trek.assigned_staff_id = int(assigned_staff_id)

        db.session.commit()

        return redirect("/admin/treks")
    staff_members=User.query.filter_by(role="staff",approved=True).all()
    return render_template("edit_trek.html",trek=trek,staff_members=staff_members)

@app.route("/admin/treks/<int:trek_id>/delete")
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)
    db.session.commit()

    return redirect("/admin/treks")

#Admin Routes (Staff approve/blacklist)
@app.route("/admin/staff")
def admin_staff():
    staff_members=User.query.filter_by(role="staff").all()
    return render_template("admin_staff.html",staff_members=staff_members)

@app.route("/admin/staff/<int:staff_id>/approve")
def approve_staff(staff_id):
    staff=User.query.get_or_404(staff_id)
    staff.approved=True
    db.session.commit()
    return redirect("/admin/staff")

@app.route("/admin/staff/<int:staff_id>/blacklist")
def blacklist_staff(staff_id):
    staff = User.query.get_or_404(staff_id)
    staff.blacklisted = True
    staff.approved=False
    db.session.commit()
    return redirect("/admin/staff")

#Admin Routes (Users blacklist)
@app.route("/admin/users")
def admin_users():
    users=User.query.filter_by(role="user").all()
    return render_template("admin_users.html",users=users)

@app.route("/admin/users/<int:user_id>/blacklist")
def blacklist_user(user_id):
    user= User.query.get_or_404(user_id)
    user.blacklisted = True
    db.session.commit()
    return redirect("/admin/users")


#User
@app.route("/user/treks")
def user_treks():
    treks = Trek.query.filter_by(status="Open").all()
    return render_template("user_treks.html", treks=treks)

if __name__=="__main__":
    app.run(debug=True)

    