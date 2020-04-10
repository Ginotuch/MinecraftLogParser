import sqlite3


def run(sql_db):
    print("Updating UUIDs for chat_messages table", end="")
    conn = sqlite3.connect(sql_db)
    print(".", end="")
    conn.execute("update chat_messages set users_uuid=(select U.users_uuid from usernames as U where U.username = current_username and (select count(U.users_uuid) from usernames as U where U.username = current_username) = 1)")
    print(".", end="")
    conn.commit()
    print(".", end="")
    conn.close()
    print("DONE")
