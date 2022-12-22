check_db_exist = "SELECT name FROM sqlite_master WHERE type='table' AND name='usr'"
fetch_new_all = 'select task_name, done, common from task where old=False'
fetch_new_common = 'select task_name, done, common from task where common=1 and old=False'
list_nicks = 'select nickname from usr'
list_uids = 'select tg_id from usr'
list_usernames = 'select nickname from usr'
list_admins = 'select tg_id from usr where is_admin=True'



def make_admin(uid):
    return f'update usr set is_admin = True where tg_id = {uid}'

def remove_admin(uid):
    return f'update usr set is_admin = False where tg_id = {uid}'


def count_usr_tasks(uid):
    return f'select count(task.task_id) from task inner '\
            f'join logger_table on task.task_id=logger_table.task_id'\
            f' where logger_table.tg_id = {uid} and old=False'


def get_uid_from_tid(tid):
    return f'select logger_table.tg_id from task inner join logger_table on '\
        f'task.task_id = logger_table.task_id where logger_table.task_id={tid}'

def set_old_true(virt):
    return f'update task set old=True where task_id = {virt}'

def get_tid_from_new(tid):
    return f'select task_id from (select * from task where old=false)'\
            f' limit 1 offset {int(tid)-1}'

def tid_from_tnum(uid):
    return f'select logger_table.tg_id, usr.task_counter,'\
        f' usr.old_task_counter, logger_table.task_usr_id from'\
        f' logger_table inner join usr on usr.tg_id ='\
        f' logger_table.tg_id where usr.tg_id={uid} and '\
        f'(logger_table.task_usr_id - usr.old_task_counter) = task_num'

def get_tid(uid):
    return f'select logger_table.task_id from logger_table inner join'\
            f' usr on usr.tg_id=logger_table.tg_id  inner join task on '\
            f'task.task_id=logger_table.task_id where logger_table.tg_id='\
            f'{uid} and task.old=False'

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


def fetch_new_by_uid(uid):
    return f'select task_name, done, common from task inner join'\
            f' logger_table on task.task_id=logger_table.task_id'\
            f' where logger_table.tg_id = {uid} and old=False'
