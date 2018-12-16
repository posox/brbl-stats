#!/usr/bin/env python3.6

import json

from flask import Flask
from instaparser import agents
from instaparser import entities


app = Flask(__name__)


@app.route("/stats")
def get_stats():
    agent = agents.Agent()
    stats = {}
    for acc_id in json.load(open("accounts.json"))["accounts"]:
        account = entities.Account(acc_id)
        data, _ = agent.get_media(account)
        likes = []
        for i in range(min(len(data), 10)):
            likes.append(data[i].likes_count)
        stats[acc_id] = {
            "followers": account.followers_count,
            "posts": account.media_count,
            "last_likes_count": likes
        }
    return str(stats)


if __name__ == '__main__':
    app.run()
