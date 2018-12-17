#!/usr/bin/env python3.6

import json
import logging
import os

import flask
from flask import Flask
from instaparser import agents
from instaparser import entities
import psycopg2
import sqlalchemy as sqla
from sqlalchemy.ext import declarative
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.environ['DATABASE_URL']

log = logging.getLogger(__name__)
app = Flask(__name__)

agent = agents.Agent()

engine = sqla.create_engine(DATABASE_URL, echo=True)
Base = declarative.declarative_base()
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = "users"

    name = sqla.Column(sqla.String, primary_key=True)
    followers = sqla.Column(sqla.Integer)
    posts = sqla.Column(sqla.Integer)
    rate = sqla.Column(sqla.Float)
    profile_pic_url = sqla.Column(sqla.String)

    def __init__(self, name, followers, posts, rate, profile_pic_url):
        self.name = name
        self.followers = followers
        self.posts = posts
        self.rate = rate
        self.profile_pic_url = profile_pic_url

    def to_json(self):
        return {
            "account": self.name,
            "followers": self.followers,
            "posts": self.posts,
            "rate": self.rate,
            "profile_pic_url": self.profile_pic_url
        }


Base.metadata.create_all(engine)


@app.route("/")
@app.route("/index")
def index():
    data = _get_stats()
    return flask.render_template("index.html", data=data)


@app.route("/stats")
def get_stats():
    return str(_get_stats())


def _get_stats():
    stats = []
    for acc_id in json.load(open("accounts.json"))["accounts"]:
        try:
            data = _get_user_data(acc_id)
        except Exception as e:
            log.error("Failed to get data for account: %s\n%s", acc_id, e)
            continue
        stats.append(data)

    sorted_stats = sorted(stats, key=lambda x: x["rate"], reverse=True)
    return sorted_stats


def _get_user_data(account_name):
    session = Session()
    for user in session.query(User).filter(User.name==account_name):
        session.close()
        return user.to_json()
    account = entities.Account(account_name)
    data, _ = agent.get_media(account)
    rate = 0
    posts = min(len(data), 12)
    for i in range(posts):
        rate += data[i].likes_count + data[i].comments_count
    user = User(
        name=account_name,
        followers=account.followers_count,
        posts=account.media_count,
        rate=rate * 100 / float(posts) / float(account.followers_count),
        profile_pic_url=account.profile_pic_url)
    session.add(user)
    session.commit()
    session.close()
    return user.to_json()


if __name__ == '__main__':
    app.run()
