import sys

import mariadb


def main():
    try:
        conn = mariadb.connect(
            user="db_user",
            password="db_user_passwd",
            host="192.168.1.113",
            port=3306,
            database="importer",
            ssl_ca="",

        )
        print("Connection to MariaDB Platform was successful!")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    cur = conn.cursor()


if __name__ == "__main__":
    main()
