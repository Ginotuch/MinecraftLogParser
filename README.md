# MinecraftLogParser
Given the logs folder from a Minecraft server, this will extract all logs (they're gzip compressed by default),
parse them to find all messages, user logins, uuids, etc. Extracted data is then put into an SQLite database.

## Usage
`$ run.py /path/to/logs/folder/ /path/to/chat.db`

* chat.db will be created if it doesn't already exist.

## Notes
* Currently ony supports chat formats of: `[group] username: message text`. Which is set in the Essentials config.yml as `format: '{DISPLAYNAME}: {MESSAGE}'` 
and using a prefix through whatever permission manager you use (e.g. LuckPerms).
* This can be run multiple times on the same dataset and will avoid data duplication and excessive file reading.
* The file `latest.log` present in most logs folders will be assumed made on the most recent modify date of the file,
otherwise rename it following ISO8601 format: `YYYY-MM-DD.log` (you can add digits at the end if there are multiple on the same day, eg adding "-4": `2020-01-01-4.log`)

####Issues
* Because this only works on log files and not while the server is running there are a few limitations.
* Undefined behavior is caused when custom `/nick` names are applied to players in-game (no way to tell since nicknames
and real usernames are logged exactly the same).
* Undefined behavior in the case of player1 changing their name from XX to YY, then player2 from ZZ to XX.

## Todo
* Figure out the best way to handle multiple log formats (first thing will be to add vanilla support).

## Other:

### commands.sql
Sample commands for extracting and searching through data from the SQLite database.

#### Requirements
* Python 3.8+ (Tested with Python 3.8)