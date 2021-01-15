-- List all messages containing a word
select send_date, current_rank, current_username, message
from chat_messages
where message like '%xxxxx%'
order by send_date desc;

-- Get all chat messages from user
select send_date, current_username, message
from chat_messages
where current_username = 'example'
order by send_date desc;

-- Get all chat messages
select send_date, current_rank, current_username, message
from chat_messages
order by send_date desc;

-- Gets a list of messages sent within 200 seconds of a given time
select send_date, current_rank, current_username, message
from chat_messages
where abs(strftime('%s', '2020-09-13 10:05:51') - strftime('%s', send_date)) < 200;

-- Gets a list of messages sent between two times
select send_date, current_rank, current_username, message
from chat_messages
where strftime('%s', '2020-03-28 05:33:14') <= strftime('%s', send_date)
  and strftime('%s', send_date) <= strftime('%s', '2020-03-28 06:22:04')
order by send_date desc;

select * from chat_messages where users_uuid = (select s.users_uuid from usernames s where s.username like 'example');

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

-- Count amount of people in some tables
select count(distinct current_username)
from chat_messages;
select count(distinct username)
from usernames;
select count(distinct uuid)
from users;

-- Get chat messages count per person with their most recent username
select current_username as username, count(*) as 'message count'
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

-- Count all messages containing a word per user
select current_username as username, count(*)
from (select * from chat_messages order by message_id desc)
where users_uuid is not NULL
  and message like '%example%'
group by users_uuid
order by count(*) desc;

-- Count all messages containing a word
select count(*)
from chat_messages
where message like '%example%';

-- Count total number of messages each user has sent with most recent username
select current_username as username, sum(length(message)) as 'message count'
from (select * from chat_messages order by message_id desc)
where users_uuid is not NULL
group by users_uuid
order by sum(length(message)) desc;


select * from usernames where username like 'example';

select user_ips.* from user_ips, usernames where username = 'example' and user_ips.users_uuid = usernames.users_uuid;

select * from usernames where username = 'example';

select * from commands where current_username = 'example';

select * from commands where command like '%nick%';

select * from usernames order by first_seen asc;

select * from user_ips inner join users u on u.uuid = user_ips.users_uuid

select * from user_ips u1, user_ips u2 where u1.users_uuid = u2.users_uuid and u1.log_in_date > date('2020-11-15') order by u2.log_in_date;