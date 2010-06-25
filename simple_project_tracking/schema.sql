drop table if exists projects;
drop table if exists clients;
drop table if exists users;

create table clients (
  id integer primary key autoincrement,
  name string not null unique,
  department string not null,
  created timestamp,
  updated timestamp
);

create table projects (
  id integer primary key autoincrement,
  title string not null unique,
  description string not null,
  client_id integer,
  created timestamp,
  updated timestamp,
  FOREIGN KEY(client_id) REFERENCES clients(id)
);

create table users (
  user_id integer primary key autoincrement, 
  username string not null,
  email string not null,
  pw_hash string not null
);

