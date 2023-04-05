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
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)

    def check_password(self, password):
        return self.password == password

    def __repr__(self):
        return f"User('{self.username}')"

#database model for Courses
class Courses(db.Model):
    course_id = db.Column(db.Integer, primary_key = True)
    course_name = db.Column(db.String, unique = True, nullable = False)
    course_teacher = db.Column(db.String, unique = True, nullable = False)
    course_time = db.Column(db.String, unique = True, nullable = False)
    #will add number of student enrolled later

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSE 160 Lab 8 Student Enrollment Web App")
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()

    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=args.port, debug = True)  