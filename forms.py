from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.fields import PasswordField, SubmitField, TextAreaField
from wtforms.fields import SelectField, StringField
from wtforms.fields.html5 import EmailField, IntegerField
from wtforms.fields.simple import FileField
from wtforms.validators import InputRequired, Email, EqualTo, Length, NumberRange

class RegisterForm(FlaskForm):
    email = EmailField("Email: ", validators=[InputRequired(), Email('Email must be in valid format')])
    password = PasswordField("Password: ", 
        validators=[InputRequired(), Length(min=8, max=256)])
    confirm_password = PasswordField("Confirm Password: ", 
        validators=[EqualTo('password', message='Passwords must match')])
    submit = SubmitField("Register")

class ProfileForm(FlaskForm):
    fname = StringField("First Name: ", validators=[InputRequired()])
    lname = StringField("Last Name: ", validators=[InputRequired()])
    age = IntegerField("Age: ", validators=[InputRequired(), NumberRange(min=0, max=120, message=None)])
    gender = SelectField("Gender: ", choices=["Male", "Female"])
    bio = TextAreaField("Bio: ", validators=[InputRequired()])
    picture = FileField("Profile Picture: ", validators=[FileRequired(), FileAllowed(["jpg", "png"], message="Images only")])
    submit = SubmitField("Update profile")

class LoginForm(FlaskForm):
    email = EmailField("Email: ", validators=[InputRequired(), Email('Email must be in valid format')])
    password = PasswordField("Password: ", 
        validators=[InputRequired(), Length(min=8, max=256)])
    submit = SubmitField("Login")