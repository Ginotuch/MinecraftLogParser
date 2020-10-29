from pathlib import Path
import sys

import minecraftlogparser

if len(sys.argv) != 3:
    print("Requires 2 arguments, only", len(sys.argv) - 1,
          "was supplied\nUsage:\n  run.py /path/to/logs/folder/ /path/to/chat.db")
    exit()
log_dir = Path(sys.argv[1]).absolute()
sql_db = Path(sys.argv[2]).absolute()
print(log_dir, sql_db)
minecraftlogparser.MinecraftLogParser(log_dir, sql_db).main()
