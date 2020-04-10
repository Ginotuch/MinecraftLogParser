import sqlite3

from OldCode import import_messages_from_logs, update_message_uuid, import_usernames_ips, make_sql, extract_logs


def main():
    log_dir = "C:\\path\\to\\logs"
    sql_db = "C:\\path\\to\\chat.db"

    make_sql.run(sql_db)
    extract_logs.extract(log_dir)

    import_usernames_ips.run(log_dir, sql_db)

    import_messages_from_logs.run(log_dir, sql_db)

    update_message_uuid.run(sql_db)

    print("Performing VACUUM operation (cleaning DB)", end='')
    conn = sqlite3.connect(sql_db)
    print(".", end="")
    conn.execute('VACUUM')
    print(".", end="")
    conn.commit()
    print(".", end="")
    conn.close()
    print("DONE")


if __name__ == '__main__':
    main()
