# 🏔️ Trekking Management Application

A web-based **Trekking Management Application** built using **Flask, Jinja2, Bootstrap, and SQLite**. The application provides separate interfaces for **Administrators, Trek Staff, and Users**, allowing treks, staff, users, and bookings to be managed through a centralized system.

---

## Features

### Admin

The Admin has complete control over the application.

* Admin login
* Add new treks
* Edit trek details
* Remove treks
* View all treks
* View registered users
* View trek staff
* Approve trek staff
* Blacklist/unblacklist users or staff
* Assign staff to treks
* Manage trek availability and status

### Trek Staff

Trek Staff can manage the treks assigned to them.

* Staff login
* View assigned trek
* View trek details
* Manage trek-related information
* View/manage relevant bookings

### User

Users can browse available treks and manage their bookings.

* User registration and login
* View available treks
* Search/view trek details
* Book a trek
* View booking history
* View booking status
* Manage their account

---

## Technologies Used

| Technology           | Purpose                |
| -------------------- | ---------------------- |
| **Python**           | Backend programming    |
| **Flask**            | Web framework          |
| **Jinja2**           | Server-side templating |
| **HTML5**            | Page structure         |
| **CSS3**             | Styling                |
| **Bootstrap**        | Responsive UI          |
| **SQLite**           | Database               |
| **Flask-SQLAlchemy** | Database ORM           |
| **Flask-Login**      | User authentication    |

---

## Project Structure

```text
Trek_Management/
│
├── app.py
├── config.py
├── database.py
├── models.py
│
├── routes/
│   ├── __init__.py
│   ├── admin.py
│   ├── staff.py
│   └── user.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   │
│   ├── admin/
│   ├── staff/
│   └── user/
│
├── static/
│   ├── css/
│   └── images/
│
├── instance/
│   └── trekking.db
│
└── README.md
```

---

## Database Design

The application uses **SQLite** with **SQLAlchemy**.

### User

Stores information about registered users and staff.

* `user_id`
* `name`
* `email`
* `password`
* `role`
* `phone_no`
* `age`
* `blacklisted`
* `approved`

### Trek

Stores information about available trekking programs.

* `trek_id`
* `trek_name`
* `location`
* `duration`
* `difficulty`
* `price`
* `start_date`
* `end_date`
* `available_slots`
* `assigned_guide`
* `status`
* `description`

### Booking

Stores information about user bookings.

* `booking_id`
* `trek_id`
* `user_id`
* `booking_date`
* `status`

---

## Authentication & Authorization

The application uses role-based access control.

There are three primary roles:

```text
Admin
  │
  ├── Manage Treks
  ├── Manage Users
  ├── Manage Staff
  └── Assign Staff
       
Staff
  │
  └── Manage Assigned Trek

User
  │
  ├── Browse Treks
  ├── Book Trek
  └── View Booking History
```

Users can only access functionality permitted for their role.

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Trek_Management
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

**macOS/Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If a `requirements.txt` file is not available, install the required packages:

```bash
pip install Flask Flask-SQLAlchemy Flask-Login
```

### 4. Configure the application

The application uses SQLite as its database.

Example configuration:

```python
SQLALCHEMY_DATABASE_URI = "sqlite:///instance/trekking.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

Make sure the `instance/` directory exists before creating the database.

### 5. Create the database

The database is created programmatically using SQLAlchemy.

Run:

```bash
python app.py
```

The application will create the required database tables when the application starts.

---

## Running the Application

Start the Flask development server:

```bash
python app.py
```

The application will normally be available at:

```text
http://127.0.0.1:5000
```

Open the address in a web browser to access the application.

---

## Application Workflow

### User Workflow

```text
Register
   ↓
Login
   ↓
Browse Treks
   ↓
View Trek Details
   ↓
Book Trek
   ↓
Booking Confirmation
   ↓
View Booking History
```

### Staff Workflow

```text
Register/Login
      ↓
Admin Approval
      ↓
Staff Dashboard
      ↓
View Assigned Trek
      ↓
Manage Trek
```

### Admin Workflow

```text
Admin Login
     ↓
Admin Dashboard
     ↓
Manage Treks
     ├── Add
     ├── Edit
     └── Remove
     
Manage Staff
     ├── Approve
     ├── Blacklist
     └── Assign Trek

Manage Users
```

---

## Main Routes

### General

| Method | Route       | Description       |
| ------ | ----------- | ----------------- |
| GET    | `/login`    | Login page        |
| POST   | `/login`    | Authenticate user |
| GET    | `/register` | Registration page |
| POST   | `/register` | Register user     |

### Admin

| Method | Route              | Description          |
| ------ | ------------------ | -------------------- |
| GET    | `/admin/dashboard` | Admin dashboard      |
| GET    | `/admin/treks`     | Manage treks         |
| POST   | `/admin/treks`     | Create/update trek   |
| GET    | `/admin/staff`     | Manage staff         |
| POST   | `/admin/staff`     | Approve/manage staff |
| GET    | `/admin/users`     | View users           |
| POST   | `/admin/users`     | Manage users         |

### Staff

| Method | Route                  | Description          |
| ------ | ---------------------- | -------------------- |
| GET    | `/staff/dashboard`     | Staff dashboard      |
| GET    | `/staff/trek_assigned` | View assigned trek   |
| POST   | `/staff/trek_assigned` | Update assigned trek |

### User

| Method | Route                | Description          |
| ------ | -------------------- | -------------------- |
| GET    | `/user/dashboard`    | User dashboard       |
| GET    | `/user/booking`      | Booking page         |
| POST   | `/user/booking`      | Create booking       |
| GET    | `/user/Trek_details` | View trek details    |
| GET    | `/user/my_history`   | View booking history |

---

## Project Objectives

The main objectives of the application are:

* Provide a centralized trekking management system.
* Simplify trek creation and management.
* Allow administrators to manage staff and users.
* Allow staff to manage their assigned treks.
* Allow users to discover and book treks.
* Maintain booking and user history.
* Implement role-based access control.
* Store application data using a relational database.

---


## Development

This project was developed as a web application using Flask and follows a modular structure separating:

**Models → Routes → Templates → Static Files → Database**

The database is generated programmatically using SQLAlchemy rather than being manually created using a database management application.

---

## Author
Marissa Arul Michael Varghese
