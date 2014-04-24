from models import *
from flask import Flask

__author__ = 'Chrille'


def create_and_run():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bubblegum123@localhost/postgres'
    db.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()
        print('Dropped and then created all tables, hopefully')


if __name__ == '__main__':
    create_and_run()