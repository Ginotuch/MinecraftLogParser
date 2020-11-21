create table chat_messages
(
    message_id       varchar(22),
    send_date        date,
    current_rank     varchar(36),
    current_username varchar(16),
    users_uuid       char(36) default NULL,
    message          text,
    primary key (message_id),
    foreign key (users_uuid) references users (uuid)
);
create index uname_index on chat_messages (current_username);
create index date_index on chat_messages (send_date);
create index message_index on chat_messages (message);

create table commands
(
    command_id       varchar(22),
    send_date        date,
    current_username varchar(16),
    users_uuid       char(36) default NULL,
    command          text,
    primary key (command_id),
    foreign key (users_uuid) references users (uuid)
);
create index commands_uname_index on commands (current_username);
create index commands_command_index on commands (command);

create table users
(
    uuid       char(36),
    uuid_id    char(22),
    first_seen date,
    PRIMARY KEY (uuid),
    unique (uuid_id)
);
create index uuid_id_index on users (uuid_id);

create table user_ips
(
    log_in_id   varchar(22),
    users_uuid  char(36),
    ip          varchar(16),
    log_in_date date,
    foreign key (users_uuid) references users (uuid),
    primary key (log_in_id)
);
create index user_ips_users_uuid_index on user_ips (users_uuid);
create index ip_index on user_ips (ip);

create table usernames
(
    username_id varchar(22),
    users_uuid  char(36),
    username    varchar(16),
    first_seen  date,
    foreign key (users_uuid) references users (uuid),
    primary key (username_id),
    unique (username, users_uuid)
);
create index usernames_users_uuid_index on usernames (users_uuid);
create index username_index on usernames (username);
