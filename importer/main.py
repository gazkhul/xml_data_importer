
from importer.database import close_db, connect_db


def main():
    conn = connect_db()
    close_db(conn)


if __name__ == "__main__":
    main()
