from database import db

class User(db.Model):
    user_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),nullable=False,unique=True)
    password=db.Column(db.String(255),nullable=False)
    role=db.Column(db.String(10),nullable=False)
    phone_no=db.Column(db.String(10),nullable=False)
    age=db.Column(db.Integer,nullable=False)
    blacklisted=db.Column(db.Boolean,default=False)
    approved=db.Column(db.Boolean,default=False)


class Trek(db.Model):
    trek_id=db.Column(db.Integer,primary_key=True)
    trek_name=db.Column(db.String(100),nullable=False)
    location=db.Column(db.String(100),nullable=False)
    duration=db.Column(db.Integer,nullable=False)
    difficulty=db.Column(db.String(20),nullable=False)
    price=db.Column(db.Float,nullable=False)
    start_date=db.Column(db.Date,nullable=False)
    end_date=db.Column(db.Date,nullable=False)
    available_slots=db.Column(db.Integer,nullable=False)
    status=db.Column(db.String(20),nullable=False,default='Closed')
    description=db.Column(db.Text,nullable=False)
    assigned_staff_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=True)

class Booking(db.Model):
    booking_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    trek_id=db.Column(db.Integer,db.ForeignKey('trek.trek_id'),nullable=False)
    booking_date=db.Column(db.DateTime,nullable=False)
    status=db.Column(db.String(20),nullable=False,default='Booked')