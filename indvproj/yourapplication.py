if __name__ == '__main__':
    from flask import g, render_template

    print('Importing db_session and db')
    from indvproj import app, db_session

    var = """app = Flask('indvproj')
    app.secret_key = "Wtf is wrong with you? Why won't you just let me register a user sometime today? :("
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bubblegum123@localhost/postgres'
    db.init_app(app)"""

    from indvproj.model import User, Category
    from flask_login import current_user
    from indvproj.model import login_manager
    from indvproj.model import MainView, RegisterView, PostView, LoginView, UserView, CollectionView, LogoutView, CategoryView, \
        BlogView, AboutView, ModerationView
    from flask_wtf.csrf import CsrfProtect
    #print("Encrypting 'what' and returns the sha512 hash with the salt generated",encrypt("what"))
    #app.debug = True
    print('Already imported db')

    csrf = CsrfProtect()

    @csrf.error_handler
    def csrf_error(reason):
        print("Well fuck", reason)

    login_manager.init_app(app)
    login_manager.login_view = 'LoginView:index'
    csrf.init_app(app)

    MainView.register(app)
    RegisterView.register(app)
    PostView.register(app)
    LoginView.register(app)
    UserView.register(app)
    CollectionView.register(app)
    LogoutView.register(app)
    CategoryView.register(app)
    BlogView.register(app)
    AboutView.register(app)
    ModerationView.register(app)

    @app.before_first_request
    def x():
        pass

    @app.before_request
    def before_request():
        print("Here then?")
        g.user = current_user
        g.categories = Category.query.all()
        g.users = User.query.all()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @login_manager.user_loader
    def load_user(userid):
        return User.query.get(int(userid))


    @app.teardown_appcontext
    def shutdown_session(self, exception=None):
        db_session.remove()

    print('Running the app')
    app.run(host='0.0.0.0', debug=True)
