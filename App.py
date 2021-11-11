from forms import RegisterForm, LoginForm
from hasher import Hasher
import os, sys
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
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode, nullable=False)
    fname = db.Column(db.Unicode, nullable=False)
    lname = db.Column(db.Unicode, nullable=False)
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


db.create_all()  # this is only needed if the database doesn't already exist

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
            user = User(email=r_form.email.data, password=r_form.password.data, fname=r_form.fname.data, lname=r_form.lname.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('get_login'))
        else: # flash error if account exists
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
        else: # flash error if account does not exist
            print('Invalid email or password')
            flash('Invalid email or password')
            return redirect(url_for('get_login'))
    else:  # flash errors if form is invalid
        for field, error in l_form.errors.items():
            print(f"{field}: {error}")
            flash(f"{field}: {error}")
        return redirect(url_for('get_login'))


@app.get('/')
def index():
    return render_template('index.html', current_user=current_user)

@app.get('/logout/')
@login_required
def get_logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.get('/profile/')
@login_required
def get_profile():
    return render_template('profile.html', user=current_user)

@app.get('/admin')
@login_required
def get_admin_page():
    print(current_user.get_id())
    if User.query.filter_by(id=current_user.get_id()).first().admin:
        users = User.query.all()
        return render_template('admin.html', user=current_user, users=users)
    else:
        return redirect(url_for('index'))