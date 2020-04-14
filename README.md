# MinecraftLogParser
Given the logs folder from a Minecraft server, this will extract all logs (they're gzip compressed by default),
parse them to find all messages, user logins, uuids, etc. Extracted data is then put into an SQLite database.

## Notes
* Currently ony supports chat formats of: `[group] username: message text`. Which is set in the Essentials config.yml as `format: '{DISPLAYNAME}: {MESSAGE}'` 
and using a prefix through whatever permission manager you use (e.g. LuckPerms).
* This can be run multiple times on the same dataset and will avoid data deduplication.
* The file `latest.log` present in most logs folders will be assumed made on the most recent modify date of the file,
otherwise rename it following ISO8601 format: `YYYY-MM-DD.log` (you can add digits at the end if there are multiple on the same day, eg adding "-4": `2020-01-01-4.log`)
* Undefined behavior is caused when custom `/nick` names are applied to players in-game (no way to tell since nicknames
and real usernames are logged exactly the same).
* When a player1 changes their username from XX to YY, then player2 changes their username to XX, the UUIDs in chat for 

## Todo
* Figure out the best way to handle multiple log formats (first thing will be to add vanilla support).

## Other:

### commands.sql
Sample commands for extracting and searching through data from the SQLite database.

#### Requirements
* Python 3.8+ (Tested with Python 3.8)