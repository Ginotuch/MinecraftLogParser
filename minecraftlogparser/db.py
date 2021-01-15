import sqlite3
from pathlib import Path


class DB:
    def __init__(self, sql_db: Path):
        db_exists: bool = sql_db.exists()
        self.connection: sqlite3.Connection = sqlite3.connect(sql_db)
        self.cursor: sqlite3.Cursor = self.connection.cursor()
        if not db_exists:
            self.make_sql()

    def make_sql(self) -> None:
        print("No database found, making new one", end="")
        print(".", end="")
        with open(Path(__file__).parent.joinpath('create_database.sql')) as sql_file:
            self.cursor.executescript(sql_file.read())
            print(".", end="")
            self.connection.commit()
            print(".", end="")
        print("DONE")

    def update_messages_uuids(self) -> None:
        print("Updating UUIDs for chat_messages table", end="")
        self.cursor.execute(
            "update chat_messages set users_uuid=(select U.users_uuid from usernames as U where U.username = current_username and (select count(U.users_uuid) from usernames as U where U.username = current_username) = 1) where users_uuid IS NULL;")
        print(".", end="")
        self.connection.commit()
        print("DONE")

    def update_commands_uuids(self) -> None:
        print("Updating UUIDs for commands table", end="")
        print(".", end="")
        self.cursor.execute(
            "update commands set users_uuid=(select U.users_uuid from usernames as U where U.username = current_username and (select count(U.users_uuid) from usernames as U where U.username = current_username) = 1) where users_uuid IS NULL;")
        print(".", end="")
        self.connection.commit()
        print("DONE")

    def vacuum(self) -> None:
        print("Performing VACUUM operation (cleaning DB)", end='')
        self.cursor.execute('VACUUM')
        print(".", end="")
        self.connection.commit()
        print("DONE")
