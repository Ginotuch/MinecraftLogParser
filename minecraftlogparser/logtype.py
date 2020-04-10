import re
import sqlite3
from typing import Any, List, Dict


class LogType:
    def __init__(self):
        self.name = "LogType"
        self.matches: List[Dict[str, Any]] = []
        self.regex = None
        self.lrow_command = ""
        self.sql_tuple = ()
        self.insert_command = ""
        self.lrow = ""

    def match_and_store(self, file_text, date) -> None:
        pass

    def _get_default_matches(self, match, date, line_num) -> Dict:
        match = match.groups()
        date_text = "{} {}".format(date, match[0][1:-1])
        message_id = "{}{:08d}".format(date_text.replace(" ", "").replace(":", "").replace("-", ""), line_num)
        temp_dict = {
            "match": match,
            "date_text": date_text,
            "id": message_id}
        self.matches.append(temp_dict)
        return temp_dict

    def sort(self):
        self.matches.sort(key=lambda x: x["id"])

    def last_row(self, conn) -> str:
        if self.lrow == "":
            self._get_last_row(conn)
        return self.lrow

    def do_sql(self, conn, sql_db) -> int:
        print(self.lrow)
        c = 0
        for match in self.matches:
            if match["id"] > self.last_row(sql_db):
                c += 1
                conn.execute(self.insert_command, [match[x] for x in self.sql_tuple])
        conn.commit()
        return c

    def _get_last_row(self, sql_db) -> None:
        conn = sqlite3.connect(sql_db)
        cur = conn.cursor()
        cur.execute(self.lrow_command)
        if (ret := cur.fetchall()) != []:
            self.lrow = ret[0][0]
        else:
            self.lrow = "0"
        cur.close()


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
            line = line.strip()
            if (match := re.match(self.regex, line)) is not None:
                temp_dict = super()._get_default_matches(match, date, line_num)
                temp_dict["rank"] = temp_dict["match"][1][1:-1]
                temp_dict["username"] = temp_dict["match"][2]
                temp_dict["message_text"] = temp_dict["match"][3]


class DoubleLineType(LogType):
    def __init__(self):
        super().__init__()
        self.name = "DoubleLineType"
        self.regex = re.compile(
            "(\[\d\d:\d\d:\d\d\]) \[User Authenticator #\d*\/INFO]: UUID of player ([^\n\v\0\r\t<>\\\/$%^@: ]{1,50}) is ([^\n\v\0\r ]*)\n\[\d\d:\d\d:\d\d\] \[Server thread\/INFO\]: [^\n\v\0\r\t<>\\\/$%^@[: ]{1,50}\[\/([0-9\.]*)")

    def match_and_store(self, file_text, date) -> None:
        line_doubles = file_text.split("\n")
        line_doubles = [line_doubles[i] + "\n" + line_doubles[i + 1] for i in range(len(line_doubles) - 1)]
        for line_num, line in enumerate(line_doubles):
            if (match := re.match(self.regex, line)) is not None:
                temp_dict = super()._get_default_matches(match, date, line_num)
                temp_dict["username"] = temp_dict["match"][1]
                temp_dict["users_uuid"] = temp_dict["match"][2]
                temp_dict["ip"] = temp_dict["match"][3]


class IPType(DoubleLineType):
    def __init__(self):
        super().__init__()
        self.lrow_command = "select log_in_id from user_ips order by log_in_id desc limit 1"
        self.insert_command = "insert or ignore into user_ips (log_in_id, users_uuid, ip, log_in_date) values (?, ?, ?, ?)"
        self.sql_tuple = ("id", "users_uuid", "ip", "date_text")


class UUIDType(DoubleLineType):
    def __init__(self):
        super().__init__()
        self.name = "UUIDType"
        self.lrow_command = "select uuid_id from users order by uuid_id desc limit 1"
        self.insert_command = "insert or ignore into users (uuid_id, uuid, first_seen) values (?, ?, ?)"
        self.sql_tuple = ("id", "users_uuid", "date_text")


class UsernameType(DoubleLineType):
    def __init__(self):
        super().__init__()
        self.name = "UsernameType"
        self.lrow_command = "select username_id from usernames order by username_id desc limit 1"
        self.insert_command = "insert or ignore into usernames (username_id, users_uuid, username, first_seen) values (?, ?, ?, ?)"
        self.sql_tuple = ("id", "users_uuid", "username", "date_text")
