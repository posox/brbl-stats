from brbl_stats import db
from brbl_stats import engine


def main():
    db.create_db()
    engine.update_info()


if __name__ == "__main__":
    main()
