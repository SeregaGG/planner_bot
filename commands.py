from db import Db
import re
import emoji
import logging
from datetime import datetime


db = Db()


def list_common_tasks():
    cmds = []
    l = db.fetch_tasks('common')
    result = 'Общие задачи:\n'
    for i, elem in enumerate(l, 1):
        result += f"{i}. {elem['mes']}" + '\n'
    result+= '\n'
    if not result:
        return "Список задач пуст"
    return result


def list_tasks(user_id = ""):
    if not user_id:
        l = db.fetch_tasks()
    else:
        l = db.fetch_tasks(user_id)
    result = ''
    for i, elem in enumerate(l, 1):
        result += f"{i}. {elem['mes'] }"
        if not elem['common']:
            if elem['done']:
                result += '\u2705'
            else:
                result += '\u25FB'
        result += '\n'

    if not result:
        return None
    return result


def get_ids():
    return db.list_ids()

def list_usernames():
    return db.list_usernames()


def _insert_task_rows(nick_list, cmd):
    row = {'task_name': cmd, 'created': datetime.now(), 'common': False}
    log_row = {'tg_id': 0, 'task_id': 0, 'task_usr_id': 0}
    if not nick_list:
        row['common'] = True
        task_id = db.insert("task", row)
    else:
        task_id = db.insert("task", row)
        for nick in nick_list:
            tg_id = db.find_id_by_nick(nick)
            task_usr_id = db.get_usr_task_counter(tg_id)
            db.set_usr_task_counter(tg_id, task_usr_id+1)
            log_row['task_usr_id'] = task_usr_id+1
            log_row['tg_id'] = tg_id
            log_row['task_id'] = task_id
            db.insert("logger_table", log_row)


def add_task(cmds):
    cmds = cmds.replace('/new_task ', '')
    cmds_list = cmds.split('\n')
    total_nicks=[]
    nicks = db.list_nicks()
    for cmd in cmds_list:
        logging.info(cmd)
        cmd = re.sub("\d\di[\*|)].\s", "", cmd, count=1)
        logging.info(cmd)
        nick_list = []
        for nick in nicks:
            if nick.lower() in cmd.lower():
                nick_list.append(nick)
        _insert_task_rows(nick_list, cmd)
        total_nicks.extend(nick_list)
    return len(cmds_list)


def check_done(uid, task_num):
    task_id = db.get_tid_from_tuid(uid, task_num)
    if task_id and not db.is_done(task_id):
        db.set_done(task_id)
        return task_id
    else:
        return 0

def remove_task(uid, task_nums):
    task_nums = task_nums.split('\n')
    logging.info(f'removing {task_nums}')
    uids_dict = db.make_old(task_nums)
    if uids_dict == -1:
        return 0
    elif uids_dict:
        state = db.increase_old_counter(uids_dict)
        if state == -1:
            return 0
    return 1

def get_id_from_usrname(username):
    return db.find_id_by_nick(username)

def remove_all():
    uids_dict = db.make_evrth_old()
    if uids_dict == -1:
        return 0
    elif uids_dict:
        state = db.increase_old_counter(uids_dict)
        if state == -1:
            return 0
    return 1


def make_admin(username, up_or_down):
    uid = get_id_from_usrname(username)
    if up_or_down:
        db.set_admin_up(uid)
    else:
        db.set_admin_down(uid)



def is_admin(uid):
    return db.is_admin(uid)

def list_admins():
    return db.list_admins()

def get_task(tuid):
    return db.get_task(tuid)

def report_trespasser(values):
    d = dict(values)
    d['time'] = datetime.now()
    db.register_unauthorized(d)

