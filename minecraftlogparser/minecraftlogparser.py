import datetime
import gzip
import os
import shutil
import sqlite3
from typing import List

from minecraftlogparser.logtype import LogType, MessageType, IPType, UUIDType, UsernameType


class MinecraftLogParser:
    def __init__(self):
        self.datatypes: List[LogType] = [MessageType(), IPType(), UUIDType(), UsernameType()]
        self.log_dir = "C:\\path\\to\\logs"
        self.sql_db = "C:\\path\\to\\chat.db"

    def main(self):
        self.make_sql()
        self.extract()
        self.read_files()
        self.vacuum()

    def update_messages_uuids(self):
        print("Updating UUIDs for chat_messages table", end="")
        conn = sqlite3.connect(self.sql_db)
        print(".", end="")
        conn.execute(
            "update chat_messages set users_uuid=(select U.users_uuid from usernames as U where U.username = current_username and (select count(U.users_uuid) from usernames as U where U.username = current_username) = 1)")
        print(".", end="")
        conn.commit()
        print(".", end="")
        conn.close()
        print("DONE")

    def vacuum(self):
        print("Performing VACUUM operation (cleaning DB)", end='')
        conn = sqlite3.connect(self.sql_db)
        print(".", end="")
        conn.execute('VACUUM')
        print(".", end="")
        conn.commit()
        print(".", end="")
        conn.close()
        print("DONE")

    def read_files(self):
        c = 0
        for root, dirs, files in os.walk(self.log_dir):
            for file in files:
                if file[-4:].lower() == ".log":
                    if file == "latest.log":
                        date = datetime.datetime.fromtimestamp(
                            os.path.getmtime(os.path.join(self.log_dir, 'latest.log'))).isoformat()[:10]
                    else:
                        date = file[:10]
                    if c == 0:
                        print(".", end="")
                    c = (c + 1) % ((datetime.datetime.now() - datetime.datetime.fromisoformat("2019-12-05")).days // 10)
                    with open(os.path.join(root, file), encoding='utf8') as f:
                        file_text = f.read()
                        for datatype in self.datatypes:
                            datatype.match_and_store(file_text, date)
        for datatype in self.datatypes:
            datatype.sort()

        conn = sqlite3.connect(self.sql_db)
        for datatype in self.datatypes:
            print("new type")
            datatype.do_sql(conn, self.sql_db)
        conn.close()

    def make_sql(self):
        if not os.path.exists(self.sql_db):
            print("No database found, making new one", end="")
            conn = sqlite3.connect(self.sql_db)
            print(".", end="")
            with open('create_database.sql') as sql_file:
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

    def extract(self):
        print("Extracting logs", end="")
        c = 0
        for file in os.listdir(self.log_dir):
            if c == 0:
                print(".", end="")
            c = (c + 1) % ((datetime.datetime.now() - datetime.datetime.fromisoformat("2019-12-05")).days // 10)
            if os.path.isfile(os.path.join(self.log_dir, file)) and file[-2:].lower() == "gz" and not os.path.exists(
                    os.path.join(self.log_dir, file[:-3])):
                with gzip.open(os.path.join(self.log_dir, file), 'rb') as f_in:
                    with open(os.path.join(self.log_dir, file[:-3]), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
        print("DONE")


if __name__ == '__main__':
    MinecraftLogParser().main()
