import datetime
import gzip
from pathlib import Path
import re
import shutil

from .logtype import LogType, MessageType, IPType, UUIDType, UsernameType, CommandType
from .db import DB


class MinecraftLogParser:
    def __init__(self, log_dir: Path, sql_db: Path, logtypes: list[LogType] = None) -> None:
        self.logtypes: list[LogType] = logtypes
        if self.logtypes is None:
            self.logtypes = [MessageType(), IPType(), UUIDType(), UsernameType(), CommandType()]
        self.log_dir: Path = log_dir
        self.db = DB(sql_db)
        self.last_log_file: str = ""
        self.encodingregex: re.Pattern = re.compile("(\[0;\d*;\d*m|\[m|\[\d*m)")
        self.chatcolor2regex: re.Pattern = re.compile("(\[\d\d:\d\d:\d\d\]) \[[^]]*\]: (?:CURRENT|PLAYER)[^\n]*\n")

    def main(self) -> None:
        self.get_lrow()
        self.extract()
        self.read_files()
        self.db.update_messages_uuids()
        self.db.update_commands_uuids()
        self.db.vacuum()

    def get_lrow(self) -> None:
        last_row: str = ""
        for datatype in self.logtypes:
            row = datatype.last_row(self.db)
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

                for datatype in self.logtypes:
                    datatype.match_and_store(file_text, date)
        print("Done")

        print("Sorting data", end="")
        for datatype in self.logtypes:
            print(".", end="")
            datatype.sort()
        print("DONE")

        for datatype in self.logtypes:
            print("Inserting rows from", datatype.name, end=" ")
            datatype.do_sql(self.db)
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
