from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, SubmitField, TextAreaField
from wtforms.fields.core import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Email, EqualTo, Length

class RegisterForm(FlaskForm):
    email = EmailField("Email: ", validators=[InputRequired(), Email()])
    fname = StringField("First Name: ", validators=[InputRequired(), Length(max=30)])
    lname = StringField("Last Name: ", validators=[InputRequired(), Length(max=30)])
    password = PasswordField("Password: ", 
        validators=[InputRequired(), Length(min=8, max=256)])
    confirm_password = PasswordField("Confirm Password: ", 
        validators=[EqualTo('password')])
    submit = SubmitField("Register")

class ProfileForm(FlaskForm):
    fname = StringField("First Name: ", validators=[InputRequired()])
    lname = StringField("Last Name: ", validators=[InputRequired()])
    bio = TextAreaField("Bio: ")
    submit = SubmitField("Create profile")

class LoginForm(FlaskForm):
    email = EmailField("Email: ", validators=[InputRequired(), Email()])
    password = PasswordField("Password: ", 
        validators=[InputRequired(), Length(min=8, max=256)])
    submit = SubmitField("Login")