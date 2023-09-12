from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = 'sqlite:///WorkoutApp.db'
engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

def initialize_database():
    Base.metadata.create_all(engine)

def get_session():
    return session

def get_fresh_session():
    session = get_session()
    if session.is_active:
        session.close()
        session = get_session()
    return session
