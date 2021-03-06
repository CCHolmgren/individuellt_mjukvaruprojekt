from indvproj import db, app
from models import Type, Status, User

__author__ = 'Chrille'

"""This file is such a cheat. Somehow the models didn't get created, probably because of something with db and how it
 is set up. So I just include all of them here, which is a bit annoying since I need to do that all the time if I want
to change the models. Will have to have some way to backup the data so I do not need to recreate it all the time."""

x = """
collection_has_post = db.Table('collection_has_post',
                               db.Column('cid', db.Integer, db.ForeignKey('collection.groupid')),
                               db.Column('pid', db.Integer, db.ForeignKey('post.postid'))
)
category_has_moderator = db.Table('category_has_moderator',
                                  db.Column('categoryid', db.Integer, db.ForeignKey('category.categoryid')),
                                  db.Column('userid', db.Integer, db.ForeignKey('user.userid'))
)


class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(postgresql.BYTEA, nullable=False)
    salt = db.Column(postgresql.BYTEA, nullable=False)
    postscreated = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    allcomments = db.relationship('Comment', backref='user', lazy='dynamic')
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    status = db.Column(db.Integer, db.ForeignKey('status.statusid'), default=1, nullable=True)
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    collections = db.relationship('Collection', backref='user', lazy='dynamic')
    moderator = db.relationship('Category', secondary=category_has_moderator,
                                backref=db.backref('moderators', lazy='dynamic'))

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
    statusid = db.Column(db.Integer, primary_key=True, nullable=False)
    statusname = db.Column(db.String(25), nullable=False, unique=True)

    def __init__(self, statusname):
        self.statusname = statusname

    def __repr__(self):
        return '<Status {}>'.format(self.statusname)


class Comment(db.Model):
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
    ugid = db.Column(db.Integer, primary_key=True)
    ugname = db.Column(db.String(50), unique=True)

    def __init__(self, ugname):
        self.ugname = ugname

    def __repr__(self):
        return '<User_Group {}>'.format(self.ugname)


ug_has_v = db.Table('ug_has_v',
                    db.Column('ugid', db.Integer, db.ForeignKey('user_group.ugid')),
                    db.Column('vid', db.Integer, db.ForeignKey('visibility.vid'))
)


class Category(db.Model):
    categoryid = db.Column(db.Integer, primary_key=True)
    categoryname = db.Column(db.String(100), unique=True, nullable=False)
    categorytitle = db.Column(db.String(100))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    def __init__(self, categoryname, title="Default title"):
        self.categoryname = categoryname
        self.categorytitle = title

    def __repr__(self):
        return '<Category {}>'.format(self.categoryname)


class Collection(db.Model):
    groupid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    title = db.Column(db.String(250), nullable=False)

    def __init__(self, userid, title):
        self.userid = userid
        self.title = title

    def __repr__(self):
        return '<Collection {} created by {}, collectionid: {}>'.format(self.title, self.user.username, self.groupid)


class Post(db.Model):
    postid = db.Column(db.Integer, primary_key=True)
    createdby = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    timeposted = db.Column(db.DateTime, nullable=False)
    views = db.Column(db.Integer, default=0)
    content = db.Column(db.String(2000), nullable=False)
    typeid = db.Column(db.Integer, db.ForeignKey('type.typeid'), nullable=True)
    title = db.Column(db.String(250), nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    posts = db.relationship('Collection', secondary=collection_has_post,
                            backref=db.backref('collections', lazy='dynamic'))
    categoryid = db.Column(db.Integer, db.ForeignKey('category.categoryid'), nullable=False)

    def __init__(self, createdby, timeposted, content, typeid, title, categoryid):
        self.createdby = createdby
        self.timeposted = timeposted
        self.content = content
        self.typeid = typeid
        self.title = title
        self.views = 0
        self.typeid = typeid
        self.categoryid = categoryid

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


var =
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
        return '<UG_has_V {} {}>'.format(self.ugid, self.vid)
ug_has_v = db.Table('ug_has_v',
                    db.Column('ugid',db.Integer,db.ForeignKey('usergroup.ugid')),
                    db.Column('vid', db.Integer,db.ForeignKey('visibility.vid'))
)

collection_has_post = db.Table('collection_has_post',
                               db.Column('cid',db.Integer, db.ForeignKey('collection.groupid')),
                               db.Column('pid',db.Integer, db.ForeignKey('post.postid'))
)
"""


def create():
    db.metadata.create_all(bind=db.engine)


def create_and_run():
    print('Running create_and_run')
    print(db.metadata)
    print(dir(db.metadata))

    db.metadata.drop_all(bind=db.engine)
    db.metadata.create_all(bind=db.engine)
    with app.app_context():
        t = Type("Normal")
        s = Status("Normal")
        u = User("Ravengenocide", "christoffer.holmgren@gmail.com",
                 b'\x1d\tT\xa8\xfdR\xff]\xdb\x17\x0f\xeask\x99\xbcX\xe2\xb4n\x1e\xe5\xbcl>\xd0\xf0G\x9dn\x8c\x98h{&\xc2>m\xf7\xb1w\xd4\xf5\x0b\x05\xe4\xa3\xdb\x9f\x8f\xe4\xa9!5\xad\xef\xacP\xd1a\x84*\x0f\xe0',
                 b'\x9af\xa0\xdd\x1b\xca\xcf0\x87$\xd3\x0b\xb6\xcc\xd9\xf3\xe5\xc8}\xa9C5\x006\x01\\$\x07\x0c\xc7,\xcc\xe6H\xb1\xa2\xac\nr\xad\xc9\x8ew\xa4\x953\x02[\x16A\x90|\xa24LZ\xe1\xb1q\x1b\x9a\xc8\xc44\x98\x9d\xa3<\xe9\xdb|x\x7f\x06\xeb\xf8k:\x10\x15\xd3\x1b\x9f\x93\x0c\x94<\xdeA>\x97?\xac3\xb2\xd6\xfd\xdc_\xdfB \xec\xec\x8at\xd3\xe6\xbd\xb6\xfa\xf0\xec\xf3\xae}\xd6X!\xd9\xf7\x96\xea\n\x0c\x8fG@',
                 4)

        db.session.add(t)
        db.session.add(s)
        db.session.commit()
        db.session.add(u)
        db.session.add(Status("Banned"))
        db.session.add(Status("Shadow-banned"))
        db.session.add(Status("Administrator"))
        db.session.add(Status("Deleted"))
        db.session.add(Status("Moderator-posts only"))
        db.session.add(Status("Administrator-posts only"))
        db.session.add(Type("Moderator-post"))
        db.session.add(Type("Admin-post"))
        db.session.commit()
    """
    with app.app_context():
        print(db)
        print(dir(db))
        print('Before try')
        try:
            print('after try')
            db.drop_all()
            print('after drop_all')
            db.create_all()
            print('after create_all')
            print('Dropped and then created all tables, hopefully')
            t = Type("Normal")
            s = Status("Normal")
            db.session.add(t)
            db.session.add(s)
            db.session.commit()
        except Exception as e:
            print(e)"""


if __name__ == '__main__':
    create_and_run()
