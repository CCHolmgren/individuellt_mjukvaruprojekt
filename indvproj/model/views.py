import _datetime

from flask.ext.classy import FlaskView, route
from models import User, Post, Collection, Category, collection_has_post

print('Importing db_session in model.views.py')
from indvproj import db_session
from flask_login import login_required, login_user, current_user, logout_user
from flask import render_template, redirect, flash, url_for, request
from forms import TextPostForm, RegistrationForm, LoginForm, CollectionForm, CategoryForm, DeletePostForm, \
    AddToCollectionForm
from markdown import markdown


__author__ = 'Chrille'


def getsalt(length):
    """
    Takes a length of the wanted salt and
    returns os.urandom(length)
    """
    import os

    return os.urandom(length)


def escape_text_and_create_markdown(unescaped_text):
    """
    Takes unsafe input and escapes it and converts it to safe html using markdown
    Safe_mode set to escapes doesn't remove anything and allows the users to post what ever they want without it getting
    removed.
    """
    return markdown(unescaped_text, safe_mode="escape")


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

        #print("User", User)
        #print("dir", dir(User))
        #print(current_user.moderator)
        #print(User.query.join(Post).filter(User.userid == Post.createdby).limit(10).all())
        #print(Post.query.join(User).filter(Post.createdby == User.userid).all())
        #print(current_user)
        #print(session)
        #print(dir(session))
        return render_template('main.html',
                               posts=Post.query.all(), categories=Category.query.all(), users=User.query.all())


class BlogView(FlaskView):
    def index(self):
        return CategoryView.get(self, 'blog')


class LoginView(FlaskView):

    @route('/', methods=['GET','POST'])
    def index(self):
        if current_user.is_active():
            return redirect(url_for('MainView:index'))

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
        post = Post.query.get(id)
        form = DeletePostForm()
        print(form)
        if post:
            return redirect(url_for('CategoryView:view_post', postid=post.postid,
                                    categoryname=Category.query.get(post.categoryid).categoryname))
        return render_template('post.html', post=Post.query.get(id), form=form)

    @route('/<postid>/delete', methods=['POST'])
    @login_required
    def delete(self, postid):
        try:
            post = Post.query.get(postid)
            db_session.delete(post)
            db_session.commit()
            return redirect(url_for('MainView:index'))
        except Exception as e:
            print(e)
            db_session.rollback()
            return redirect(url_for('MainView:index'))

    @route('/new/', methods=['GET', 'POST'])
    @login_required
    def new_post(self, categoryname=""):
        form = TextPostForm()
        form.categoryname.data = categoryname
        #linkform = LinkPostForm()
        if form.validate_on_submit():  # or linkform.validate_on_submit():
            try:
                category = Category.query.filter_by(categoryname=form.categoryname.data).first()
                post = Post(current_user.userid, _datetime.datetime.now(),
                            escape_text_and_create_markdown(form.content.data), 1,
                            form.title.data, category.categoryid)  # or Post(current_user.userid,
                #        _datetime.datetime.now(),
                #       linkform.link.data,
                #      1, linkform.title.data,
                #     linkform.categoryname.data)
                print(post)
                db_session.add(post)
                print(current_user.update(postscreated=current_user.postscreated + 1))
                db_session.commit()
                #assert Post.query.get(post.postid) > 0
                return redirect(
                    url_for("CategoryView:view_post", categoryname=category.categoryname, postid=post.postid))
            except Exception as e:
                flash('Something horrible happened')
                print(e)
                print('Damn')
                return redirect(url_for("PostView:new_post"))
        return render_template('new_post.html', form=form, categoryname=categoryname)  #, linkform=linkform)


class RegisterView(FlaskView):

    """def index(self):
        form = RegistrationForm(request.form)
        return render_template('create_user.html', form=form)"""

    @route('/', methods=['GET', 'POST'])
    def new_user(self):
        if current_user.is_active():
            return redirect(url_for('MainView:index'))

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
                #assert User.query.get(user.userid) > 0
                #login_user(user)
                flash("Thanks for registering!")
                flash("Now you can login and start using the site.")
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
            print(user.collections.all())
            return render_template('user.html',user=user)
        return render_template('user_missing.html', title="The user doesn't seem to exist")


class CategoryView(FlaskView):
    route_base = '/c'

    def index(self):
        categories = Category.query.all()
        print(categories)
        return render_template("all_categories.html", categories=categories)

    @route('/<categoryname>/')
    def get(self, categoryname):
        from sqlalchemy import func

        category = Category.query.filter(func.lower(Category.categoryname) == func.lower(categoryname)).first()
        print("Category:", category)
        print("Dir category:", dir(category))
        posts = category.posts.all()
        return render_template('category.html', category=category, posts=posts)

    @route('<categoryname>/p/<postid>')
    def view_post(self, categoryname, postid):
        from sqlalchemy import func

        form = DeletePostForm()
        post = Post.query.get(postid)
        print(post.categoryid)
        category = Category.query.filter(func.lower(Category.categoryname) == func.lower(categoryname)).first()
        print(category)
        if post.categoryid == category.categoryid:
            return render_template('post.html', post=Post.query.get(postid), form=form)
        print(Category.query.get(post.categoryid).categoryname, postid)
        return redirect(url_for('CategoryView:view_post', categoryname=Category.query.get(post.categoryid).categoryname,
                                postid=postid))

    @route('<categoryname>/p/new', methods=['GET', 'POST'])
    @login_required
    def new_post(self, categoryname):
        return PostView.new_post(self, categoryname)

        print(request.method)
        print('Were inside CategoryView:new_post')
        form = TextPostForm()
        form.categoryname.data = categoryname
        print(form)
        print(dir(form))
        #linkform = LinkPostForm(categoryname=id)
        if form.validate_on_submit():
            print('Inside the if')
            try:
                print('Inside the try')
                post = Post(current_user.userid, _datetime.datetime.now(),
                            escape_text_and_create_markdown(form.content.data), 1, form.title.data,
                            Category.query.filter_by(
                                categoryname=categoryname).first().categoryid)  #or Post(current_user.userid, _datetime.datetime.now(),linkform.link.data,1, linkform.title.data,id)
                print(post)
                db_session.add(post)
                current_user.postscreated += 1
                db_session.commit()
                print(post.postid)
                return redirect(url_for("CategoryView:get", categoryname=categoryname))
            except Exception as e:
                flash('Something horrible happened')
                print(e)
                print('Damn')
                return redirect(url_for("CategoryView:new_post", categoryname=categoryname))
        print('Returning')
        return render_template('new_post_category.html', form=form, categoryname=categoryname)

    @route('/new', methods=['GET', 'POST'])
    @login_required
    def new_category(self):
        print('We are inside CategoryView:new_category')
        form = CategoryForm()
        if form.validate_on_submit():
            try:
                potential_category = Category.query.filter_by(categoryname=form.categoryname.data.lower()).first()

                if potential_category:
                    flash("There is already a category with that categoryname")
                    return redirect(url_for("CategoryView:new_category"))

                category = Category(form.categoryname.data.lower(), form.categorytitle.data)
                db_session.add(category)
                db_session.commit()
                flash("The category was created")
                return redirect(url_for('CategoryView:get', categoryname=category.categoryname))
            except Exception as e:
                db_session.rollback()
                print('Something horrible happened')
                flash('Something horrible happened')
                print(repr(e), e)
                redirect(url_for("CategoryView:new_category"))
        return render_template('create_category.html', form=form, title="Create a new category")

    @route('<categoryname>/moderators/add', methods=['GET', 'POST'])
    @login_required
    def add_moderator(self, categoryname):
        """
        Add moderators to a category
        :param categoryname:
        :return:
        """
        return render_template('add_moderators.html')


class CollectionView(FlaskView):
    @login_required
    def index(self):
        return render_template('collections.html', title="Displays your collections",
                               collections=current_user.collections)

    @route('/<collectionid>/delete', methods=['POST'])
    @login_required
    def delete(self, collectionid):
        try:
            collection = Collection.query.get(collectionid)
            db_session.delete(collection)
            db_session.commit()
            flash("The collection was removed")
            return redirect(url_for('MainView:index'))
        except Exception as e:
            print(e)
            db_session.rollback()
            return redirect(url_for('MainView:index'))

    @route('/<collectionid>/add_link', methods=['POST'])
    @login_required
    def add_link(self, collectionid):
        addform = AddToCollectionForm()
        if addform.validate_on_submit():
            oldpost = Post.query.get(addform.link.data)

            print(collection_has_post)
            collection = Collection.query.get(collectionid)
            collection.posts.append(oldpost)
            db_session.commit()
            print(collection.posts.all())
            """
            print(collection)
            print(collection_has_post.insert().values(cid=collection.groupid, pid=addform.link.data))
            stmt = collection_has_post.insert().values(cid=collection.groupid, pid=addform.link.data)
            print(db.engine.execute(stmt))
            #db_session.commit()
            print(collection_has_post)
            print(dir(collection_has_post))
            """
            return redirect(url_for('MainView:index'))

    @login_required
    def get(self, id):
        collection = Collection.query.get(id)
        deleteform = DeletePostForm()
        addform = AddToCollectionForm()
        if collection:
            print(collection)
            print(collection.userid)
            print(current_user.userid)
            if current_user.userid == collection.userid:
                return render_template('collection.html', collection=collection, title=collection.title, \
                                       deleteform=deleteform, addform=addform)
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