import datetime
import json
import logging

from apscheduler.schedulers import blocking
from instaparser import agents
from instaparser import entities

from brbl_stats import db

log = logging.getLogger(__name__)

sched = blocking.BlockingScheduler()
agent = agents.Agent()


@sched.scheduled_job('interval', minutes=30)
def update_info():
    log.info("Starting update user stats!")
    with db.get_session() as session:
        for acc_id in json.load(open("accounts.json"))["accounts"]:
            try:
                data = _get_user_data(session, acc_id)
            except Exception as e:
                log.error("Failed to get data for account: %s\n%s", acc_id, e)
                continue
        session.merge(db.Info(id=1, last_updated=datetime.datetime.now()))
        session.commit()
    log.info("Update stats was finished!")


def _get_user_data(session, account_name):
    account = entities.Account(account_name)
    data, _ = agent.get_media(account)
    rate = 0
    posts = min(len(data), 12)
    posts_cnt = 0
    curr_time = datetime.datetime.now()
    for i in range(posts):
        post_date = datetime.datetime.fromtimestamp(data[i].date)
        delta = curr_time() - post_date
        if delta.days <= 21:    # 3 weeks
            posts_cnt += 1
            rate += data[i].likes_count + data[i].comments_count
    posts_cnt = posts_cnt if posts_cnt else 1
    user = db.User(
        name=account_name,
        followers=account.followers_count,
        posts=account.media_count,
        rate=rate / float(posts_cnt),
        profile_pic_url=account.profile_pic_url)
    session.merge(user)


if __name__ == "__main__":
    sched.start()
