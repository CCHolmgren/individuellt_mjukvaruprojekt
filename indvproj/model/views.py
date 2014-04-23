import _datetime

from flask.ext.classy import FlaskView, route
from models import User, Post, Collection
from database import db_session
from flask_login import login_required, login_user, current_user, logout_user
from flask import render_template, redirect, flash, url_for
from forms import NewPostForm, RegistrationForm, LoginForm, CollectionForm


__author__ = 'Chrille'

def encrypt(password):
    """
    Takes a password, encodes it in utf-8 and
    then uses the haslib sha512 function to encrypt it.
    The hexdigest and the salt used is then returned.
    """

    import os
    import hashlib
    password = password.encode('utf-8')
    salt = os.urandom(24)
    return hashlib.sha512(password + salt).hexdigest(),salt

def check_password(string_password,salt):
    import hashlib
    print(string_password, salt)
    string_password = string_password.encode('utf-8')
    return hashlib.sha512(string_password+salt).hexdigest()

class MainView(FlaskView):
    route_base = '/'

    def index(self):
        #print(Post.query.limit(10).all())
        print(User.query.join(Post).filter(User.userid == Post.createdby).limit(10).all())
        print(Post.query.join(User).filter(Post.createdby == User.userid).all())
        print(dir(current_user))
        return render_template('main.html', message='Du accessade sidan med get istället för post',
                               posts=Post.query.limit(10).all(), user=current_user if current_user is not None else {})


class LoginView(FlaskView):

    @route('/', methods=['GET','POST'])
    def index(self):
        form = LoginForm()
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                user = User.query.filter_by(username=form.username.data,password=check_password(form.password.data,User.query.filter(User.username == form.username.data).first().salt)).first()
                if user is not None:
                    login_user(user, remember=False)
                    flash("Logged in successfully.")
                    return redirect(url_for("MainView:index"))
            flash('The login failed, check the username and password and try again')
            return redirect(url_for('LoginView:index'))
        return render_template("login.html",form=form)


class LogoutView(FlaskView):
    @login_required
    def index(self):
        logout_user()
        flash('You were logged out')
        return redirect(url_for("MainView:index"))


class PostView(FlaskView):
    route_base = '/p'

    def get(self, id):
        #return "Hello from PostView:get"
        return render_template('post.html', post=Post.query.get(id))

    @route('/new', methods=['GET','POST'])
    @login_required
    def new_post(self):
        form = NewPostForm()
        if form.validate_on_submit():
            try:
                post = Post(current_user.userid,_datetime.datetime.now(),form.content.data,1,form.title.data)
                print(post)
                db_session.add(post)
                db_session.commit()
                redirect(url_for("PostView:get",id=post.postid))
            except Exception as e:
                flash('Something horrible happened')
                print(e)
                print('Damn')
                redirect(url_for("PostView:new_post"))
        return render_template('new_post.html', form=form)

class RegisterView(FlaskView):

    """def index(self):
        form = RegistrationForm(request.form)
        return render_template('create_user.html', form=form)"""

    @route('/', methods=['GET', 'POST'])
    def new_user(self):
        form = RegistrationForm()
        if form.validate_on_submit():
            try:
                print(*encrypt(form.password.data))
                user = User(form.username.data, form.email.data, *encrypt(form.password.data))
                db_session.add(user)
                db_session.commit()
                login_user(user)
                flash("Thanks for registering")
                return redirect(url_for('MainView:index'))
            except Exception as e:
                db_session.rollback()
                flash('Something horrible happened')
                repr(e)
                redirect(url_for("RegisterView:new_user"))
        return render_template('create_user.html', form=form)

class UserView(FlaskView):
    route_base = '/u'

    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if user is not None:
            return render_template('user.html',user=user)
        return render_template('user_missing.html')

class CollectionView(FlaskView):
    route_base = '/c'

    def index(self):
        return render_template('not_verified_collection.html')

    @login_required
    def get(self, id):
        if Collection.query.get(id):
            print(Collection.query.get(id))
            if current_user.userid == Collection.query.get(id).userid:
                return render_template('collection.html', collection=Collection.query.get(id))
            return render_template('not_verified_collection.html')
        return render_template('not_verified_collection.html')

    @route('/new', methods=['GET', 'POST'])
    @login_required
    def new_collection(self):
        form = CollectionForm()
        if form.validate_on_submit():
            try:
                collection = Collection(current_user.userid, form.title.data)
                db_session.add(collection)
                db_session.commit()
                flash("The collection was created")
                return redirect(url_for('CollectionView:get', id=collection.groupid))
            except Exception as e:
                db_session.rollback()
                flash('Something horrible happened')
                print(repr(e), e)
                redirect(url_for("CollectionView:new_collection"))
        return render_template('create_collection.html', form=form)