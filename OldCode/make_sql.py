import os
import sqlite3


def run(sql_db):
    if not os.path.exists(sql_db):
        print("No database found, making new one", end="")
        conn = sqlite3.connect(sql_db)
        print(".", end="")
        with open('../create_database.sql') as sql_file:
            c = conn.cursor()
            print(".", end="")
            c.executescript(sql_file.read())
            print(".", end="")
            conn.commit()
            print(".", end="")
            c.close()
            print(".", end="")
        conn.close()
        print(".", end="")
        print("DONE")
    else:
        print("Clearing old database", end='')
        conn= sqlite3.connect(sql_db)
        print(".", end="")
        # conn.execute('delete from chat_messages')
        print(".", end="")
        conn.execute('delete from user_ips')
        print(".", end="")
        conn.execute('delete from usernames')
        print(".", end="")
        conn.execute('delete from users')
        print(".", end="")
        conn.commit()
        print(".", end="")
        conn.close()
        print("DONE")
