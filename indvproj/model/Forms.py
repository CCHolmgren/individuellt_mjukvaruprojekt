from flask_wtf import Form
from wtforms import TextField, PasswordField, validators, TextAreaField, SubmitField
from wtforms.fields.html5 import URLField
from .models import Category, User
from wtforms.validators import ValidationError
from sqlalchemy import func

__author__ = 'Chrille'


class RegistrationForm(Form):
    username = TextField("Username",
                         [validators.Regexp(r'^[\w\d]+$', message="Your username can only contain a-zA-Z and 0-9"),
                          validators.Length(min=5, max=120)])
    email = TextField("Email", [validators.Length(min=6), validators.Email()])
    password = PasswordField("New password", [
        validators.Required(),
        validators.EqualTo("confirm", message="Passwords must match"),
        validators.Length(min=5)
    ])
    confirm = PasswordField("Repeat password", [validators.Required()])


class TextPostForm(Form):
    title = TextField("Title", [validators.Length(min=10, max=250), validators.Required()])
    content = TextAreaField("Content here", [validators.Length(min=10, max=2000), validators.Required()])
    categoryname = TextField('Categoryname', [validators.Length(min=1, max=100), validators.Required()])

    def validate_categoryname(self, field):
        if not Category.query.filter_by(categoryname=field.data).first():
            raise ValidationError("The category doesn't seem to exist.")


class EditPostForm(Form):
    content = TextAreaField("Content here", [validators.Length(min=10, max=2000), validators.Required()])


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
    categorytitle = TextField("Categorytitle", [validators.Length(min=10, max=100), validators.Required()])
    categoryname = TextField("Categoryname", [validators.Length(min=4, max=100), validators.Regexp(r'^[\w+-]+$')])


class DeletePostForm(Form):
    submit = SubmitField("Delete")


class AddToCollectionForm(Form):
    link = TextField("Link", [validators.URL(require_tld=False)], default="Link")
    submit = SubmitField("Add link to collection")


class AddModeratorForm(Form):
    username = TextField('Username')

    def validate_username(self, field):
        if not User.query.filter(func.lower(User.username) == func.lower(field.data)).first():
            raise ValidationError("The user doesn't seem to exist.")


class CommentForm(Form):
    content = TextAreaField('Content', [validators.Length(max=2000)])
