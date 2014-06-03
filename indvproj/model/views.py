import datetime

from flask.ext.classy import FlaskView, route
from .models import User, Post, Collection, Category, Comment, Link

print('Importing db_session in model.views.py')
from indvproj import db_session
from flask_login import login_required, login_user, current_user, logout_user
from flask import render_template, redirect, flash, url_for, g, request, abort
from .Forms import TextPostForm, RegistrationForm, LoginForm, CollectionForm, CategoryForm, DeletePostForm, \
    AddToCollectionForm, AddModeratorForm, CommentForm, EditPostForm
from markdown import markdown

__author__ = 'Chrille'

#This is the highest value that we dare put into the selectors since they will creash if they get a larger value than this
MAXINT = 2147483647


def getsalt(length):
    """
    Takes a length of the wanted salt and
    returns os.urandom(length)
    """
    import os

    return os.urandom(length)


def decode_base64_with_split(base64string):
    """
    Takes a base64 stirng, and decodes it. It is then split with '-' so that we get the postid and random value
    :param base64string:
    :return: Returns postid, random
    """
    import base64

    try:
        return base64.b64decode(bytes(base64string, 'ascii')).decode('utf-8').split('-')
    except base64.binascii.Error as e:
        return abort(404)


def escape_text_and_create_markdown(unescaped_text, safe_mode="escape"):
    """
    Takes unsafe input and escapes it and converts it to safe html using markdown
    Safe_mode set to escapes doesn't remove anything and allows the users to post what ever they want without it getting
    removed.
    """
    return markdown(unescaped_text, safe_mode=safe_mode, extensions=["sane_lists", "tables"])


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


def check_password(string_password, salt):
    """
    Checks a password using it's salt
    """
    import hashlib

    print(string_password, salt)
    password = string_password.encode('utf-8')
    for i in range(10000):
        password = hashlib.sha512(password + salt).digest()
    return password


def is_url(user_input):
    import re

    return re.match('^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+&', user_input)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text, error
            ))


def allowed_to_add_moderators(user, category):
    """
    A user can add a moderator to a category if the user is a moderator himself, or an admin
    :param user: User doing the adding
    :param category: Category to add to
    :return:
    """
    if user in category.moderators or user.status == 4:
        return True
    return False


def allowed_to_remove_post(user, post):
    """
    A user who created the post, a moderator of the category or an admin can remove a post
    :param user: The user doing the removal
    :param post: The post to remove
    :return: True if the user is allowed to remove the post else False
    """
    if user.userid == post.createdby:
        return True
    elif user in post.category.moderators:
        return True
    elif user.status == 4:
        return True
    return False


def allowed_to_remove_category(user, category):
    """
    We don't want anyone except admins removing categories, just send a message to them if you want to remove it
    :param user: the user that is doing the removal
    :param category: category to remove
    :return: True if user.status is 4, i.e. administrator else False
    """
    if user.status == 4:
        return True
    return False


def allowed_to_post_in_category(user, category):
    """

    :param user:
    :param category:
    :return:
    """
    #If the user is an admin
    if user.status == 4:
        return True
    #If the user is a moderator
    elif user in category.moderators:
        return True
    #If the category is a normal category
    elif category.statusid == 1:
        return True
    #All other cases
    else:
        return False


# noinspection PyTypeChecker
class AboutView(FlaskView):
    def index(self):
        return CategoryView.get(CategoryView(), 'about')


class MainView(FlaskView):
    """
    MainView handles ourpage.tld/
    I.e: takes care of the frontpage
    """
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
        """
        Index is the mainpage of the site.
        You redirect here if you want to get back to the start of the site.

        :return: rendered template main.html with the options inserted
        """
        #print(Comment.query.all())  #.children.append(Comment(userid=1, content="Hello"))
        #print(dir(Comment.query.first()))
        #print(Comment.query.first().ignored_list.all())
        #ui = UserIgnore(Comment.query.first(), Comment(userid=1, content=""))
        #db_session.add(ui)
        #db_session.commit()
        #Comment.query.first().ignored_list.append(Comment(userid=1, content=""))
        #db_session.commit()
        #raise Exception()

        if getattr(current_user, "status", None) != 4:
            return render_template('main.html',
                                   posts=Post.query.filter(Post.statusid != 5).limit(100).all()[::-1],
                                   categories=Category.query.all(),
                                   users=User.query.limit(100).all())
        else:
            return render_template('main.html',
                                   posts=Post.query.limit(100).all()[::-1], categories=Category.query.all(),
                                   users=User.query.limit(100).all())


# noinspection PyTypeChecker
class BlogView(FlaskView):
    """
    Shorthand for /c/blog
    """

    def index(self):
        """
        Takes care of /blog/ and returns CategoryView.get('blog')
        """
        # noinspection PyCallByClass
        return CategoryView.get(CategoryView(), 'blog')


class LoginView(FlaskView):
    """
    The LoginView takes care of login via Flask_login
    Does the error checking and the password checking
    """

    @route('/', methods=['GET', 'POST'])
    def index(self):
        """
        This is the login page and it handels evertyhing around login.
        Checks if the user exists and logs it in, otherwise it handles the other cases.

        :return: Either a redirect to MainView, LoginView:index again or a rendered template of login.html
        """
        from sqlalchemy import func

        if current_user.is_active():
            return redirect(url_for('MainView:index'))

        form = LoginForm()

        if form.validate_on_submit():
            potentialuser = User.query.filter(func.lower(User.username) == func.lower(form.username.data)).first()

            if potentialuser:
                #Instead of doing a odd query, just do this instead
                if potentialuser.password == check_password(form.password.data, potentialuser.salt):
                    login_user(potentialuser)
                    flash("Logged in successfully.")
                    return redirect(url_for("MainView:index"))

            flash('The login failed, check the username and password and try again')
            return redirect(url_for('LoginView:index'))

        return render_template("login.html", form=form)


class LogoutView(FlaskView):
    """
    LOgs the user out via Flask_login
    """

    @route('/')
    @login_required
    def logout(self):
        logout_user()
        flash('You were logged out')
        return redirect(url_for("MainView:index"))


class PostView(FlaskView):
    """
    PostView handles everything that is centered around specific posts such as deletion and commenting,
    and also creation of new posts
    """
    # TODO: Add so that we can see what user did what, such as removal of the post and edited and so on
    # I.e. logging
    # TODO: Change so that it's possible to make a post visible again

    route_base = '/p'

    def get(self, postid):
        """
        Redirects to CategoryView:view_post if the post has a category (exists)
        Else it renders template post.html
        :param postid: The postid of the post to view
        :return: Either a redirect to CategoryView:view_post if the post exists, or a rendered template of post.html
        """

        post = Post.query.get_or_404(postid)

        #print(dir(Comment.query.filter(Comment.commentid in Post.comments)))

        #form = DeletePostForm()
        #print(form)
        # I.E. deleted
        if post.statusid == 5 and getattr(current_user, "status", None) != 4:
            return abort(404)
        return redirect(url_for('CategoryView:view_post', postid=post.postid,
                                categoryname=Category.query.get(post.categoryid).categoryname))
        #return render_template('post.html', post=Post.query.get(postid), form=form)

    @route('/<postid>/remove', methods=['POST'])
    @login_required
    def remove(self, postid):
        try:
            post = Post.query.get(postid)
            category = Category.query.get(post.categoryid)
            if current_user.allowed_to_remove_post(post):
                post.statusid = 5
                db_session.commit()
                flash('The post was removed.')
                return redirect(url_for('CategoryView:get', categoryname=category.categoryname))
            else:
                flash(
                    "You weren't allowed to remove this post, maybe you aren't the posts creator,"
                    "or you aren't a moderator.")
                return redirect(url_for('MainView:index'))
        except Exception as e:
            print(e)
            db_session.rollback()
            return redirect(url_for('MainView:index'))

    @route('/<postid>/delete', methods=['POST'])
    @login_required
    def delete(self, postid):
        """
        Deletes the post associated with the postid, but only if the user is the created or a moderator of the category
        This is a permanent deletion, it won't be marked invisible or something, it will get deleted
        Use with caution

        :param postid: Postid of post to delete
        :return: Redirects to MainView:index all the time
        """
        try:
            post = Post.query.get(postid)
            category = Category.query.get(post.categoryid)
            if current_user.allowed_to_remove_post(post):
                db_session.delete(post)
                db_session.commit()
                flash('The post was deleted.')
                return redirect(url_for('CategoryView:get', categoryname=category.categoryname))
            else:
                flash(
                    "You weren't allowed to delete this post, maybe you aren't the posts creator,"
                    "or you aren't a moderator.")
                return redirect(url_for('MainView:index'))
        except Exception as e:
            print(e)
            db_session.rollback()
            return redirect(url_for('MainView:index'))

    @route('/<postid>/comment', methods=['POST'])
    @login_required
    def comment(self, postid):
        """
        Handles commenting on a post. At this time it's only possible to have top-level comments,
        but that should change in the future to include child comments

        :param postid: Postid to comment on
        :return:
        """
        print("Inside of comment")
        form = CommentForm()
        if form.validate_on_submit():
            print("Inside of validate_on_submit")
            post = Post.query.get(postid)
            if post:
                print("Inside if post:")
                post.comments.append(
                    Comment(content=escape_text_and_create_markdown(form.content.data), postid=post.postid,
                            userid=current_user.userid))
                db_session.commit()
                flash("The comment was posted")
                return redirect(url_for('PostView:get', postid=postid))
            flash("That post does not exist.")
            return redirect(url_for("MainView:index"))

    @route('/<postid>/<commentid>/remove', methods=['POST'])
    @login_required
    def remove_comment(self, postid, commentid):
        try:
            post = Post.query.get(postid)
            comment = Comment.query.get(commentid)
            if current_user.allowed_to_remove_comment(comment, post):
                comment.statusid = 5
                db_session.commit()
                flash('The comment was removed.')
                return redirect(url_for('PostView:get', postid=postid))
            else:
                flash(
                    "You weren't allowed to remove this comment, maybe you aren't the comments creator,"
                    "or you aren't a moderator.")
                return redirect(url_for('PostView:get', postid=postid))
        except Exception as e:
            print(e)
            db_session.rollback()
            return redirect(url_for('PostView:get', postid=postid))

    @route('/<postid>/<commentid>/delete', methods=['POST'])
    @login_required
    def delete_comment(self, postid, commentid):
        try:
            post = Post.query.get(postid)
            comment = Comment.query.get(commentid)
            if current_user.allowed_to_remove_comment(comment, post):
                db_session.delete(comment)
                db_session.commit()
                flash('The comment was deleted.')
                return redirect(url_for('PostView:get', postid=postid))
            else:
                flash(
                    "You weren't allowed to delete this comment, maybe you aren't the comments creator,"
                    "or you aren't a moderator.")
                return redirect(url_for('PostView:get', postid=postid))
        except Exception as e:
            print(e)
            db_session.rollback()
            return redirect(url_for('PostView:get', postid=postid))

    @route('/<postid>/<commentid>/comment', methods=['POST'])
    @login_required
    def comment_on_comment(self, postid, commentid):
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment.query.get(commentid)
            if comment:
                comment.children.append(
                    Comment(content=escape_text_and_create_markdown(form.content.data), userid=current_user.userid))
                #, parent=commentid))
                #newcomment = Comment(content=form.content.data, userid=current_user.userid, parent=commentid)
                #db_session.add(newcomment)
                db_session.commit()
                #print(newcomment.commentid)
                #db.engine.execute(comment_has_comment.insert().values
                ## (parentcommentid=commentid, childcommentid=newcomment.commentid))

                #comment.children.append(Comment(content=form.content.data,
                ## postid=postid, userid=current_user.userid,parent=1))
                #db_session.commit()

                flash("The comment was created")
                return redirect(url_for('PostView:get', postid=postid))

    @route('/<postid>/<commentid>')
    @login_required
    def comment_on(self, postid, commentid):
        form = CommentForm()
        Comment.query.get(commentid)
        if int(commentid) > MAXINT:
            return abort(404)
        return render_template('comment_on_comment.html', form=form, parentcomment=Comment.query.get(commentid),
                               postid=postid)

    @route('/new/', methods=['GET', 'POST'])
    @login_required
    def new_post(self, categoryname=""):
        """
        Allow you to create new posts in a category. The inputbox with categoryname will have default value\
         of categoryname

        :param categoryname: A potential categoryname to be set in the form, which can be used when you want to display\
        that you are in [categoryname] and the box is already inputted
        :return:
        """
        print("We are inside new_post of PostView")
        form = TextPostForm()
        if not form.categoryname.data:
            form.categoryname.data = categoryname
        #linkform = LinkPostForm()
        print(form.categoryname.data)
        if current_user.status == 4:
            # Ugly hack to remove the length requirement if the user is a moderator
            form.title.validators = form.title.validators[1:]
            form.content.validators = form.content.validators[1:]

        if form.validate_on_submit():  # or linkform.validate_on_submit():
            print("Inside validate")
            category = Category.query.filter_by(categoryname=form.categoryname.data).first()
            if category:
                if current_user.allowed_to_post_in_category(category):
                    post = Post(current_user.userid, datetime.datetime.now(),
                                escape_text_and_create_markdown(form.content.data), 1,
                                form.title.data, category.categoryid, non_markdown=form.content.data)

                    print(post)
                    db_session.add(post)
                    current_user.postscreated += 1
                    db_session.commit()
                    #assert Post.query.get(post.postid) > 0
                    return redirect(
                        url_for("CategoryView:view_post", categoryname=category.categoryname, postid=post.postid))
                flash("You are not allowed to post in that category!")
                return redirect(url_for('PostView:new_post'))
            flash('The category cant be found')
            return redirect(url_for('PostView:new_post'))
        print(form.errors)
        return render_template('new_post.html', form=form, categoryname=categoryname)

    @route('/<postid>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_post(self, postid):
        if current_user.allowed_to_remove_post(Post.query.get(postid)):
            print("Hello?")
            form = EditPostForm()
            post = Post.query.get_or_404(postid)
            if not form.content.data:
                form.content.data = post.non_markdown
            if form.validate_on_submit():
                print("Save the post")
                post.content = escape_text_and_create_markdown(form.content.data)
                post.non_markdown = form.content.data
                db_session.commit()
                flash('The post was updated.')
                return redirect(url_for('PostView:get', postid=postid))
            print("Something failed", form.errors)
            return render_template('edit_post.html', form=form, post=post)
        flash('You are not allowed to edit this post.')
        return redirect(url_for('PostView:get', postid=postid))


class RegisterView(FlaskView):
    """
    Handles Registration of users
    """

    @route('/', methods=['GET', 'POST'])
    def new_user(self):
        """
        Allows creation of users
        Checks that no user has the same username and also that no one has the same email
        Then it tries to create the user

        :return: Either a redirect to MainView:index if the user is already registered and logged in,
        a redirect to RegisterView:new_user again or a rendered template of create_user.html
        """
        print("Do we get here?")
        if current_user.is_active():
            return redirect(url_for('MainView:index'))

        form = RegistrationForm()
        if form.validate_on_submit():
            try:
                #print(*encrypt(form.password.data))
                failed = False
                potentialUser = User.query.filter_by(username=form.username.data).first()
                print(potentialUser)

                if potentialUser:
                    flash("The username already exists.")
                    failed = True
                if User.query.filter_by(email=form.email.data).first():
                    flash("The email already exists.")
                    failed = True

                if failed:
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
                flash('The user could not be created, please try again later.')
                print(repr(e))
                redirect(url_for("RegisterView:new_user"))
        return render_template('create_user.html', form=form, title="Create a new user")


class UserView(FlaskView):
    """
    Handles Userpages found under /u
    """
    route_base = '/u'

    def get(self, username):
        """
        Handles /u/<username>
        Since usernames are unique it allows us to have that route

        :param username: The username of the user to lookup
        :return: Either a rendered template of user.html or user_missing.html if there isn't a user with that username
        """
        from sqlalchemy import func

        user = User.query.filter(func.lower(User.username) == func.lower(username)).first()
        if user is not None:
            #print(user.collections.all())
            return render_template('user.html', user=user,
                                   allowed_to_view_collections=current_user == user or current_user.is_active() and
                                                               current_user.status == 4)
        return render_template('user_missing.html', title="The user doesn't seem to exist")


# noinspection PyTypeChecker
class CategoryView(FlaskView):
    """
    CategoryView handles everything centered around categories such as new categories, moderators
    """
    route_base = '/c'

    def index(self):
        """
        Displays all categories

        :return:
        """
        categories = Category.query.all()
        print(categories)
        return render_template("all_categories.html", categories=categories)

    @route('/<categoryname>/')
    def get(self, categoryname):
        """
        Displays all posts in a category

        :param categoryname:
        :return:
        """
        from sqlalchemy import func

        print(g.user)
        deletionform = DeletePostForm()
        category = Category.query.filter(func.lower(Category.categoryname) == func.lower(categoryname)).first()
        print("Category:", category)
        print("Dir category:", dir(category))
        #Reverse the posts so we get most recent first

        #if getattr(current_user, "status", None) != 4:
        if category:
            posts = category.posts.filter(Post.statusid != 5).limit(100).all()[::-1]
            #else:
            #    posts = category.posts.limit(100).all()[::-1]
            return render_template('category.html', category=category, posts=posts, form=deletionform)
        return abort(404)

    @route('<categoryname>/p/<postid>')
    def view_post(self, categoryname, postid):
        """
        Displays a post in a category
        Does some checking on the user and such t oeither render deletion buttons or not, but it can
        probably be simplified

        :param categoryname:
        :param postid:
        :return:
        """
        from sqlalchemy import func

        form = DeletePostForm()
        commentform = CommentForm()
        if int(postid) > MAXINT:
            return abort(404)
        post = Post.query.get_or_404(postid)

        if post.statusid == 5 and getattr(current_user, "status", None) != 4:
            return abort(404)
        #print(post.categoryid)
        category = Category.query.filter(func.lower(Category.categoryname) == func.lower(categoryname)).first_or_404()
        #print(category)
        #print(dir(current_user))
        #if post.categoryid == category.categoryid:
        if post in category.posts:
            if current_user.is_active() and current_user.allowed_to_remove_post(post):
                return render_template('post.html', post=Post.query.get(postid), form=form, allowed_to_remove=True,
                                       commentform=commentform)
            return render_template('post.html', post=Post.query.get(postid), form=form, allowed_to_remove=False,
                                   commentform=commentform)
        return abort(404)
        #print(Category.query.get(post.categoryid).categoryname, postid)
        #return redirect(url_for('CategoryView:view_post', categoryname=Category.query.get(post.categoryid).
        # categoryname,
        #                       postid=postid))

    @route('<categoryname>/p/<postid>/edit')
    @login_required
    def edit_post(self, categoryname, postid):
        return PostView.edit_post(PostView(), postid)

    @route('<categoryname>/p/new', methods=['GET', 'POST'])
    @login_required
    def new_post(self, categoryname):
        """
        Returns PostView.new_post since PostView handles all creation of posts

        :param categoryname:
        :return:
        """
        # noinspection PyCallByClass
        return PostView.new_post(PostView(), categoryname)

    @route('/new', methods=['GET', 'POST'])
    @login_required
    def new_category(self):
        """
        Creates a new category as long as categoryname is unique

        :return:
        """
        print('We are inside CategoryView:new_category')
        form = CategoryForm()
        if current_user.allowed_to_create_category():
            if form.validate_on_submit():
                try:
                    potential_category = Category.query.filter_by(categoryname=form.categoryname.data.lower()).first()

                    if potential_category:
                        flash("There is already a category with that categoryname")
                        return redirect(url_for("CategoryView:new_category"))

                    category = Category(form.categoryname.data.lower(), title=form.categorytitle.data, statusid=1)
                    print("Category created: ", category, category)
                    print(repr(category))
                    db_session.add(category)
                    db_session.commit()

                    category.moderators.append(current_user)
                    db_session.commit()

                    flash("The category was created")
                    return redirect(url_for('CategoryView:get', categoryname=category.categoryname))
                except Exception as e:
                    db_session.rollback()
                    print('Something horrible happened')
                    flash('The category could not be created, please try again later.')
                    print(repr(e), e)
                    redirect(url_for("CategoryView:new_category"))

            return render_template('create_category.html', form=form, title="Create a new category")

        flash("You are not allowed to create categories. Please contact the admins to resolve this.")
        return redirect(url_for("MainView:index"))

    @route('/<categoryname>/moderators')
    def moderators(self, categoryname):
        """
        Displays all moderators in a category

        :param categoryname: Categoryname to display moderators in
        :return:
        """
        form = AddModeratorForm()
        return render_template('moderators.html', category=Category.query.filter_by(categoryname=categoryname).first(),
                               form=form)

    @route('<categoryname>/moderators/add', methods=['GET', 'POST'])
    @login_required
    def add_moderator(self, categoryname):
        """
        Add moderators to a category

        :param categoryname:
        :return:
        """

        category = Category.query.filter_by(categoryname=categoryname).first()
        print(category)
        if current_user.allowed_to_add_moderators(category):
            form = AddModeratorForm()
            if form.validate_on_submit():
                user = User.query.filter_by(username=form.username.data).first()
                if user not in category.moderators:
                    category.moderators.append(user)
                    db_session.commit()
                flash("That user is already a moderator in this category.")
                return redirect(url_for('CategoryView:add_moderator', categoryname=categoryname))
            return render_template('add_moderators.html', category=category, form=form,
                                   categoryname=category.categoryname)
        flash("You are not allowed to add moderators to this category!")
        return redirect(url_for("MainView:index"))

    @route('/<categoryname>/delete', methods=['POST'])
    @login_required
    def delete(self, categoryname):
        """
        Deletes the post associated with the postid, but only if the user is the created or a moderator of the category
        This is a permanent deletion, it won't be marked invisible or something, it will get deleted
        Use with caution

        :param postid: Postid of post to delete
        :return: Redirects to MainView:index all the time
        """
        #try:
        category = Category.query.filter_by(categoryname=categoryname).first()
        print(category)
        if current_user.allowed_to_remove_category(category):
            db_session.delete(category)
            db_session.commit()
            return redirect(url_for('MainView:index'))
        else:
            flash("To remove this category message the admins")
            return redirect(url_for('MainView:index'))
            #except Exception as e:
            #    print(e)
            #    db_session.rollback()
            #    return redirect(url_for('MainView:index'))


class CollectionView(FlaskView):
    """
    CollectionView handles everything around collections
    New collections, adding links and such
    Collections are private and as such you will only be able to view your own, unless you got a password, I think
    """

    @login_required
    def index(self):
        """
        Displays all collection of the logged in user

        :return: Rendered template of collections.html which displays all collections of the user
        """
        return render_template('collections.html', title="Displays your collections",
                               collections=current_user.collections)

    @route('/<collectionid>/delete', methods=['POST'])
    @login_required
    def delete(self, collectionid):
        """
        Deletes the collection, since we use csrf_protection the user cannot remove a collection that they
        aren't allowed to delete, so we don't need any checking of the user

        :param collectionid: Collection to delete
        :return:
        """
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
        """
        Adds a link to the collection if the user is alloweed to do so

        :param collectionid: Id of collection to add the link to
        :return:
        """
        addform = AddToCollectionForm()
        if addform.validate_on_submit():
            #Check to see if there exists a link with that url already
            potentiallink = Link.query.filter_by(link=addform.link.data).first()

            #If that's the case, just use that link
            if potentiallink:
                collection = Collection.query.get(collectionid)
                collection.links.append(potentiallink)
            #Otherwise we just add a new link
            else:
                link = Link(addform.link.data)

                db_session.add(link)
                db_session.commit()

                collection = Collection.query.get(collectionid)
                collection.links.append(link)
            db_session.commit()
            print(collection.links.all())
            return redirect(url_for('CollectionView:get', collectionid=collectionid))
        flash_errors(addform)
        return redirect(url_for('CollectionView:get', collectionid=collectionid))

    @login_required
    def get(self, collectionid):
        """
        Gets the collection with the given id, if the user is allowed to view that collection,
        i.e. if he created it

        :param collectionid: Collectionid to lookup
        :return:
        """
        if not collectionid.isdigit() or int(collectionid) > MAXINT:
            return abort(404)
        collection = Collection.query.get(collectionid)
        print(dir(collection))
        print(collection.links.all())
        deleteform = DeletePostForm()
        if request.args.get('link') is not None:
            addform = AddToCollectionForm(link=request.args.get('link'))
        else:
            addform = AddToCollectionForm()
        print("Does it crash here?")
        if collection:
            print(collection)
            print(collection.userid)
            print(current_user.userid)
            if current_user.userid == collection.userid:
                return render_template('collection.html', collection=collection, title=collection.title,
                                       deleteform=deleteform, form=addform)
            return render_template('not_verified_collection.html', title="You are not eligible to view this collection")
        return render_template('not_verified_collection.html', title="You are not eligible to view this collection")

    def __get(self, collectionid, allowed_to_watch):
        collection = Collection.query.get(collectionid)

        if collection:
            return render_template('shared_collection.html', collection=collection)
        return abort(404)

    @route('/new', methods=['GET', 'POST'])
    @login_required
    def new_collection(self):
        """
        Creates a new collection

        :return: Either a redirect to CollectionView:get with the created collection, a redirect to the same view or
        rendered template of create_collection.html
        """
        form = CollectionForm()
        if form.validate_on_submit():
            try:
                collection = Collection(current_user.userid, form.title.data)
                db_session.add(collection)
                db_session.commit()
                flash("The collection was created")
                return redirect(url_for('CollectionView:get', collectionid=collection.collectionid))
            except Exception as e:
                db_session.rollback()
                flash('The collection could not be created, please try again later.')
                print(repr(e), e)
                redirect(url_for("CollectionView:new_collection"))
        return render_template('create_collection.html', form=form, title="Create a new collection")

    @route('/test', methods=['POST'])
    @login_required
    def test_function(self):
        collection = Collection.query.get(int(request.form['collectionid']))
        post = Post.query.get(int(request.form['postid']))
        collection.links.append(Link(url_for('PostView:get', postid=post.postid, _external=True)))
        db_session.commit()
        return redirect(url_for('CollectionView:get', collectionid=collection.collectionid))

    @route('/share/<base64string>')
    def display_collection(self, base64string):
        collectionid, randomvalue = decode_base64_with_split(base64string)
        collection = Collection.query.filter_by(collectionid=collectionid, random=randomvalue).first()

        if collection:
            return self.__get(collection.collectionid, allowed_to_watch=True)

        return abort(404)

    @route('/<collectionid>/<linkid>/remove', methods=['POST'])
    @login_required
    def remove_link(self, collectionid, linkid):
        """
        Deletes the collection, since we use csrf_protection the user cannot remove a collection that they
        aren't allowed to delete, so we don't need any checking of the user

        :param collectionid: Collection to delete
        :return:
        """
        link = Link.query.get(linkid)
        collection = Collection.query.get(collectionid)
        collection.links.remove(link)
        db_session.commit()
        flash("The link was removed from the collection")
        return redirect(url_for('CollectionView:get', collectionid=collectionid))


class ModerationView(FlaskView):
    route_base = '/mod'

    def index(self):
        return "This is the moderation view, here you will take care of all your moderation needs."
