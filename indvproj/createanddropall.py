from model.models import *
from model.database import *
from flask import Flask

__author__ = 'Chrille'


def create_and_run():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bubblegum123@localhost/postgres'
    db.init_app(app)

    with app.app_context():
        print('Before try')
        try:
            db_session.close()
            print('after try')

            #print('after drop_all')
            db.create_all()
            print('after create_all')
            print('Dropped and then created all tables, hopefully')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    create_and_run()
