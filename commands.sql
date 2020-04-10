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

select count(distinct current_username)
from chat_messages;
select count(distinct username)
from usernames;
select count(distinct uuid)
from users;

update chat_messages
set users_uuid=(select users_uuid from usernames where username = current_username);

update chat_messages
set users_uuid=(select U.users_uuid
                from usernames as U
                where U.username = current_username
                group by U.users_uuid
                having count(distinct U.users_uuid) == 1);

select message_id
from chat_messages
order by message_id desc
limit 1;