__author__ = 'Chrille'
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import create_engine
#from sqlalchemy.orm import scoped_session, sessionmaker
#from sqlalchemy.ext.declarative import declarative_base

#engine = create_engine('postgres://postgres:bubblegum123@localhost/postgres', convert_unicode=True)
#db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,bind=engine))

db = SQLAlchemy()
Base = db
db_session = db.session

"""def init_db():
    import models
    Base.metadata.create_all(bind=engine)"""
