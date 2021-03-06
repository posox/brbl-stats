import contextlib
import os

import sqlalchemy as sa
from sqlalchemy import types as sa_types
from sqlalchemy.ext import declarative
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


Base = declarative.declarative_base()

DATABASE_URL = os.environ['DATABASE_URL']
engine = sa.create_engine(DATABASE_URL, pool_pre_ping=True)
Session = scoped_session(sessionmaker(bind=engine))


class User(Base):
    __tablename__ = "users"

    name = sa.Column(sa.String, primary_key=True)
    followers = sa.Column(sa.Integer)
    posts = sa.Column(sa.Integer)
    rate = sa.Column(sa.Float)
    old_rate = sa.Column(sa.Float)
    rate_posts = sa.Column(sa.Integer)
    er = sa.Column(sa.Float)
    profile_pic_url = sa.Column(sa.String(1024))
    factor = sa.Column(sa.Float)
    last_updated = sa.Column(sa_types.DateTime)

    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])


def create_db():
    Base.metadata.create_all(engine)


@contextlib.contextmanager
def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()
