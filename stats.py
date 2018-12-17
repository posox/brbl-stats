#!/usr/bin/env python3.6

import json
import logging

import flask
from flask import Flask
from instaparser import agents
from instaparser import entities


log = logging.getLogger(__name__)
app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    data = _get_stats()
    return flask.render_template("index.html", data=data)


@app.route("/stats")
def get_stats():
    return str(_get_stats())


def _get_stats():
    agent = agents.Agent()
    stats = []
    for acc_id in json.load(open("accounts.json"))["accounts"]:
        account = entities.Account(acc_id)
        try:
            data, _ = agent.get_media(account)
        except Exception as e:
            log.error("Failed to get data for account %s", acc_id)
            continue
        rate = 0
        posts = min(len(data), 12)
        for i in range(posts):
            rate += data[i].likes_count + data[i].comments_count
        stats.append({
            "account": acc_id,
            "followers": account.followers_count,
            "posts": account.media_count,
            "rate": rate * 100 / float(posts) / float(account.followers_count)
        })
    sorted_stats = sorted(stats, key=lambda x: x["rate"], reverse=True)
    return sorted_stats


if __name__ == '__main__':
    app.run()
