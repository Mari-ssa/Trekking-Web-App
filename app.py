from flask import Flask, render_template, request, redirect, session, abort
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from database import db
from config import Config
from models import User,Trek,Booking
from datetime import datetime

app=Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return redirect("/login")
            if session.get("role") != role:
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form["name"].strip()
        age=request.form["age"]
        email=request.form["email"].strip().lower()
        phone_no=request.form["phone_no"].strip()
        password=request.form["password"]
        confirm_password=request.form["confirm_password"]
        role=request.form["role"]

        # Name validation
        if not name:
            return "Name is required.", 400

        if len(name) > 100:
            return "Name is too long.", 400
        
        # Age validation
        try:
            age = int(age)
        except ValueError:
            return "Age must be a valid number.", 400
        
        if age < 18 or age > 100:
            return "Age must be between 18 and 100.", 400

        # Email validation
        if "@" not in email or "." not in email.split("@")[-1]:
            return "Invalid email address.", 400

        # Phone validation
        if not phone_no.isdigit() or len(phone_no) != 10:
            return "Phone number must contain exactly 10 digits.", 400

        # Password validation
        if len(password) < 8:
            return "Password must be at least 8 characters long.", 400

        if password != confirm_password:
            return "Passwords do not match!", 400

        # Role validation
        if role not in ["user", "staff"]:
            return "Invalid role.", 400

        existing_user=User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered!"

        if password!=confirm_password:
            return "Passwords do not match!"
        
        hashed_password = generate_password_hash(password,method="pbkdf2:sha256")
        user=User(name=name,age=age,email=email,phone_no=phone_no,password=hashed_password,role=role)
        db.session.add(user)
        db.session.commit()
    

        return "Registration successful"

    return render_template("register.html")


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]

        user=User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password,password):

            if user.blacklisted:
                return "Your account has been blacklisted."

            if user.role == "staff" and not user.approved:
                return "Your staff account is not approved yet."

            session["user_id"] = user.user_id
            session["role"] = user.role

            if user.role == "admin":
                return redirect("/admin/dashboard")

            elif user.role == "staff":
                return redirect("/staff/dashboard")

            elif user.role == "user":
                return redirect("/user/dashboard")

            else:
                return "Invalid role"

        else:
            return "Invalid email or password"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Dashboards -- 3 
@app.route("/admin/dashboard")
@role_required("admin")
def admin_dashboard():
    number_of_treks=Trek.query.count()
    number_of_users=User.query.filter_by(role="user").count()
    number_of_staff=User.query.filter_by(role="staff").count()
    number_of_bookings=Booking.query.filter_by(status="Booked").count()
    return render_template("admin_dashboard.html",number_of_treks=number_of_treks,number_of_users=number_of_users,number_of_staff=number_of_staff,number_of_bookings=number_of_bookings)


@app.route("/staff/dashboard")
@role_required("staff")
def staff_dashboard():
    staff_id = session["user_id"]
    treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()

    return render_template( "staff_dashboard.html",treks=treks)


@app.route("/user/dashboard")
@role_required("user")
def user_dashboard():
    return render_template("user_dashboard.html")


# Admin Routes (Trek add/edit/delete)
@app.route("/admin/treks")
@role_required("admin")
def admin_trek():
    treks = Trek.query.all()
    return render_template("admin_trek.html",treks=treks)

@app.route("/admin/treks/add",methods=["GET","POST"])
@role_required("admin")
def add_trek():
    if request.method=="POST":
        trek_name=request.form["trek_name"]
        location=request.form["location"]
        difficulty=request.form["difficulty"]
        description=request.form["description"]
        status=request.form["status"]

        try:
            duration = int(request.form["duration"])
            price = float(request.form["price"])
            available_slots = int(request.form["available_slots"])
        except ValueError:
            return "Duration, price and available slots must be valid numbers.", 400

        try:
            start_date=datetime.strptime(request.form["start_date"],"%Y-%m-%d").date()
            end_date=datetime.strptime(request.form["end_date"],"%Y-%m-%d").date()
        except ValueError:
            return "Invalid date.", 400

        # Basic validation
        if not trek_name:
            return "Trek name is required.", 400

        if not location:
            return "Location is required.", 400

        if not description:
            return "Description is required.", 400

        if duration <= 0:
            return "Duration must be greater than zero.", 400

        if price < 0:
            return "Price cannot be negative.", 400

        if available_slots < 0:
            return "Available slots cannot be negative.", 400

        if end_date < start_date:
            return "End date cannot be before start date.", 400

        if difficulty not in ["Easy", "Moderate", "Hard"]:
            return "Invalid difficulty.", 400

        if status not in ["Open", "Closed"]:
            return "Invalid trek status.", 400


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
@role_required("admin")
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if request.method=="POST":
        trek.trek_name=request.form["trek_name"].strip()
        trek.location=request.form["location"].strip()
        trek.difficulty=request.form["difficulty"]
        trek.description=request.form["description"].strip()
        trek.status=request.form["status"]
        assigned_staff_id = request.form["assigned_staff_id"]

        try:
            trek.duration=int(request.form["duration"])
            trek.price=float(request.form["price"])
            trek.available_slots=int(request.form["available_slots"])
        except ValueError:
            return "Duration, price and available slots must be valid numbers.", 400

        try:
            trek.start_date = datetime.strptime(request.form["start_date"],"%Y-%m-%d").date()
            trek.end_date = datetime.strptime(request.form["end_date"],"%Y-%m-%d").date()

        except ValueError:
            return "Invalid date.", 400
        
        if assigned_staff_id == "":
            trek.assigned_staff_id = None
        else:
            try:
                trek.assigned_staff_id=int(assigned_staff_id)
            except ValueError:
                return "Invalid staff ID.", 400
            staff = User.query.filter_by(user_id=assigned_staff_id,role="staff",approved=True,blacklisted=False).first()

            if not staff:
                return "Invalid staff assignment.", 400

        if trek.duration <= 0:
            return "Duration must be greater than zero.", 400

        if trek.price < 0:
            return "Price cannot be negative.", 400

        if trek.available_slots < 0:
            return "Available slots cannot be negative.", 400

        if trek.end_date < trek.start_date:
            return "End date cannot be before start date.", 400

        if trek.difficulty not in ["Easy", "Moderate", "Hard"]:
            return "Invalid difficulty.", 400

        if trek.status not in ["Open", "Closed"]:
            return "Invalid trek status.", 400
        

        db.session.commit()

        return redirect("/admin/treks")
    staff_members=User.query.filter_by(role="staff",approved=True,blacklisted=False).all()
    return render_template("edit_trek.html",trek=trek,staff_members=staff_members)

@app.route("/admin/treks/<int:trek_id>/delete")
@role_required("admin")
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    bookings = Booking.query.filter_by(trek_id=trek_id).count()

    if bookings > 0:
        return "This trek cannot be deleted because it has booking records.", 400

    db.session.delete(trek)
    db.session.commit()

    return redirect("/admin/treks")

#Admin Routes (Staff approve/blacklist)
@app.route("/admin/staff")
@role_required("admin")
def admin_staff():
    staff_members=User.query.filter_by(role="staff",approved=True,blacklisted=False).all()
    return render_template("admin_staff.html",staff_members=staff_members)

@app.route("/admin/staff/<int:staff_id>/approve")
@role_required("admin")
def approve_staff(staff_id):
    staff=User.query.get_or_404(staff_id)

    if staff.role != "staff":
        return "Invalid staff account.", 400

    if staff.blacklisted:
        return "Blacklisted staff cannot be approved.", 400
    
    staff.approved=True
    db.session.commit()
    return redirect("/admin/staff")

@app.route("/admin/staff/<int:staff_id>/blacklist")
@role_required("admin")
def blacklist_staff(staff_id):
    staff=User.query.get_or_404(staff_id)
    staff.blacklisted=True
    staff.approved=False
    assigned_treks=Trek.query.filter_by(assigned_staff_id=staff_id).all()

    for trek in assigned_treks:
        trek.assigned_staff_id=None

    db.session.commit()
    return redirect("/admin/staff")

#Admin Routes (Users blacklist)
@app.route("/admin/users")
@role_required("admin")
def admin_users():
    users=User.query.filter_by(role="user").all()
    return render_template("admin_users.html",users=users)

@app.route("/admin/users/<int:user_id>/blacklist")
@role_required("admin")
def blacklist_user(user_id):
    user= User.query.get_or_404(user_id)
    if user.role != "user":
        return "Invalid user account.", 400
    user.blacklisted = True
    db.session.commit()
    return redirect("/admin/users")

@app.route("/admin/bookings")
@role_required("admin")
def admin_bookings():
    bookings = Booking.query.all()
    return render_template("admin_bookings.html", bookings=bookings)

#User
@app.route("/user/treks")
@role_required("user")
def user_treks():
    treks = Trek.query.filter_by(status="Open").all()
    return render_template("user_treks.html", treks=treks)

@app.route("/user/treks/<int:trek_id>/book", methods=["POST"])
@role_required("user")
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    if trek.status != "Open":
        return "This trek is not open for booking.",400
    if trek.available_slots <= 0:
        return "No slots available.",400
    
    existing_booking=Booking.query.filter_by(user_id=session["user_id"],trek_id=trek_id,status="Booked").first()

    if existing_booking:
        return "You have already booked this trek.", 400
    
    booking=Booking(user_id=session["user_id"],trek_id=trek_id,booking_date=datetime.now(),status="Booked")

    trek.available_slots -= 1

    db.session.add(booking)
    db.session.commit()

    return redirect("/user/bookings")

@app.route("/user/bookings")
@role_required("user")
def user_bookings():

    bookings=Booking.query.filter_by(user_id=session["user_id"]).all()
    return render_template( "user_bookings.html",bookings=bookings)

@app.route("/user/bookings/<int:booking_id>/cancel",methods=["POST"])
@role_required("user")
def cancel_booking(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session["user_id"]:
        return "Unauthorized",403
    
    if booking.status == "Booked":
        booking.status = "Cancelled"
        trek = Trek.query.get(booking.trek_id)
        trek.available_slots += 1
        db.session.commit()

    return redirect("/user/bookings")

if __name__=="__main__":
    app.run(debug=True)

