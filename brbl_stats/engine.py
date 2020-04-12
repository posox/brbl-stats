import datetime
import json
import logging
import os
import random
import time

from apscheduler.schedulers import blocking
from instagram import agents
from instagram import entities
from instagram import exceptions

from brbl_stats import db
from brbl_stats import logging as logger

log = logging.getLogger(__name__)

IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
IG_CHECKPOINT = os.environ.get("IG_CHECKPOINT")

sched = blocking.BlockingScheduler()
agent = agents.WebAgentAccount(IG_USERNAME)


def auth():
    try:
        agent.auth(IG_PASSWORD)
    except exceptions.CheckpointException as e:
        resp = agent.checkpoint_send(
            "https://www.instagram.com/accounts/login/ajax",
            e.navigation['forward'],
            1
        )
        agent.checkpoint(
            e.checkpoint_url,
            IG_CHECKPOINT
        )


@sched.scheduled_job('interval', minutes=240)
def update_info():
    log.info("Starting update user stats!")
    with db.get_session() as session:
        db_users = set(map(lambda x: x[0], session.query(db.User.name)))
        log.info("Load user list")
        accounts, pointer, ok = [], None, True
        while ok:
            followers, pointer = agent.get_followers(pointer=pointer, delay=20)
            accounts.extend([a.username for a in followers])
            ok = pointer is not None
        log.info("Loaded %d accounts", len(accounts))
        random.shuffle(accounts)
        for acc_id in accounts:
            if acc_id in db_users:
                db_users.remove(acc_id)
            try:
                _get_user_data(session, acc_id)
            except exceptions.InternetException as e:
                log.error("Failed to get data for account: %s retrying...\n%s",
                          acc_id, e)
                if e.response.status_code == 429:
                    try:
                        _get_user_data(session, acc_id)
                    except Exception as e:
                        log.error("Failed to get data for account: %s\n%s",
                                  acc_id, e)
                        continue
            except Exception as e:
                log.error("Failed to get data for account: %s\n%s", acc_id, e)
                continue
            session.commit()
        session.query(db.User) \
            .filter(db.User.name.in_(db_users)) \
            .delete(synchronize_session='fetch')
        session.commit()
    log.info("Update stats was finished!")


def _get_user_data(session, account_name):
    log.info("Update info for: %s", account_name)
    account = entities.Account(account_name)
    pointer = None
    rate = 0
    counter = 0
    curr_time = datetime.datetime.utcnow()
    stop = False
    while not stop:
        data, pointer = agent.get_media(account, pointer=pointer, delay=20)
        time.sleep(20)
        for post in data:
            post_date = datetime.datetime.fromtimestamp(post.date)
            delta = curr_time - post_date
            if delta.days <= 40:
                counter += 1
                rate += post.likes_count + post.comments_count
            else:
                stop = True
                break
        if pointer is None:
            break
    factor = 1.0 + 0.05 * (counter - 20)
    user = db.User(
        name=account_name,
        followers=account.followers_count,
        posts=account.media_count,
        rate=rate / float(counter or 1) * factor,
        old_rate=rate / float(counter or 1),
        rate_posts=counter,
        profile_pic_url=account.profile_pic_url,
        factor=factor,
        er=rate * 100.0 / (counter or 1) / account.followers_count,
        last_updated=curr_time)
    session.merge(user)


if __name__ == "__main__":
    logger.setup_logging()
    db.create_db()
    auth()
    update_info()
    sched.start()
