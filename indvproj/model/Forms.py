from flask_wtf import Form
from wtforms import TextField, PasswordField, validators, TextAreaField
from wtforms.fields.html5 import URLField

__author__ = 'Chrille'


class RegistrationForm(Form):
    username = TextField("Username", [validators.Regexp(r'^[\w.+-]+$'), validators.Length(min=5, max=120)])
    email = TextField("Email", [validators.Length(min=6), validators.Email()])
    password = PasswordField("New password", [
        validators.Required(),
        validators.EqualTo("confirm", message="Passwords must match"),
        validators.Length(min=5)
    ])
    confirm = PasswordField("Repeat password")


class TextPostForm(Form):
    title = TextField("Title", [validators.Length(min=10, max=250), validators.Required()])
    content = TextAreaField("Content here", [validators.Length(min=10, max=2000), validators.Required()])
    categoryname = TextField('Categoryname', [validators.Length(min=1, max=100), validators.Required()])


class LinkPostForm(Form):
    title = TextField("Title", [validators.Length(min=10, max=250), validators.Required()])
    link = URLField([validators.url()])
    categoryname = TextField('Categoryname', [validators.Length(min=10, max=100), validators.Required()])


class LoginForm(Form):
    username = TextField("Username", [validators.Length(min=3, max=120), validators.Required()])
    password = PasswordField("Password", [validators.Length(min=5), validators.Required()])


class CollectionForm(Form):
    title = TextField("Title", [validators.Length(min=10, max=250)])


class CategoryForm(Form):
    categoryname = TextField("Categoryname", [validators.Length(min=10, max=100), validators.Regexp(r'^[\w+-]+$')])