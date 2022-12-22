create table usr(
    tg_id integer primary key,
    nickname varchar(255),
    is_admin boolean default False,
    task_counter integer default 0,
    old_task_counter integer default 0
);

create table task(
    task_id integer primary key,
    task_name varchar(255),
    created datetime,
    deadline date,
    done boolean default False,
    common boolean default False,
    old boolean default False
);

create table logger_table(
    id integer primary key,
    tg_id integer,
    task_id integer,
    task_usr_id integer,
    FOREIGN KEY(tg_id) REFERENCES usr(tg_id),
    FOREIGN KEY(task_id) REFERENCES task(task_id)
);

create table unauthorized_access(
    num integer primary key,
    id integer,
    first_name integer,
    last_name integer,
    is_bot boolean,
    username varchar (255),
    language_code varchar(255),
    time datetime
);

insert into usr(tg_id, nickname, is_admin)
values
    ("398914847", "@timafefi", True),
    ("157671471", "@zubenjo", False),
    ("321863603", "@mihailaksel1996", True),
    ("703247500", "@mikhailgaliashkin", False),
    ("892444970", "@Troitske", False),
    ("1053423753", "@Natalya_kriv", True),
    ("468239947", "@mariechen_sv", False),
    ("371450394", "@Ziggy2750", True),
    ("249892412", "@norway_spruce", False)

