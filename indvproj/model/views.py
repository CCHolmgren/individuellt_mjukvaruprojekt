from flask.ext.classy import FlaskView, route
import flask.ext.classy
from models import User, Post
from database import db_session
from loginmanager import login_manager
from flask_login import login_required, login_user
from flask import render_template, request, redirect, flash, url_for
from forms import NewPostForm, RegistrationForm, LoginForm
import _datetime

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
    return hashlib.sha512(password + salt).hexdigest()#,salt

def check_password(string_password,salt):
    import hashlib
    print(string_password, salt)
    string_password = string_password.encode('utf-8')
    return hashlib.sha512(string_password+salt).hexdigest()

class MainView(FlaskView):
    route_base = '/'

    def index(self):
        #print(Post.query.limit(10).all())
        return render_template('main.html',message='Du accessade sidan med get istället för post',posts=Post.query.limit(10).all())

class LoginView(FlaskView):

    @route('/', methods=['GET','POST'])
    def index(self):
        form = LoginForm(request.form)
        """, password=encrypt(form.password.data)"""
        if request.method == 'POST' and form.validate():
            user = User.query.filter_by(username=form.username.data,password=check_password(form.password.data,User.query.filter(User.username == form.username.data).first().salt)).first()
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for("MainView:index"))
        return render_template("login.html",form=form)


class PostView(FlaskView):

    def get(self, id):
        #return "Hello from PostView:get"
        return render_template('post.html', post=Post.query.get_or_404(id))

    @route('/new')
    @login_required
    def new_post(self):
        form = NewPostForm(request.form)
        if request.method == 'POST' and form.validate():
            try:
                post = Post(5,_datetime.datetime.now(),form.content.data,1,form.title.data)
                print(post)
                db_session.add(post)
                db_session.commit()
                redirect(url_for("PostView:get",id=post.postid))
            except Exception:
                flash('Something horrible happened')
                print('Damn')
                redirect(url_for("PostView:new_post"))
        return render_template('new_post.html', form=form)

class RegisterView(FlaskView):

    def get(self):
        form = RegistrationForm(request.form)
        return render_template('create_user.html', form=form)

    def post(self):
        form = RegistrationForm(request.form)
        if form.validate:
            try:
                user = User(form.username.data, form.email.data, *encrypt(form.password.data))
                db_session.add(user)
                db_session.commit()
                login_user(user)
                flash("Thanks for registering")
                return redirect(url_for('MainView:index'))
            except Exception as e:
                flash('Something horrible happened')
                print(e)
                redirect(url_for("MainView:register"))