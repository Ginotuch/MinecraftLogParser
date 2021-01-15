import datetime
import gzip
from pathlib import Path
import re
import shutil
import sqlite3

from minecraftlogparser.logtype import LogType, MessageType, IPType, UUIDType, UsernameType, CommandType


class MinecraftLogParser:
    def __init__(self, log_dir: Path, sql_db: Path) -> None:
        self.datatypes: list[LogType] = [MessageType(), IPType(), UUIDType(), UsernameType(), CommandType()]
        self.log_dir: Path = log_dir
        self.sql_db: Path = sql_db
        self.last_log_file: str = ""
        self.encodingregex: re.Pattern = re.compile("(\[0;\d*;\d*m|\[m|\[\d*m)")
        self.chatcolor2regex: re.Pattern = re.compile("(\[\d\d:\d\d:\d\d\]) \[[^]]*\]: (?:CURRENT|PLAYER)[^\n]*\n")

    def main(self) -> None:
        self.make_sql()
        self.get_lrow()
        self.extract()
        self.read_files()
        self.update_messages_uuids()
        self.update_commands_uuids()
        self.vacuum()

    def update_messages_uuids(self) -> None:
        print("Updating UUIDs for chat_messages table", end="")
        conn = sqlite3.connect(self.sql_db)
        print(".", end="")
        conn.execute(
            "update chat_messages set users_uuid=(select U.users_uuid from usernames as U where U.username = current_username and (select count(U.users_uuid) from usernames as U where U.username = current_username) = 1) where users_uuid IS NULL;")
        print(".", end="")
        conn.commit()
        print(".", end="")
        conn.close()
        print("DONE")

    def update_commands_uuids(self) -> None:
        print("Updating UUIDs for commands table", end="")
        conn = sqlite3.connect(self.sql_db)
        print(".", end="")
        conn.execute(
            "update commands set users_uuid=(select U.users_uuid from usernames as U where U.username = current_username and (select count(U.users_uuid) from usernames as U where U.username = current_username) = 1) where users_uuid IS NULL;")
        print(".", end="")
        conn.commit()
        print(".", end="")
        conn.close()
        print("DONE")

    def vacuum(self) -> None:
        print("Performing VACUUM operation (cleaning DB)", end='')
        conn = sqlite3.connect(self.sql_db)
        print(".", end="")
        conn.execute('VACUUM')
        print(".", end="")
        conn.commit()
        print(".", end="")
        conn.close()
        print("DONE")

    def get_lrow(self) -> None:
        last_row: str = ""
        for datatype in self.datatypes:
            row = datatype.last_row(self.sql_db)
            if last_row == "" or last_row > row[:8]:
                last_row = row[:8]
        self.last_log_file = "{}-{}-{}".format(last_row[:4], last_row[4:6], last_row[6:8])

    def read_files(self) -> None:
        c = 0
        print("Parsing log files", end="")
        log_count = len(list(self.log_dir.glob("*.log")))
        for file in self.log_dir.glob("*.log"):
            if file.name == "latest.log":
                date: str = datetime.datetime.fromtimestamp(
                    self.log_dir.joinpath('latest.log').stat().st_mtime).isoformat()[:10]
            else:
                date: str = file.name[:10]
            if date < self.last_log_file:
                continue
            if c == 0:
                print(".", end="")
            c = (c + 1) % (log_count // 10)
            with open(file, encoding='utf8') as f:
                file_text = self.remove_chatcolor2_outputs(self.remove_encoding_errors(f.read()))

                for datatype in self.datatypes:
                    datatype.match_and_store(file_text, date)
        print("Done")

        print("Sorting data", end="")
        for datatype in self.datatypes:
            print(".", end="")
            datatype.sort()
        print("DONE")

        conn: sqlite3.Connection = sqlite3.connect(self.sql_db)
        for datatype in self.datatypes:
            print("Inserting rows from", datatype.name, end=" ")
            datatype.do_sql(conn, self.sql_db)
            print("DONE")
        conn.close()

    def make_sql(self) -> None:
        if not self.sql_db.exists():
            print("No database found, making new one", end="")
            conn = sqlite3.connect(self.sql_db)
            print(".", end="")
            with open(Path(__file__).parent.joinpath('create_database.sql')) as sql_file:
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

    def extract(self) -> None:
        print("Extracting logs", end="")
        log_count = len(list(self.log_dir.glob("*.gz")))
        c = 0
        for file in self.log_dir.iterdir():
            if c == 0:
                print(".", end="")
            c = (c + 1) % (log_count // 10)
            if file.is_file() and file.name[-2:].lower() == "gz" and not self.log_dir.joinpath(file.name[:-3]).exists():
                if file.name[:10] < self.last_log_file:
                    continue
                with gzip.open(file, 'rb') as f_in:
                    with open(self.log_dir.joinpath(file.name[:-3]), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
        print("DONE")

    def remove_encoding_errors(self, text: str) -> str:
        return self.encodingregex.sub("", text)

    def remove_chatcolor2_outputs(self, text: str) -> str:
        return self.chatcolor2regex.sub("", text)
