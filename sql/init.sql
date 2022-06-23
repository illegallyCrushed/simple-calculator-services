CREATE DATABASE IF NOT EXISTS srv_calc;

USE srv_calc;

CREATE TABLE IF NOT EXISTS requests
(
    id               int auto_increment
        primary key,
    username         varchar(50)                          not null,
    type             varchar(20)                          not null,
    input            int                                  not null,
    start_timestamp  timestamp  default CURRENT_TIMESTAMP not null,
    finish_timestamp timestamp                            null,
    result           int                                  null,
    status           tinyint(1) default 0                 not null,
    constraint requests_id_uindex
        unique (id)
);

CREATE TABLE IF NOT EXISTS users
(
    username varchar(50)  not null
        primary key,
    password varchar(100) not null,
    constraint user_username_uindex
        unique (username)
);



