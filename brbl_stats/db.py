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
    rate_posts = sa.Column(sa.Integer)
    er = sa.Column(sa.Float)
    profile_pic_url = sa.Column(sa.String(1024))

    def __init__(self, name, followers, posts, rate, rate_posts, profile_pic_url, er):
        self.name = name
        self.followers = followers
        self.posts = posts
        self.rate = rate
        self.rate_posts = rate_posts
        self.profile_pic_url = profile_pic_url
        self.er = er

    def to_json(self):
        return {
            "account": self.name,
            "followers": self.followers,
            "posts": self.posts,
            "rate": self.rate,
            "rate_posts": self.rate_posts,
            "profile_pic_url": self.profile_pic_url,
            "er": self.er
        }


class Info(Base):
    __tablename__ = "info"

    id = sa.Column(sa.Integer, primary_key=True)
    last_updated = sa.Column(sa_types.DateTime)

    def __init__(self, id, last_updated):
        self.id = id
        self.last_updated = last_updated


def create_db():
    Base.metadata.create_all(engine)


@contextlib.contextmanager
def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()
