import sqlite3
import re
import os
import datetime


def run(log_dir, sql_db):
    message_regex = re.compile(
        "(\[\d\d:\d\d:\d\d\]) \[Async Chat Thread - #\d*\/INFO]: (\[[a-zA-Z0-9 ]{1,30}\]) ([^\n\v\0\r\t<>\\\/$%^@: ]{1,50}): ([^\n\v\0\r]*)")
    # group 1 is time
    # group 2 is rank
    # group 3 is username
    # group 4 is message

    print("Parsing messages", end="")
    print(".", end="")
    msg_tuples = []

    c = 0

    for root, dirs, files in os.walk(log_dir):
        for file in files:
            if file[-4:].lower() == ".log":
                if file == "latest.log":
                    date = datetime.datetime.fromtimestamp(
                        os.path.getmtime(os.path.join(log_dir, 'latest.log'))).isoformat()[:10]
                else:
                    date = file[:10]
                if c == 0:
                    print(".", end="")
                c = (c + 1) % ((datetime.datetime.now() - datetime.datetime.fromisoformat("2019-12-05")).days // 10)
                with open(os.path.join(root, file), encoding='utf8') as f:
                    for line_num, line in enumerate(f.readlines()):
                        try:
                            r = re.match(message_regex, line)
                        except UnicodeDecodeError:
                            print(os.path.join(file))
                            input()
                        if r is not None:
                            r = r.groups()
                        else:
                            continue
                        date_text = "{} {}".format(date, r[0][1:-1])
                        rank = r[1][1:-1]
                        username = r[2]
                        message_text = r[3]
                        message_id = "{}{:08d}".format(date_text.replace(" ", "").replace(":", "").replace("-", ""), line_num)
                        msg_tuples.append((message_id, date_text, rank, username, message_text))

    msg_tuples.sort()
    print("DONE")

    print("Importing into SQLite database", end='')
    conn = sqlite3.connect(sql_db)

    cur = conn.cursor()
    cur.execute("select message_id from chat_messages order by message_id desc limit 1")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    conn = sqlite3.connect(sql_db)

    print(".", end="")
    c = 0
    for message_id, date_text, rank, username, message_text in msg_tuples:
        if message_id <= rows[0][0]:
            continue
        if c == 0:
            print(".", end="")
        c = (c + 1) % (len(msg_tuples) // 10)
        conn.execute(
            "insert into chat_messages (message_id, send_date, current_rank, current_username, message) values (?, ?, ?, ?, ?)",
            [message_id, date_text, rank, username, message_text])
    print(".", end="")
    conn.commit()
    print(".", end="")
    conn.close()
    print("DONE")
