from datetime import datetime
from db import Db
from aiogram.types import Message
import logging


class DbAttr:
    def __init__(self):
        self.id = None
        self.first_name = None
        self.last_name = None
        self.is_bot = None
        self.username = None
        self.admin = None


class User:

    def __init__(self, uid = None, username = None, message: Message = None):
        self.db = Db()
        self.attr = DbAttr()
        self.tasks = []
        if message:
            self.from_message(message)
        else:
            self.attr.id = uid
            self.attr.username = username


    def from_message(self, message: Message):
        mes = message.from_user
        self.attr.id = mes.id
        self.attr.username = mes.username
        self.attr.first_name = mes.first_name
        self.attr.last_name = mes.last_name
        self.attr.is_bot = mes.is_bot


    def user_tasks(self):
        self.tasks = self.db.get_table_column("logger_table", "task_id", {'tg_id': self.attr.id})
        return self.tasks
    

    def from_database(self):
        if not self.attr.id:
            if self.attr.username:
                self.attr.id = self.username_to_id(self.attr.username)
            else:
                raise ValueError("Either id or username must be set")
        columns = [a for a in dir(self.attr) if not a.startswith('__')]
        info = self.db.get_table_row("usr", columns, {'id': self.attr.id})
        if info:
            for key in columns:
                setattr(self.attr, key, info[key])


    def to_database(self):
        if self.attr.id in self.idlist():
            self.db.update("usr", self.as_dict(), {'id':self.attr.id})
        else:
            self.db.insert("usr", self.as_dict())
        
        
    def username_to_id(self, username='', user_list=[]):
        if user_list:
            return self.db.username_to_id(user_list=user_list)
        elif username:
            return self.db.username_to_id(username=username)
        return None
            


    def id_to_username(self, uid='', uid_list=[]):
        if uid_list:
            return self.db.id_to_username(uid_list=uid_list)
        elif uid:
            return self.db.id_to_username(uid=uid)
        return None
          


    def is_assignee(self, tid):
        if tid in self.user_tasks():
            return True
        return False


    def adminlist(self):
        return self.db.list_admins()


    def usernamelist(self, mention=0):
        user_list = self.db.get_table_column("usr", "username")
        if mention:
            for i in range(0, len(user_list)):
                user_list[i] = f'@{user_list[i]}'
        return user_list


    def idlist(self):
        l = self.db.get_table_column("usr", 'id')
        return l


    def is_admin(self, uid=0):
        if not uid:
            uid = self.attr.id
        return self.db.get_table_column("usr", "admin", {"id": uid})[0]


    def as_dict(self):
        d = {}
        for a in dir(self.attr):
            if (not a.startswith('__')) and getattr(self.attr, a)!=None:
                d[a] = getattr(self.attr, a)
        return d


    def show_stats(self, username=''):
        if username:
            uid = self.username_to_id(username)
            s = f'<b>Задачи 👤@{username}:</b>\n\n'\
            f'<i>Активных задач:</i> {self.db.count_active(uid)}\n'\
            f'<i>В работе:</i> {self.db.count_inproc(uid)}\n'\
            f'<i>Завершенных:</i> {self.db.count_done(uid)}\n'\
            f'<i>Всего задач:</i> {self.db.user_stats()}\n'\
            f"<pre>                                &#x200D</pre>"
        else:
            s = f'<b>Все задачи:</b>\n\n'\
            f'<i>Активных задач:</i> {self.db.count_active()}\n'\
            f'<i>В работе:</i> {self.db.count_inproc()}\n'\
            f'<i>Завершенных:</i> {self.db.count_done()}\n'\
            f'<i>Всего задач:</i> {self.db.user_stats()}\n'\
            f"<pre>                                &#x200D</pre>"
        return s


    def make_admin(self, uid, state):
        if not uid:
            uid = self.attr.id
            self.attr.admin = state
        self.db.update('usr', {'admin': state}, {'id': uid})


    def del_users(self, users: list):
        if not users:
            return
        for user in users:
            self.db.delete('usr', ['username', f"'{user}'"])
