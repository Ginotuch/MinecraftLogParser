import re
from typing import Any

from .db import DB


class LogType:
    def __init__(self):
        self.name: str = "LogType"
        self.matches: list[dict[str, Any]] = []
        self.regex: re.Pattern = re.compile("")
        self.lrow_command: str = ""
        self.sql_tuple: tuple[str] = ("",)
        self.insert_command: str = ""
        self.lrow: str = "0"

    def match_and_store(self, file_text, date) -> None:
        pass

    def _get_default_matches(self, match, date, line_num) -> dict:
        match: tuple = match.groups()
        date_text: str = "{} {}".format(date, match[0][1:-1])
        message_id: str = "{}{:08d}".format(date_text.replace(" ", "").replace(":", "").replace("-", ""), line_num)
        temp_dict: dict[str, Any] = {
            "match": match,
            "date_text": date_text,
            "id": message_id}
        self.matches.append(temp_dict)
        return temp_dict

    def sort(self) -> None:
        self.matches.sort(key=lambda x: x["id"])

    def last_row(self, db: DB) -> str:
        if self.lrow == "0":
            self._get_last_row(db)
        return self.lrow

    def do_sql(self, db: DB) -> int:
        c: int = 0
        for match in self.matches:
            if match["id"] > self.last_row(db):
                c += 1
                db.cursor.execute(self.insert_command, [match[x] for x in self.sql_tuple])
        db.connection.commit()
        return c

    def _get_last_row(self, db: DB) -> None:
        db.cursor.execute(self.lrow_command)
        if (ret := db.cursor.fetchall()) != []:
            self.lrow = ret[0][0]


class MessageType(LogType):
    def __init__(self):
        super().__init__()
        self.name = "MessageType"
        self.lrow_command = "select message_id from chat_messages order by message_id desc limit 1"
        self.insert_command = "insert or ignore into chat_messages (message_id, send_date, current_rank, current_username, message) values (?, ?, ?, ?, ?)"
        self.sql_tuple = ("id", "date_text", "rank", "username", "message_text")
        self.regex = re.compile(
            "(\[\d\d:\d\d:\d\d\]) \[Async Chat Thread - #\d*\/INFO]: (\[[a-zA-Z0-9 ]{1,30}\]) ([^\n\v\0\r\t<>\\\/$%^@: ]{1,50}): ([^\n\v\0\r]*)")

    def match_and_store(self, file_text, date) -> None:
        for line_num, line in enumerate(file_text.split("\n")):
            line: str = line.strip()
            if (match := self.regex.match(line)) is not None:
                temp_dict: dict[str, Any] = self._get_default_matches(match, date, line_num)
                temp_dict["rank"] = temp_dict["match"][1][1:-1]
                temp_dict["username"] = temp_dict["match"][2]
                temp_dict["message_text"] = temp_dict["match"][3]


class CommandType(MessageType):
    def __init__(self):
        super().__init__()
        self.name = "CommandType"
        self.lrow_command = "select command_id from commands order by command_id desc limit 1"
        self.insert_command = "insert or ignore into commands (command_id, send_date, current_username, command) values (?, ?, ?, ?)"
        self.sql_tuple = ("id", "date_text", "username", "command")
        self.regex = re.compile(
            "(\[\d\d:\d\d:\d\d\]) \[Server thread\/INFO]: ([^\n\v\0\r\t<>\\\/$%^@: ]{1,50}) issued server command: ([^\n\v\0\r]*)"
        )

    def match_and_store(self, file_text, date) -> None:
        for line_num, line in enumerate(file_text.split("\n")):
            line: str = line.strip()
            if (match := self.regex.match(line)) is not None:
                temp_dict: dict[str, Any] = self._get_default_matches(match, date, line_num)
                temp_dict["username"] = temp_dict["match"][1]
                temp_dict["command"] = temp_dict["match"][2]


class UserLoginType(LogType):
    def __init__(self):
        super().__init__()
        self.name = "DoubleLineType"
        self.regex = re.compile(
            "(\[\d\d:\d\d:\d\d\]) \[User Authenticator #\d*\/INFO]: UUID of player ([^\n\v\0\r\t<>\\\/$%^@: ]{1,50}) is ([^\n\v\0\r ]*)\n\[\d\d:\d\d:\d\d\] \[Server thread\/INFO\]: [^\n\v\0\r\t<>\\\/$%^@[: ]{1,50}\[\/([0-9\.]*)")

    def match_and_store(self, file_text, date) -> None:
        line_doubles: list[str] = file_text.split("\n")
        line_doubles = [line_doubles[i] + "\n" + line_doubles[i + 1] for i in range(len(line_doubles) - 1)]
        for line_num, line in enumerate(line_doubles):
            if (match := self.regex.match(line)) is not None:
                temp_dict: dict[str, Any] = self._get_default_matches(match, date, line_num)
                temp_dict["username"] = temp_dict["match"][1]
                temp_dict["users_uuid"] = temp_dict["match"][2]
                temp_dict["ip"] = temp_dict["match"][3]


class IPType(UserLoginType):
    def __init__(self):
        super().__init__()
        self.lrow_command = "select log_in_id from user_ips order by log_in_id desc limit 1"
        self.insert_command = "insert or ignore into user_ips (log_in_id, users_uuid, ip, log_in_date) values (?, ?, ?, ?)"
        self.sql_tuple = ("id", "users_uuid", "ip", "date_text")


class UUIDType(UserLoginType):
    def __init__(self):
        super().__init__()
        self.name = "UUIDType"
        self.lrow_command = "select uuid_id from users order by uuid_id desc limit 1"
        self.insert_command = "insert or ignore into users (uuid_id, uuid, first_seen) values (?, ?, ?)"
        self.sql_tuple = ("id", "users_uuid", "date_text")


class UsernameType(UserLoginType):
    def __init__(self):
        super().__init__()
        self.name = "UsernameType"
        self.lrow_command = "select username_id from usernames order by username_id desc limit 1"
        self.insert_command = "insert or ignore into usernames (username_id, users_uuid, username, first_seen) values (?, ?, ?, ?)"
        self.sql_tuple = ("id", "users_uuid", "username", "date_text")
