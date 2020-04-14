-- Gets a list of messages sent within 200 seconds of a given time
select *
from chat_messages
where abs(strftime('%s', '2020-04-07 06:21:00') - strftime('%s', send_date)) < 200;

-- Gets a list of messages sent between two times
select *
from chat_messages
where strftime('%s', '2020-03-28 05:33:14') <= strftime('%s', send_date)
  and strftime('%s', send_date) <= strftime('%s', '2020-03-28 06:22:04')
order by send_date;

-- List of UUIDs with usernames if they've changed their username
select username, users_uuid, first_seen
from usernames
where users_uuid in (select users_uuid from usernames group by users_uuid having count(username) > 1)
order by users_uuid, first_seen desc;

-- Gets a list of IPs each user has in from if there's more than one and their most recent username
select distinct U.username, IP.ip
from usernames as U,
     user_ips as IP
where U.users_uuid = IP.users_uuid
  and U.username in
      (select sub.username from usernames as sub where sub.users_uuid = U.users_uuid order by first_seen desc limit 1)
  and U.users_uuid in (select users_uuid from user_ips group by users_uuid having count(distinct ip) > 1)
order by username;

-- Get most recent username of people who have had more than 1 username
select U.username, U.users_uuid
from usernames as U
where U.username in
      (select sub.username from usernames as sub where sub.users_uuid = U.users_uuid order by first_seen desc limit 1)
  and U.users_uuid in (select users_uuid from usernames group by users_uuid having count(username) > 1)
order by U.users_uuid;

-- Get all chat messages from user
select *
from chat_messages
where current_username = 'xxxx';

-- Count amount of people in some tables
select count(distinct current_username)
from chat_messages;
select count(distinct username)
from usernames;
select count(distinct uuid)
from users;

-- Get chat messages count per person with their most recent username
select current_username as username, count(*)
from (select * from chat_messages order by message_id desc)
where users_uuid is not NULL
group by users_uuid
order by count(*) desc;

-- Get chat message count and last log in date (very slow command)
select C.current_username as username, count(*), log_in_date
from (select * from chat_messages order by message_id desc) as C,
     (select distinct users_uuid, log_in_date from user_ips order by log_in_id asc) as L
where C.users_uuid is not NULL
  and C.users_uuid = L.users_uuid
group by C.users_uuid
order by count(*) desc;


-- Get total number of chat messages sent
select count(*)
from chat_messages;

select count(distinct uuid)
from users;

-- Get all messages containing a word
select current_username as username, count(*)
from (select * from chat_messages order by message_id desc)
where users_uuid is not NULL and message like '%y''all%'
   or message like '%yall%'
   or message like '%ya''ll%'
group by users_uuid
order by count(*) desc;