import sqlite3
import re
import os
import datetime
import gzip
import shutil

def run(log_dir, sql_db):
    login_regex = re.compile( "(\[\d\d:\d\d:\d\d\]) \[User Authenticator #\d*\/INFO]: UUID of player ([^\n\v\0\r\t<>\\\/$%^@: ]{1,50}) is ([^\n\v\0\r ]*)\n\[\d\d:\d\d:\d\d\] \[Server thread\/INFO\]: [^\n\v\0\r\t<>\\\/$%^@[: ]{1,50}\[\/([0-9\.]*)")
    #0 is time
    #1 is username
    #2 is uuid
    #3 is ip

    print("Parsing logins", end="")
    print(".", end="")
    tuples = []

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
                    try:
                        r = re.findall(login_regex, f.read())
                    except UnicodeDecodeError:
                        print(os.path.join(file))
                        input()
                    for login in r:
                        date_text = "{} {}".format(date, login[0][1:-1])
                        username = login[1]
                        uuid = login[2]
                        ip = login[3]
                        tuples.append((date_text, username, uuid, ip))

    tuples.sort()
    print("DONE")

    print("Importing into SQLite database", end='')
    conn = sqlite3.connect(sql_db)
    print(".", end="")
    c = 0
    inserted_uuids = []
    inserted_uname_uuid = []
    for date_text, username, uuid, ip in tuples:
        if c == 0:
            print(".", end="")
        c = (c + 1) % (len(tuples) // 10)

        if uuid not in inserted_uuids:
            conn.execute('insert into users (uuid) values (?)', (uuid, ))
            inserted_uuids.append(uuid)
        if (username, uuid) not in inserted_uname_uuid:
            conn.execute('insert into usernames (users_uuid, username, first_seen) values (?, ?, ?)', (uuid, username, date_text))
            inserted_uname_uuid.append((username, uuid))
        conn.execute('insert into user_ips (users_uuid, ip, log_in_date) values (?, ?, ?)', (uuid, ip, date_text))
    print(".", end="")
    conn.commit()
    print(".", end="")
    conn.close()
    print("DONE")