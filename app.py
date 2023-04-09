import argparse
from flask import Flask, redirect, url_for, request, render_template, flash
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, login_required, LoginManager, UserMixin


app = Flask(__name__)

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.secret_key = 'its a secret to everyone'

db = SQLAlchemy(app)

#association table
# users_courses = db.Table('users_courses',
#     db.Column('users_id', db.Integer, db.ForeignKey('Users.id')),                   
#     db.Column('courses_id', db.Integer, db.ForeignKey('Courses.course_id'))
# )
#database model for enrolled classes, links both courses table with users table
class EnrolledClasses(db.Model):
    __tablename__ = "EnrolledClasses"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column('users_id', db.Integer, db.ForeignKey('Users.id'))
    courses_id = db.Column('courses_id', db.Integer, db.ForeignKey('Courses.course_id'))
    grade = db.Column(db.Integer, nullable = True)

    user = db.relationship('Users', back_populates = 'enrolled')
    course = db.relationship('Courses', back_populates = 'enrolled')

    def __init__(self, user_id, courses_id, grade):
        self.user_id = user_id
        self.courses_id = courses_id
        self.grade = grade

#database model for Users
class Users(UserMixin, db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    accountId = db.Column(db.Integer, nullable = False) 
    #0:Student, 1:Teacher, 2:Admin
    enrolled = db.relationship('EnrolledClasses', back_populates = 'user')

    def __init__(self, username, name, password, accountId):
        self.username = username
        self.name = name
        self.password = password
        self.accountId = accountId

    def check_password(self, password):
        return self.password == password

    def get_id(self):
        return self.id

    # def __repr__(self):
    #     return f"User('{self.username}')"

#database model for Courses
class Courses(db.Model):
    __tablename__ = "Courses"
    course_id = db.Column(db.Integer, primary_key = True)
    course_name = db.Column(db.String, nullable = False)
    course_teacher = db.Column(db.String, nullable = False)
    course_time = db.Column(db.String, nullable = False)
    students_enrolled = db.Column(db.Integer, nullable = False)
    capacity = db.Column(db.Integer, nullable = False)

    enrolled = db.relationship('EnrolledClasses', back_populates = 'course')

    def __init__(self, course_name, course_teacher, course_time, students_enrolled, capacity):
        self.course_name = course_name
        self.course_teacher = course_teacher
        self.course_time = course_time
        self.students_enrolled = students_enrolled
        self.capacity = capacity


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

#login 
@app.route('/login')
def login_page():
    #replace with actual login template later
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        # if current_user.accountId == 1:
        #     return redirect(url_for('teacher'))
        if current_user.accountId == 0:
            return redirect(url_for('studentUser'))
        else:
            return redirect(url_for('index'))
        
    user = Users.query.filter_by(username=request.form['username']).first()
    if user is None or not user.check_password(request.form['password']):
        return redirect(url_for('login'))
    
    login_user(user)
    # if current_user.accountId == 1:
    #     return redirect(url_for('teacher'))
    if current_user.accountId == 0:
        return redirect(url_for('studentUser'))
    else:
        return redirect(url_for('index'))


@app.route("/student")

def studentClasses():
    stuClasses = []
    enrolledCourses = EnrolledClasses.query.filter_by(user_id=current_user.id).all()
     # using 1 for testing data, replace with current_user

    for course in enrolledCourses:
        stuClasses.append(course.classes_id)

    classes = Courses.query.filter(Courses.course_id.in_(stuClasses))

    return render_template('studentScheduleTest.html', courses = classes)

#display all courses
@app.route("/user")
def studentUser():
    # user_id = current_user.id  # get current user's id
    # user = Users.query.get(user_id)
    enrolled_courses = current_user.enrolled
    allCourses = Courses.query.all()

    #Loop through the enrolled courses and print out the course ids
    courseId_list = []
    for ec in enrolled_courses:
        print(ec.courses_id)
        courseId_list.append(ec.courses_id)

    return render_template('all_courses.html', allCourses=allCourses, user = courseId_list)

#go to page with all enrolled courses
@app.route('/enrolled-courses')
@login_required
def enrolled_courses():
    # usersID = current_user.id
    # print(usersID)
    # user = Users.query.get(usersID)
    # allCourses =  current_user.enrolled
    # print('this is current',user.enrolled)
    
    enrolled_classes = current_user.enrolled
    all_courses = [enrolled.course for enrolled in enrolled_classes]
    print(all_courses)
    return render_template('enrolled_courses.html', allCourses = all_courses)

#add a students course
@app.route('/add_course', methods=['POST'])
@login_required
def enroll_course():
    user_id = current_user.id  # get current user's id
    course_id = request.form['course_id']  # get course_id from form data
    enrollment = EnrolledClasses.query.filter_by(user_id=user_id, courses_id=course_id).first()

    if enrollment:
        flash('You are already enrolled in this course.', 'warning')
        return redirect(url_for('studentUser'))
    
    enrollment = EnrolledClasses(user_id=user_id, courses_id=course_id, grade=None)

    # Get the user and course objects from the database
    user = Users.query.get(user_id)
    course = Courses.query.get(course_id)
    print(course.course_id)
    
    # Add the course to the user's enrolled courses
   
    user.enrolled.append(enrollment)
    course.students_enrolled += 1

    db.session.commit()

    return redirect(url_for('studentUser'))

@app.route('/remove_course', methods=['POST'])
@login_required
def remove_course():
    user_id = current_user.id  # get current user's id
    course_id = request.form['course_id']  # get course_id from form data

    # Get the enrollment object from the database
    enrollment = EnrolledClasses.query.filter_by(user_id=user_id, courses_id=course_id).first()
    if not enrollment:
        flash('You are not enrolled in this course.', 'error')
        return redirect(url_for('studentUser'))
    
    # Get the user and course objects from the database
    user = Users.query.get(user_id)
    course = Courses.query.get(course_id)

    # Remove the enrollment from the user's enrolled courses
    user.enrolled.remove(enrollment)
    course.students_enrolled -= 1
    db.session.delete(enrollment)

    db.session.commit()

    flash('You have been removed from the course.', 'success')
    return redirect(url_for('studentUser'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSE 160 Lab 8 Student Enrollment Web App")
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()

    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=args.port, debug = True)  
