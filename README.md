# MinecraftLogParser
Given the logs folder from a Minecraft server, this will extract all logs (they're gzip compressed by default),
parse them to find all messages, user logins, uuids, etc. Extracted data is then put into an SQLite database.

## Notes
* This can be run multiple times on the same dataset and will avoid data deduplication.
* The file `latest.log` present in most logs folders will be assumed made on today's date,
otherwise rename it following ISO8601 format: YYYY-MM-DD

### commands.sql
Sample commands for extracting and searching through data from the SQLite database.

#### Requirements
* Python 3.8+ (Tested with Python 3.8)