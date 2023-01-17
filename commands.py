from db import Db
import re
import emoji
import logging
from datetime import datetime


db = Db()

def get_task_by_tid(tid):
    status = ''
    task = db.get_task_by_tid(tid)
    if not task[6]:
        status = 'В работе'
    else:
        status = 'Выполнено'
    s = f"<b>Задача M{task[0]}:</b> {task[1]}\n\n"\
    f"<b>Статус:</b> {status}\n\n"\
    f"<b>Описание:</b> {task[2]}\n\n"\
    f"<b>Ответственные:</b> {task[8]}\n\n"\
    f"<b>Дедлайн:</b> {task[5]}\n\n"\
    f"<b>Создатель:</b> {task[4]}\n"\
    f"<b>Дата создания:</b> {task[3]}\n"
    return s



def list_headers(uid="", limit=0, offset=0):
    return db.fetch_headers(uid, limit, offset)


def get_table_size(table, user):
    if user and user == 'общее':
        return db.count_common_tasks(user)
    elif user:
        return db.count_usr_tasks(user)
    return db.get_table_size(table)


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


def make_lowerscore_remove_at(l):
    tmp = []
    for it in l:
        tmp.append(it.replace('@', '').lower())
    return tmp


def insert_new_task(task_dict, creator):
    log_row = {'tg_id': 0, 'task_id': 0, 'task_usr_id': 0}
    task_dict['creator'] = f'@{creator}'
    task_dict['created_datetime'] = datetime.now()
    assignees = task_dict['assignees']
    username_list = db.list_nicks()
    username_list = make_lowerscore_remove_at(username_list)    
    task_dict['assignees'] = ', '.join(task_dict['assignees'])
    if not assignees:
        task_dict['common'] = True
        db.insert("tasks", task_dict)
    else:
        task_id = db.insert("tasks", task_dict)
        for nick in task_dict['assignees'].split(', '):
            if nick.lower().replace('@', '') in username_list:
                tg_id = db.find_id_by_nick(nick)
                log_row['tg_id'] = tg_id
                log_row['task_id'] = task_id
                db.insert("logger_table", log_row)

def delete_task(tid):
    db.delete_tid_from_logger(tid)
    db.delete_tid_from_tasks(tid)


def check_done(tid):
    db.set_done(tid)
    return tid


def is_done(tid):
    return db.is_done(tid)


def get_id_from_usrname(username):
    return db.find_id_by_nick(username)


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


def report_trespasser(values):
    d = dict(values)
    d['time'] = datetime.now()
    db.register_unauthorized(d)

def is_owner(uid, tid):
    return db.is_owner(uid, tid)
