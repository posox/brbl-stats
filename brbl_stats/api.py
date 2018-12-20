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
        data = session.query(db.User).order_by(db.User.rate.desc())
    return flask.render_template("index.html",
                                 data=list(map(lambda x: x.to_json(), data)))
