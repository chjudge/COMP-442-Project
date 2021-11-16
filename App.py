from forms import RegisterForm, LoginForm
from hasher import Hasher
import os
import sys
from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required
from flask_login import login_user, logout_user, current_user

# Make sure this directory is in your Python path for imports
scriptdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(scriptdir)

dbfile = os.path.join(scriptdir, "users.sqlite3")
pepfile = os.path.join(scriptdir, "pepper.bin")

# open and read the contents of the pepper file into your pepper key
with open(pepfile, 'rb') as fin:
    pepper_key = fin.read()

# create a new instance of UpdatedHasher using that pepper key
pwd_hasher = Hasher(pepper_key)

# Configure the Flask Application
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = 'correcthorsebatterystaple'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbfile}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Getting the database object handle from the app
db = SQLAlchemy(app)

# Prepare and connect the LoginManager to this app
app.login_manager = LoginManager()
app.login_manager.login_view = 'get_login'

@app.login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode, nullable=False)
    profile = db.relationship('UserProfile', backref='user', lazy=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.LargeBinary)  # hash is a binary attribute

    # make a write-only password property that just updates the stored hash
    @property
    def password(self):
        raise AttributeError("password is a write-only attribute")

    @password.setter
    def password(self, pwd):
        self.password_hash = pwd_hasher.hash(pwd)

    # add a verify_password convenience method
    def verify_password(self, pwd):
        return pwd_hasher.check(pwd, self.password_hash)

# store data for users profile information
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    profile_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fname = db.Column(db.Unicode, nullable=False)
    lname = db.Column(db.Unicode, nullable=False)
    bio = db.Column(db.Unicode, nullable=True)
    def __str__(self):
        return f"UserProfile(profile_id={self.profile_id}, user_id={self.user_id}, fname={self.fname}, lname={self.lname})"
    def __repr__(self):
        return f"UserProfile(profile_id={self.profile_id}, user_id={self.user_id}, fname={self.fname}, lname={self.lname})"

db.create_all()

# show user registration form
@app.get('/register/')
def get_register():
    r_form = RegisterForm()
    return render_template('register.html', form=r_form)

# show user login form
@app.get('/login/')
def get_login():
    l_form = LoginForm()
    return render_template('login.html', form=l_form)

# validate registration form
@app.post('/register/')
def post_register():
    r_form = RegisterForm()

    if r_form.validate():
        # check if user has an account
        user = User.query.filter_by(email=r_form.email.data).first()

        if user is None:
            print('creating user')
            user = User(email=r_form.email.data, password=r_form.password.data)
            db.session.add(user)
            db.session.commit()

            # add name to profile
            user_profile = UserProfile(user_id=User.query.filter_by(
                email=r_form.email.data).first().id, fname=r_form.fname.data, lname=r_form.lname.data)
            db.session.add(user_profile)
            db.session.commit()
            return redirect(url_for('get_login'))
        else:  # flash error if account exists
            print('user exists')
            flash('An account with that email address already exists')
            return redirect(url_for('get_register'))
    else:  # flash errors if form is invalid
        for field, error in r_form.errors.items():
            print(f"{field}: {error}")
            flash(f"{field}: {error}")
        return redirect(url_for('get_register'))

# validate login form
@app.post('/login/')
def post_login():
    l_form = LoginForm()

    if l_form.validate():
        # check if user has an account
        user = User.query.filter_by(email=l_form.email.data).first()

        # check if password is correct
        if user is not None and user.verify_password(l_form.password.data):
            print(f'logging in user {l_form.email.data}')
            login_user(user)

            # send user back to page they are trying to access
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('index')
            return redirect(next)
        else:  # flash error if account does not exist
            print('Invalid email or password')
            flash('Invalid email or password')
            return redirect(url_for('get_login'))
    else:  # flash errors if form is invalid
        for field, error in l_form.errors.items():
            print(f"{field}: {error}")
            flash(f"{field}: {error}")
        return redirect(url_for('get_login'))

# logout user account
@app.get('/logout/')
@login_required
def get_logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

# display user's profile information
@app.get('/profile/')
@login_required
def get_profile():
    # pass through the profile of the current user
    user_profile = UserProfile.query.filter_by(
        user_id=current_user.get_id()).first()
    return render_template('profile.html', user=current_user, profile=user_profile)

# facilitate updates to user profile information
@app.post('/profile/')
@login_required
def post_profile():
    # update bio
    bio = request.form.get('bio')
    if bio is not None:
        user_profile = UserProfile.query.filter_by(
            user_id=current_user.get_id()).first()
        user_profile.bio = bio
        db.session.commit()
    return redirect(url_for('get_profile'))

# show admin only page, view and remove users
@app.get('/admin/')
@login_required
def get_admin_page():
    if User.query.filter_by(id=current_user.get_id()).first().admin:
        users = User.query.all()
        profiles = UserProfile.query.all()
        return render_template('admin.html', user=current_user, users=users, profiles=profiles)
    # non-admin users can't view the page
    else:
        return redirect(url_for('index'))

# update database from admin page
@app.post('/admin/')
@login_required
def post_admin_page():
    if User.query.filter_by(id=current_user.get_id()).first().admin:
        if request.form.get('remove_user') is not None:
            user_id = request.form.get('remove_user')
            user = User.query.filter_by(id=user_id).first()
            # remove users
            if user is not None:
                db.session.delete(UserProfile.query.filter_by(
                    user_id=user_id).first())
                db.session.delete(user)
                db.session.commit()
        elif request.form.get('view_profile') is not None:
            user_id = request.form.get('view_profile')
            # get user requested by admin page
            user = User.query.filter_by(id=user_id).first()
            user_profile = UserProfile.query.filter_by(
                user_id=user.get_id()).first()
            # go to user profile
            return render_template('profile.html', user=user, profile=user_profile)

        return redirect(url_for('get_admin_page'))
    else:
        return redirect(url_for('index'))

        # return default page

@app.get('/')
def index():
    return render_template("homepage.html") # Replaced index.html, user=current_user

@app.get("/about/")
def get_about_page():
    pass