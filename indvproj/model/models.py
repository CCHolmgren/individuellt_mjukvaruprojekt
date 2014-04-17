__author__ = 'Chrille'
from sqlalchemy.dialects import postgresql
#from sqlalchemy import db.Column, db.Integer, db.String, db.DateTime, db.ForeignKey, PrimaryKeyConstraint
from database import db
import datetime

class User(db.Model):
    __tablename__="user"
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(256))
    salt = db.Column(postgresql.BYTEA(24),nullable=False)
    postscreated = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    allcomments = db.relationship('Comment',backref='user',lazy='dynamic')
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    status = db.Column(db.Integer,db.ForeignKey('status.statusid'), default=1, nullable=False)
    posts = db.relationship('Post',backref='user',lazy='dynamic')
    groups = db.relationship('Group', backref='user', lazy='dynamic')

    def __init__(self, username, email, password, salt):
        self.username = username
        self.email = email
        self.password = password
        self.postscreated = 0
        self.comments = 0
        self.salt = salt

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.userid
    def __unicode__(self):
        return self.username

class Status(db.Model):
    __tablename__="status"
    statusid = db.Column(db.Integer, primary_key=True, nullable=False)
    statusname = db.Column(db.String(25), nullable=False, unique=True)

    def __repr__(self):
        return '<Status {}>'.format(self.statusname)

class Comment(db.Model):
    __tablename__="comment"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'))
    postid = db.Column(db.Integer, db.ForeignKey('post.postid'))
    commentid = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    content = db.Column(db.String(2000))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

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

    def __init__(self, ugname):
        self.ugname = ugname

    def __repr__(self):
        return '<User_Group {}>'.format(self.ugname)


class Category(db.Model):
    __tablename__="category"
    categoryid = db.Column(db.Integer, primary_key=True)
    categoryname = db.Column(db.String(100), unique=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, categoryname):
        self.categoryname = categoryname

    def __repr__(self):
        return '<Category {}>'.format(self.categoryname)


class Group(db.Model):
    __tablename__="group"
    groupid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    title = db.Column(db.String(250), nullable=False)

    def __init__(self, userid, title):
        self.userid = userid
        self.title = title

    def __repr__(self):
        return '<Group {} created by {}>'.format(self.title, self.userid)


class Post(db.Model):
    __tablename__="post"
    postid = db.Column(db.Integer, primary_key=True)
    createdby = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    timeposted = db.Column(db.DateTime, nullable=False)
    views = db.Column(db.Integer, default=0)
    content = db.Column(db.String(2000), nullable=False)
    typeid = db.Column(db.Integer, db.ForeignKey('type.typeid'), nullable=False)
    title = db.Column(db.String(250), nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    comments = db.relationship('Comment',backref='post',lazy='dynamic')

    def __init__(self, createdby, timeposted, content, typeid, title):
        self.createdby = createdby
        self.timeposted = timeposted
        self.content = content
        self.typeid = typeid
        self.title = title
        self.views = 0
        self.typeid = typeid

    def __repr__(self):
        return '<Post {}>'.format(self.title)


class Type(db.Model):
    __tablename__="type"
    typeid = db.Column(db.Integer, primary_key=True)
    typename = db.Column(db.String(50), unique=True)

    def __init__(self, typename):
        self.typename = typename

    def __repr__(self):
        return '<Type {}>'.format(self.typename)


class Visibility(db.Model):
    __tablename__="visibility"
    vid = db.Column(db.Integer, primary_key=True)
    vname = db.Column(db.String(50), unique=True)

    def __init__(self, vname):
        self.vname = vname

    def __repr__(self):
        return '<Visibility {}>'.format(self.vname)

"""
class UG_has_V(db.Model):
    __tablename__ = 'ughasv'
    ugid = db.Column(db.Integer, db.ForeignKey('usergroup.ugid'))
    vid = db.Column(db.Integer, db.ForeignKey('visibility.vid'))

    __table_args__ = (
        ('ugid', 'vid'),
        {},
    )

    def __init__(self, ugid, vid):
        self.ugid = ugid
        self.vid = vid

    def __repr__(self):
        return '<UG_has_V {} {}>'.format(self.ugid, self.vid)"""
ug_has_v = db.Table('ug_has_v',
                    db.Column('ugid',db.Integer,db.ForeignKey('usergroup.ugid')),
                    db.Column('vid', db.Integer,db.ForeignKey('visibility.vid'))
)

