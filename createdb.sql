create table usr(
    id integer primary key,
    first_name integer,
    last_name integer,
    is_bot boolean,
    username varchar (255),
    admin boolean default False,
    blacklist boolean default False
);

create table tasks(
    task_id integer primary key,
    header varchar(255),
    body varchar(4095),
    createdtime float default 0,
    submittedtime float default 0,
    creator int,
    deadline float default 0,
    state integer default 0,
    common boolean default False,
    assignees varchar(255)
);

create table logger_table(
    id integer primary key,
    tg_id integer,
    task_id integer,
    FOREIGN KEY(tg_id) REFERENCES usr(tg_id),
    FOREIGN KEY(task_id) REFERENCES task(task_id)
);

create table notify(
    id integer primary key,
    value integer default 7,
    FOREIGN KEY(id) REFERENCES usr(id)
);

create table unauthorized_access(
    num integer primary key,
    id integer,
    first_name varchar(255),
    last_name varchar(255),
    is_bot boolean,
    username varchar(255),
    language_code varchar(255),
    time datetime
);

create table motherchat(
    id integer primary key,
    motherid integer default 0
);
