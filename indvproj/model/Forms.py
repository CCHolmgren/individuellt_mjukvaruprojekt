from flask_wtf import Form
from wtforms import BooleanField, TextField, PasswordField, validators, TextAreaField
__author__ = 'Chrille'

class RegistrationForm(Form):
    username = TextField("Username", [validators.Length(min=5, max=120)])
    email = TextField("Email", [validators.Length(min=6, max=120)])
    password = PasswordField("New password", [
        validators.Required(),
        validators.EqualTo("confirm", message="Passwords must match")
    ])
    confirm = PasswordField("Repeat password")

class NewPostForm(Form):
    title = TextField("Title",[validators.Length(min=10, max=250),validators.Required()])
    content =  TextAreaField("Content here", [validators.Length(min=10, max=2000),validators.Required()])

class LoginForm(Form):
    username = TextField("Username",[validators.Length(min=3,max=120),validators.Required()])
    password = PasswordField("Password",[validators.Length(min=6),validators.Required()])

class CollectionForm(Form):
    title = TextField("Title", [validators.Length(min=10, max=250)])