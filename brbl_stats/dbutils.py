from brbl_stats import db
from brbl_stats import engine
from brbl_stats import logging


def main():
    logging.setup_logging()
    db.create_db()
    engine.update_info()


if __name__ == "__main__":
    main()
