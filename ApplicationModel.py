__author__ = 'Chrille'
#from flask import Flask
import flask.ext.sqlalchemy
#from sqlalchemy.ext.declarative import declarative_base

#Base = declarative_base()

#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:bubblegum123@localhost/postgres'
#db = SQLAlchemy(app)
db = flask.ext.sqlalchemy.SQLAlchemy()

class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(256))
    postscreated = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)

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
    postid = db.Column(db.Integer, db.ForeignKey('post.postid'))
    commentid = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    content = db.Column(db.String(2000))

    def __init__(self, userid, postid, content, commentid=None):
        self.userid = userid
        self.postid = postid
        self.content = content
        self.commentid = commentid

    def __repr__(self):
        return '<Comment {}>'.format(self.content[:15])


class UserGroup(db.Model):
    __tablename__ = 'usergroup'
    ugid = db.Column(db.Integer, primary_key=True)
    ugname = db.Column(db.String(50), unique=True)
    #children = db.relationship("Visibility", secondary=ug_has_v_table)

    def __init__(self, ugname):
        self.ugname = ugname

    def __repr__(self):
        return '<User_Group {}>'.format(self.ugname)


class Category(db.Model):
    categoryid = db.Column(db.Integer, primary_key=True)
    categoryname = db.Column(db.String(100), unique=True)

    def __init__(self, categoryname):
        self.categoryname = categoryname

    def __repr__(self):
        return '<Category {}>'.format(self.categoryname)


class Group(db.Model):
    groupid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    title = db.Column(db.String(250), nullable=False)

    def __init__(self, userid, title):
        self.userid = userid
        self.title = title

    def __repr__(self):
        return '<Group {} created by {}>'.format(self.title, self.userid)


class Post(db.Model):
    postid = db.Column(db.Integer, primary_key=True)
    createdby = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    timeposted = db.Column(db.DateTime, nullable=False)
    views = db.Column(db.Integer, default=0)
    content = db.Column(db.String(2000), nullable=False)
    typeid = db.Column(db.Integer, db.ForeignKey('type.typeid'), nullable=False)
    title = db.Column(db.String(250), nullable=False)

    def __init__(self, createdby, timeposted, content, typeid, title):
        self.createdby = createdby
        self.timeposted = timeposted
        self.content = content
        self.typeid = typeid
        self.title = title

    def __repr__(self):
        return '<Post {}>'.format(self.title)


class Type(db.Model):
    typeid = db.Column(db.Integer, primary_key=True)
    typename = db.Column(db.String(50), unique=True)

    def __init__(self, typename):
        self.typename = typename

    def __repr__(self):
        return '<Type {}>'.format(self.typename)


class Visibility(db.Model):
    vid = db.Column(db.Integer, primary_key=True)
    vname = db.Column(db.String(50), unique=True)

    def __init__(self, vname):
        self.vname = vname

    def __repr__(self):
        return '<Visibility {}>'.format(self.vname)


class UG_has_V(db.Model):
    __tablename__ = 'ughasv'
    ugid = db.Column(db.Integer, db.ForeignKey('usergroup.ugid'))
    vid = db.Column(db.Integer, db.ForeignKey('visibility.vid'))

    __table_args__ = (
        db.PrimaryKeyConstraint('ugid', 'vid'),
        {},
    )

    def __init__(self, ugid, vid):
        self.ugid = ugid
        self.vid = vid

    def __repr__(self):
        return '<UG_has_V {} {}>'.format(self.ugid, self.vid)