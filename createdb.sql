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

insert into usr(id, username, admin)
values
    ("5050470568", "filitim", True),
    ("157671471", "zubenjo", False),
    ("321863603", "mihailaksel1996", True),
    ("703247500", "mikhailgaliashkin", False),
    ("892444970", "troitske", False),
    ("1053423753", "natalya_kriv", True),
    ("468239947", "mariechen_sv", False),
    ("371450394", "ziggy2750", True),
    ("249892412", "norway_spruce", False),
    ("5744386776", "armaggedon1488", False);


insert into tasks(header, body, creator, common, createdtime)
values
    ("Задача 1", "Разобраться с тем, как работает бот", 5050470568, 1, 0.0),
    ("Задача 2", "Создать свою первую задачу", 5050470568, 1, 0.0),
    ("Задача 3", "Отметить задачи 1 и 2 как выполненные", 5050470568, 1, 0.0);
