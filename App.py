from werkzeug.datastructures import MultiDict
from forms import ProfileForm, RegisterForm, LoginForm
from hasher import Hasher
import os, sys, datetime, re
from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
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
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    fname = db.Column(db.Unicode, nullable = True)
    lname = db.Column(db.Unicode, nullable = True)
    gender = db.Column(db.Enum('Male', 'Female'), nullable = True)
    bio = db.Column(db.Unicode, nullable = True)
    # interests = db.Column(db.Unicode, nullable = True) # TODO: make this into a list
    # dislikes = db.Column(db.Unicode, nullable = True) # TODO: make this into a list

    def __str__(self):
        return f"UserProfile(id={self.id}, fname={self.fname}, lname={self.lname})"
    def __repr__(self):
        return f"UserProfile(id={self.id}, fname={self.fname}, lname={self.lname})"

    # (K) I know he did an example on this is class 11/17. Once I get that code, I may change this
    def serialize(self):
        return {
            "id": self.id,
            "fname": self.fname,
            "lname": self.lname,
            "gender": self.gender,
            "bio": self.bio
        }
    def profile_to_json(self):
        return {
            "id": self.id,
            "fname": self.fname,
            "lname": self.lname,
            "gender": self.gender,
            "bio": self.bio,
            "interests": self.interests,
            "dislikes": self.dislikes
        }

# db.drop_all() # (K) Added this to fix querying issues. Use it as needed
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
            user_profile = UserProfile(id=User.query.filter_by(email=r_form.email.data).first().id)
            db.session.add(user_profile)
            db.session.commit()

            # (K) trying something
            # user = User.query.filter_by(email=r_form.email.data).first()
            login_user(user) 

            return redirect(url_for('get_profile'))
        else:  # flash error if account exists
            print('user exists')
            flash('An account with that email address already exists')
            return redirect(url_for('get_register'))
    else:  # flash errors if form is invalid
        exclude = r'[\'\[\]]'
        for field, error in r_form.errors.items():
            print(f"{field}: {str(error)}")
            flash(f"{re.sub(exclude, '', str(error))}")
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
                next = url_for('get_homepage')
            return redirect(next)
        else:  # flash error if account does not exist
            print('Invalid email or password')
            flash('Invalid email or password')
            return redirect(url_for('get_login'))
    else:  # flash errors if form is invalid
        exclude = r'[\'\[\]]'
        for field, error in l_form.errors.items():
            print(f"{field}: {str(error)}")
            flash(f"{re.sub(exclude, '', str(error))}")
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
    p_form = ProfileForm()
    # pass through the profile of the current user
    user_profile = UserProfile.query.filter_by(id=current_user.get_id()).first()
    return render_template('profile.html', user=current_user, profile=user_profile, form=p_form, update = False)

# allow user to update
@app.get('/profile/update/')
@login_required
def update_profile():
    user_profile = UserProfile.query.filter_by(id=current_user.get_id()).first()
    p_form = ProfileForm(formdata=MultiDict({"fname": user_profile.fname, "lname": user_profile.lname, 
        "gender": user_profile.gender, "bio": user_profile.bio}))
    return render_template('profile.html', user=current_user, profile=user_profile, form=p_form, update = True)

# @app.post('/profile/update/')
# @login_required
# def post_update_profile():
#     p_form = ProfileForm()
#     # update bio
#     if p_form.validate():
#         user_profile = UserProfile.query.filter_by(id=current_user.get_id()).first()
#         user_profile.fname = p_form.fname.data
#         user_profile.lname = p_form.lname.data
#         user_profile.gender = p_form.gender.data
#         user_profile.bio = p_form.bio.data
        
#         db.session.commit()
#     else:
#         print('failure')
#         print(p_form.fname.data)
#         print(p_form.lname.data)
#         print(p_form.gender.data)
#         print(p_form.bio.data)
#         for field, error in p_form.errors.items():
#             print(f"{field}: {error}")
#     return redirect(url_for('get_profile'))
# facilitate updates to user profile information

@app.post('/profile/')
@app.post('/profile/update/')
@login_required
def post_profile():
    p_form = ProfileForm()
    # update bio
    if p_form.validate():
        user_profile = UserProfile.query.filter_by(id=current_user.get_id()).first()
        user_profile.fname = p_form.fname.data
        user_profile.lname = p_form.lname.data
        user_profile.gender = p_form.gender.data
        user_profile.bio = p_form.bio.data

        db.session.commit()
    else:
        print('failure')
        print(p_form.fname.data)
        print(p_form.lname.data)
        print(p_form.gender.data)
        print(p_form.bio.data)
        for field, error in p_form.errors.items():
            print(f"{field}: {error}")
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
                db.session.delete(UserProfile.query.filter_by(id=user_id).first())
                db.session.delete(user)
                db.session.commit()
                flash(f'User #{user_id} has been removed')
        elif request.form.get('view_profile') is not None:
            user_id = request.form.get('view_profile')
            # get user requested by admin page
            user = User.query.filter_by(id=user_id).first()
            user_profile = UserProfile.query.filter_by(id=user.get_id()).first()
            # go to user profile
            return render_template('profile.html', user=user, profile=user_profile)
        elif request.form.get('make_admin') is not None:
            user_id = request.form.get('make_admin')
            # get user requested by admin page
            user = User.query.filter_by(id=user_id).first()
            if user is not None:
                user.admin = 1
                db.session.commit()
                flash(f'User {user_id} has been made an administrator')
        return redirect(url_for('get_admin_page'))
    else:
        return redirect(url_for('index'))

        # return default page

@app.get('/')
def index():
    return render_template("welcome.html", user = current_user)

@app.get("/home/")
@login_required
def get_homepage():
    return render_template("homepage.html", user = current_user)

@app.get("/about/")
def get_about_page():
    pass

@app.get("/api/v1/profiles/")
def get_profiles():
    profiles = UserProfile.query.all()
    return jsonify({
        "requested": datetime.datetime.now(),
        "profiles": [profile.serialize() for profile in profiles]
    })

# @app.get("/api/v1/profiles/<int:user_id>")
# def get_other_profile(user_id): # Rename eventually
#     profile = UserProfile.query.filter(id = user_id)
#     return jsonify({
#         "requested": datetime.datetime.now(),
#         "profile": profile.profile_to_json()
#     })