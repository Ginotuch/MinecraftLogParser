import os
import sys

import minecraftlogparser

if len(sys.argv) != 3:
    print("Requires 2 arguments, only", len(sys.argv) - 1, "was supplied\nUsage:\n  run.py /path/to/logs/folder/ /path/to/chat.db")
    exit()
log_dir = os.path.abspath(sys.argv[1])
sql_db = os.path.abspath(sys.argv[2])
print(log_dir, sql_db)
minecraftlogparser.MinecraftLogParser(log_dir, sql_db).main()
