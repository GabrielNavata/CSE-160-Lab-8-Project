from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import app, db
from flask_login import current_user, login_user, login_required, LoginManager, UserMixin

migrate = Migrate(app, db)

# Define your models here
class Users(UserMixin, db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    #0:Student, 1:Teacher, 2:Admin
    accountId = db.Column(db.Integer, nullable = False) 
    #relationship
    enrolled_courses = db.relationship('Courses', secondary='users_courses')
    __table_args__ = {'extend_existing': True}

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
    #relationship
    enrolled_users = db.relationship('Users', secondary='users_courses')
    __table_args__ = {'extend_existing': True}

    def __init__(self, course_name, course_teacher, course_time, students_enrolled, capacity):
        self.course_name = course_name
        self.course_teacher = course_teacher
        self.course_time = course_time
        self.students_enrolled = students_enrolled
        self.capacity = capacity

#database model for enrolled classes, links both courses table with users table
class EnrolledClasses(db.Model):
    __tablename__ = "EnrolledClasses"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    classes_id = db.Column(db.Integer, db.ForeignKey('Courses.course_id'), nullable=False)
    grade = db.Column(db.Integer, nullable = False)
    __table_args__ = {'extend_existing': True}
    def __init__(self, user_id, classes_id, grade):
        self.user_id = user_id
        self.classes_id = classes_id
        self.grade = grade

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        migrate.init_app(app, db)
        migrate_made = migrate.db.create_all()
        print(migrate_made)
