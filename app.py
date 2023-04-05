import argparse
from flask import Flask, redirect, url_for, request, render_template
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, login_required, LoginManager, UserMixin


app = Flask(__name__)

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.secret_key = 'its a secret to everyone'

db = SQLAlchemy(app)


#database model for Users
class Users(UserMixin, db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    accountId = db.Column(db.Integer, nullable = False) 
    #0:Student, 1:Teacher, 2:Admin

    def __init__(self, username, name, password, accountId):
        self.username = username
        self.name = name
        self.password = password
        self.accountId = accountId

    def check_password(self, password):
        return self.password == password

    def get_id(self):
        return self.id

    def __repr__(self):
        return f"User('{self.username}')"

#database model for Courses
class Courses(db.Model):
    __tablename__ = "Courses"
    course_id = db.Column(db.Integer, primary_key = True)
    course_name = db.Column(db.String, nullable = False)
    course_teacher = db.Column(db.String, nullable = False)
    course_time = db.Column(db.String, nullable = False)
    students_enrolled = db.Column(db.Integer, nullable = False)
    capacity = db.Column(db.Integer, nullable = False)

    def __init__(self, course_name, course_teacher, course_time, studnets_enrolled, capacity):
        self.course_name = course_name
        self.course_teacher = course_teacher
        self.course_time = course_time
        self.students_enrolled = students_enrolled
        self.capacity = capacity

#database model for enrolled classes, links both courses table with users table
class EnrolledClasses(db.Model):
    __tablename__ = "EnrolledClasses"
    user_id = db.Column(db.ForeignKey("Users.id"), primary_key = True)
    classes_id = db.Column(db.ForeignKey("Courses.course_id"), primary_key = True)
    grade = db.Column(db.Integer, nullable = False)

    def __init__(self, user_id, classes_id, grade):
        self.user_id = user_id
        self.classes_id = classes_id
        self.grade = grade

#flask admin 
admin = Admin(app, name='EnrollmentApp', template_mode='bootstrap3')
admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(Courses, db.session))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)     


@app.route('/')
@login_required
def index():
    return render_template('index.html')

#login stuff no security stuff yet
@app.route('/login')
def login_page():
    #replace with actual login template later
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = Users.query.filter_by(username=request.form['username']).first()
    if user is None or not user.check_password(request.form['password']):
        return redirect(url_for('login'))
    login_user(user)
    return redirect(url_for('index'))


@app.route("/student")

def studentClasses():
    stuClasses = []
    enrolledCourses = EnrolledClasses.query.filter_by(user_id = 1)
     # using 1 for testing data, replace with current_user

    for course in enrolledCourses:
        stuClasses.append(course.classes_id)

    classes = Courses.query.filter(Courses.course_id.in_(stuClasses))

    return render_template('studentScheduleTest.html', courses = classes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSE 160 Lab 8 Student Enrollment Web App")
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()

    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=args.port, debug = True)  
