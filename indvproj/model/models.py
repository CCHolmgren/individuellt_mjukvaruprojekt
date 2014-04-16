__author__ = 'Chrille'
from sqlalchemy.dialects import postgresql
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PrimaryKeyConstraint
from model.database import Base as db
import datetime

class User(db):
    __tablename__="user"
    userid = Column(Integer, primary_key=True)
    username = Column(String(120), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(256))
    salt = Column(postgresql.BYTEA(24),nullable=False)
    postscreated = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(Integer,ForeignKey('status.statusid'), default=1, nullable=False)

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

class Status(db):
    __tablename__="status"
    statusid = Column(Integer, primary_key=True, nullable=False)
    statusname = Column(String(25), nullable=False, unique=True)

    def __repr__(self):
        return '<Status {}>'.format(self.statusname)

class Comment(db):
    __tablename__="comment"
    id = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('user.userid'))
    postid = Column(Integer, ForeignKey('post.postid'))
    commentid = Column(Integer, ForeignKey('comment.id'), nullable=True)
    content = Column(String(2000))
    created = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, userid, postid, content, commentid=None):
        self.userid = userid
        self.postid = postid
        self.content = content
        self.commentid = commentid

    def __repr__(self):
        return '<Comment {}>'.format(self.content[:15])


class UserGroup(db):
    __tablename__ = 'usergroup'
    ugid = Column(Integer, primary_key=True)
    ugname = Column(String(50), unique=True)

    def __init__(self, ugname):
        self.ugname = ugname

    def __repr__(self):
        return '<User_Group {}>'.format(self.ugname)


class Category(db):
    __tablename__="category"
    categoryid = Column(Integer, primary_key=True)
    categoryname = Column(String(100), unique=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, categoryname):
        self.categoryname = categoryname

    def __repr__(self):
        return '<Category {}>'.format(self.categoryname)


class Group(db):
    __tablename__="group"
    groupid = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('user.userid'), nullable=False)
    title = Column(String(250), nullable=False)

    def __init__(self, userid, title):
        self.userid = userid
        self.title = title

    def __repr__(self):
        return '<Group {} created by {}>'.format(self.title, self.userid)


class Post(db):
    __tablename__="post"
    postid = Column(Integer, primary_key=True)
    createdby = Column(Integer, ForeignKey('user.userid'), nullable=False)
    timeposted = Column(DateTime, nullable=False)
    views = Column(Integer, default=0)
    content = Column(String(2000), nullable=False)
    typeid = Column(Integer, ForeignKey('type.typeid'), nullable=False)
    title = Column(String(250), nullable=False)
    created = Column(DateTime, default=datetime.datetime.utcnow)

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


class Type(db):
    __tablename__="type"
    typeid = Column(Integer, primary_key=True)
    typename = Column(String(50), unique=True)

    def __init__(self, typename):
        self.typename = typename

    def __repr__(self):
        return '<Type {}>'.format(self.typename)


class Visibility(db):
    __tablename__="visibility"
    vid = Column(Integer, primary_key=True)
    vname = Column(String(50), unique=True)

    def __init__(self, vname):
        self.vname = vname

    def __repr__(self):
        return '<Visibility {}>'.format(self.vname)


class UG_has_V(db):
    __tablename__ = 'ughasv'
    ugid = Column(Integer, ForeignKey('usergroup.ugid'))
    vid = Column(Integer, ForeignKey('visibility.vid'))

    __table_args__ = (
        PrimaryKeyConstraint('ugid', 'vid'),
        {},
    )

    def __init__(self, ugid, vid):
        self.ugid = ugid
        self.vid = vid

    def __repr__(self):
        return '<UG_has_V {} {}>'.format(self.ugid, self.vid)


