import _datetime

from flask.ext.classy import FlaskView, route
from models import User, Post, Collection, Category
from database import db_session
from flask_login import login_required, login_user, current_user, logout_user
from flask import render_template, redirect, flash, url_for
from forms import TextPostForm, RegistrationForm, LoginForm, CollectionForm, LinkPostForm, CategoryForm


__author__ = 'Chrille'


def getsalt(length):
    """
    Takes a length of the wanted salt and
    returns os.urandom(length)
    """
    import os

    return os.urandom(length)


def encrypt(password):
    """
    Takes a password, encodes it in utf-8 and
    then uses the haslib sha512 function to encrypt it.
    The hexdigest and the salt used is then returned.
    """
    import hashlib
    password = password.encode('utf-8')
    salt = getsalt(128)
    for i in range(10000):
        password = hashlib.sha512(password + salt).digest()
    return password, salt


def check_password(string_password,salt):
    """
    Checks a password using it's salt
    """
    import hashlib

    print(string_password, salt)
    password = string_password.encode('utf-8')
    for i in range(10000):
        password = hashlib.sha512(password + salt).digest()
    return password


class MainView(FlaskView):
    route_base = '/'

    def index(self):
        #print(Post.query.limit(10).all())
        print(User.query.join(Post).filter(User.userid == Post.createdby).limit(10).all())
        print(Post.query.join(User).filter(Post.createdby == User.userid).all())
        print(dir(current_user))
        return render_template('main.html',
                               posts=Post.query.limit(10).all())


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
    def logout(self):
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
        form = TextPostForm()
        linkform = LinkPostForm()
        if form.validate_on_submit() or linkform.validate_on_submit():
            try:
                post = Post(current_user.userid, _datetime.datetime.now(), form.content.data, 1,
                            form.title.data, form.categoryname.data) or Post(current_user.userid,
                                                                             _datetime.datetime.now(),
                                                                             linkform.link.data,
                                                                             1, linkform.title.data,
                                                                             linkform.categoryname.data)
                print(post)
                db_session.add(post)
                db_session.commit()
                redirect(url_for("PostView:get",id=post.postid))
            except Exception as e:
                flash('Something horrible happened')
                print(e)
                print('Damn')
                redirect(url_for("PostView:new_post"))
        return render_template('new_post.html', form=form, linkform=linkform)


class RegisterView(FlaskView):

    """def index(self):
        form = RegistrationForm(request.form)
        return render_template('create_user.html', form=form)"""

    @route('/', methods=['GET', 'POST'])
    def new_user(self):
        form = RegistrationForm()
        if form.validate_on_submit():
            try:
                #print(*encrypt(form.password.data))

                potentialUser = User.query.filter_by(username=form.username.data).first()
                print(potentialUser)

                if potentialUser:
                    flash("The username already exists.")
                    redirect(url_for("RegisterView:new_user"))

                if User.query.filter_by(email=form.email.data).first():
                    flash("The email already exists.")
                    redirect(url_for("RegisterView:new_user"))

                user = User(form.username.data, form.email.data, *encrypt(form.password.data))
                db_session.add(user)
                db_session.commit()
                login_user(user)
                flash("Thanks for registering")
                return redirect(url_for('MainView:index'))
            except Exception as e:
                db_session.rollback()
                flash('Something horrible happened')
                print(repr(e))
                redirect(url_for("RegisterView:new_user"))
        return render_template('create_user.html', form=form, title="Create a new user")


class UserView(FlaskView):
    route_base = '/u'

    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if user is not None:
            return render_template('user.html',user=user)
        return render_template('user_missing.html', title="The user doesn't seem to exist")


class CategoryView(FlaskView):
    def get(self, categoryname):
        category = Category.query.filter_by(categoryname=categoryname)
        print("Category:", category)
        print("Dir category:", dir(category))
        posts = category.posts.all()
        return render_template('category.html', category=category, posts=posts)

    @route('<categoryname>/p/<postid>')
    @login_required
    def view_post(self, categoryname, postid):
        return render_template('post.html', post=Post.query.get(postid))

    @route('<categoryname>/p/new', methods=['GET', 'POST'])
    @login_required
    def new_post(self, categoryname):
        print('Were inside CategoryView:new_post')
        form = TextPostForm()
        print(form)
        print(dir(form))
        #linkform = LinkPostForm(categoryname=id)
        if form.validate_on_submit():
            print('Inside the if')
            try:
                print('Inside the try')
                post = Post(current_user.userid, _datetime.datetime.now(), form.content.data, 1, form.title.data,
                            categoryname)  #or Post(current_user.userid, _datetime.datetime.now(),linkform.link.data,1, linkform.title.data,id)
                print(post)
                db_session.add(post)
                db_session.commit()
                print(post.postid)
                return redirect(url_for("CategoryView:get", categoryname=categoryname))
            except Exception as e:
                flash('Something horrible happened')
                print(e)
                print('Damn')
                return redirect(url_for("CategoryView:new_post", categoryname=categoryname))
        print('Returning')
        return render_template('new_post.html', form=form, categoryname=categoryname)

    @route('/new', methods=['GET', 'POST'])
    @login_required
    def new_category(self):
        print('We are inside CategoryView:new_category')
        form = CategoryForm()
        if form.validate_on_submit():
            try:
                category = Category(form.categoryname.data)
                db_session.add(category)
                db_session.commit()
                flash("The category was created")
                return redirect(url_for('CategoryView:get', categoryname=category.categoryid))
            except Exception as e:
                db_session.rollback()
                print('Something horrible happened')
                flash('Something horrible happened')
                print(repr(e), e)
                redirect(url_for("CategoryView:new_category"))
        return render_template('create_category.html', form=form, title="Create a new category")


class CollectionView(FlaskView):
    route_base = '/c'

    def index(self):
        return render_template('not_verified_collection.html', title="You are not eligible to view this collection")

    @login_required
    def get(self, id):
        collection = Collection.query.get(id)
        if collection:
            print(collection)
            if current_user.userid == collection.userid:
                return render_template('collection.html', collection=collection, title=collection.title)
            return render_template('not_verified_collection.html', title="You are not eligible to view this collection")
        return render_template('not_verified_collection.html', title="You are not eligible to view this collection")

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
        return render_template('create_collection.html', form=form, title="Create a new collection")