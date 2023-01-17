check_db_exist = "SELECT name FROM sqlite_master WHERE type='table' AND name='usr'"
list_nicks = 'select nickname from usr'
list_uids = 'select tg_id from usr'
list_usernames = 'select nickname from usr'
list_admins = 'select tg_id from usr where is_admin=True'


def get_task_by_tid(tid):
    return f'select * from tasks where task_id={tid}'


def fetch_common(limit=0, offset=0):
    return  f'select task_id, header, done from tasks where common=1 order by'\
    f' created_datetime desc limit {limit} offset {limit*offset}'


def fetch_all(limit=0, offset=0):
    return f'select task_id, header, done from tasks order by created_datetime desc'\
            f' limit {limit} offset {limit*offset}'
    

def fetch_by_uid(uid, limit=0, offset=0):
    return f'select tasks.task_id, header, done from tasks inner join'\
            f' logger_table on tasks.task_id=logger_table.task_id'\
            f' where logger_table.tg_id = {uid} order by created_datetime desc'\
            f' limit {limit} offset {offset*limit}'


def make_admin(uid):
    return f'update usr set is_admin = True where tg_id = {uid}'

def remove_admin(uid):
    return f'update usr set is_admin = False where tg_id = {uid}'


def count_usr_tasks(uid):
    return f"select count(1) from tasks inner "\
            f"join logger_table on tasks.task_id=logger_table.task_id"\
            f" where logger_table.tg_id = '{uid}'"


def get_uid_from_tid(tid):
    return f'select logger_table.tg_id from tasks inner join logger_table on '\
        f'tasks.task_id = logger_table.task_id where logger_table.task_id={tid}'

def set_old_true(virt):
    return f'update tasks set old=True where task_id = {virt}'

def get_tid_from_new(tid):
    return f'select task_id from (select * from tasks where old=false)'\
            f' limit 1 offset {int(tid)-1}'


def get_tid(uid):
    return f'select logger_table.task_id from logger_table inner join'\
            f' usr on usr.tg_id=logger_table.tg_id  inner join tasks on '\
            f'tasks.task_id=logger_table.task_id where logger_table.tg_id='\
            f'{uid} and tasks.old=False'

def increase_oldc(oldc, inc, uid):
    return f'update usr set old_task_counter={oldc+inc} where tg_id={uid}'

def fetch_oldc(uid):
    return f'select old_task_counter from usr where tg_id={uid}'


def get_usr_task_counter(user_id):
    return  f"select task_counter from usr where tg_id={user_id}"


def get_id_by_nick(nickname):
    return f'select tg_id from usr where nickname = "{nickname}"'


def insert_general(table, columns, placeholders):
    return f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"


