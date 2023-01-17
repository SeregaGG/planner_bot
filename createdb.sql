create table usr(
    tg_id integer primary key,
    nickname varchar(255),
    is_admin boolean default False,
);

create table tasks(
    task_id integer primary key,
    header varchar(255),
    body varchar(4095),
    created_datetime datetime,
    creator varchar(255),
    deadline datetime,
    done boolean default False,
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
    ("5050470568", "filitim", True),
    ("157671471", "zubenjo", False),
    ("321863603", "mihailaksel1996", True),
    ("703247500", "mikhailgaliashkin", False),
    ("892444970", "Troitske", False),
    ("1053423753", "Natalya_kriv", True),
    ("468239947", "mariechen_sv", False),
    ("371450394", "Ziggy2750", True),
    ("249892412", "norway_spruce", False)

