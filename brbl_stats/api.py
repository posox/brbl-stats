#!/usr/bin/env python3.6

import logging

import flask

from brbl_stats import db


log = logging.getLogger(__name__)
app = flask.Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    with db.get_session() as session:
        data = session.query(db.User).order_by(db.User.old_rate.desc())
    return flask.render_template("index.html", data=data)


@app.route("/new")
def new():
    with db.get_session() as session:
        data = session.query(db.User).order_by(db.User.rate.desc())
    return flask.render_template("new.html", data=data)


@app.teardown_appcontext
def cleanup(resp_or_exc):
    db.Session.remove()


if __name__ == "__main__":
    app.run()
