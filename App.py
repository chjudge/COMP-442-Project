import os, sys
from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required
from flask_login import login_user, logout_user, current_user

# Make sure this directory is in your Python path for imports
scriptdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(scriptdir)

from hasher import Hasher
from forms import RegisterForm, LoginForm

#get database
dbfile = os.path.join(scriptdir, 'users.sqlite3')
pepfile = os.path.join(scriptdir, 'pepper.bin')

with open(pepfile, 'rb') as fin:
  pepper_key = fin.read()

# create a new instance of UpdatedHasher using that pepper key
pwd_hasher = Hasher(pepper_key)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = '15vbhwficniuh7h23j8h2892hf92'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbfile}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(dbfile)

app.login_manager = LoginManager()
app.login_manager.login_view = 'get_login'
@app.login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))


#database model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode, nullable=False)
    password_hash = db.Column(db.LargeBinary) # hash is a binary attribute

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

db.create_all()

@app.get('/register/')
def get_register():
    r_form = RegisterForm()
    return render_template('register.html', form=r_form)


@app.get('/login/')
def get_login():
    pass

@app.get('/')
def index():
    return redirect(url_for('get_register'))