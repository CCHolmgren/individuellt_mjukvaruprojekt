__author__ = 'Chrille'
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:bubblegum123@localhost/postgres'
db = SQLAlchemy(app)

class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120),unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(256))
    postscreated = db.Column(db.Integer,default=0)
    comments = db.Column(db.Integer,default=0)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.postscreated = 0
        self.comments = 0

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'))
    #postid = db.Column(db.Integer, db.ForeignKey('post.postid'))
    commentid = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    content = db.Column(db.String(2000))