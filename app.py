import argparse
from flask_sqlalchemy import SQLAlchemy
from flask import *


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

db = SQLAlchemy(app)

#database model for Users
class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)

    def __repr__(self):
        return f"User('{self.username}')"

#database model for Courses
class Courses(db.Model):
    course_id = db.Column(db.Integer, primary_key = True)
    course_name = db.Column(db.String, unique = True, nullable = False)
    course_teacher = db.Column(db.String, unique = True, nullable = False)
    course_time = db.Column(db.String, unique = True, nullable = False)
    #will add number of student enrolled later





@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSE 160 Lab 8 Student Enrollment Web App")
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()

    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=args.port, debug = True)  