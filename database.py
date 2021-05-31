import sqlalchemy
from sqlalchemy.orm import sessionmaker

from models import *
import os


try:
    os.environ['DATABASE_URL']
except:
    print("DEBUG: using sqlite")

os.environ.setdefault('DATABASE_URL', 'sqlite:///default.sqlite3?check_same_thread=false')
DATABASE_URL = os.environ['DATABASE_URL']

ECHO_LOG = False

engine = sqlalchemy.create_engine(DATABASE_URL, echo=ECHO_LOG)

Base.metadata.create_all(bind=engine)

SessionClass = sessionmaker(engine)