from db import Db as database
import logging
from datetime import datetime, timedelta
from enums import TaskState, SortType, TIMEFORMAT
from user import User

class DbAttr:
    def __init__(self):
        self.task_id = None
        self.header = None
        self.body = None
        self.createdtime = None
        self.submittedtime = None
        self.creator = None
        self.deadline = None
        self.state = None
        self.common = None


class Task:

    def __init__(self, tid=0, header=[]):
        self.db = database()
        self.attr = DbAttr()
        self.assignees = []
        if header:
            self.load_from_header(header)
        elif tid:
            self.attr.task_id = tid


    def fill_attr(self, info):
        self.attr.header = info[1]
        self.attr.body = info[2]
        self.attr.createdtime = datetime.fromtimestamp(float(info[3]))
        self.attr.submittedtime = datetime.fromtimestamp(info[4])
        self.attr.creator = info[5]
        self.attr.deadline = datetime.fromtimestamp(float(info[6]))
        self.attr.state = TaskState(info[7])
        self.attr.common = info[8]


    def load_from_db(self):
        info = self.db.get_table_row('tasks', ['*'], {'task_id': self.attr.task_id})
        if not info:
            raise ValueError("Unexisting task id")
        self.fill_attr(info)
        self.assignees=self.db.get_table_column('logger_table', 'tg_id', {'task_id': self.attr.task_id})


    def load_from_header(self, header):
        self.attr.task_id = header['task_id']
        self.attr.header = header['header']
        self.attr.state = TaskState(header['state'])
        self.attr.deadline = datetime.fromtimestamp(header['deadline'])


    def save_to_db(self):
        log_row = {'tg_id': 0, 'task_id': 0}
        if not self.assignees:
            self.attr.common = True
        self.attr.createdtime = datetime.now().timestamp()
        self.attr.state = TaskState.AWAITING_START
        self.attr.assignees = ', '.join(self.assignees)
        self.attr.task_id = self.db.insert("tasks", self.as_dict())
        if self.assignees:
            id_list = self.db.username_to_id(user_list=self.assignees)
        for username in self.assignees:
            log_row['tg_id'] = id_list[username]
            log_row['task_id'] = self.attr.task_id
            self.db.insert("logger_table", log_row)


    def as_dict(self):
        d = {}
        for a in dir(self.attr):
            if a == 'state' and getattr(self.attr, a)!=None:
                d[a] = getattr(self.attr, a).value
            elif (not a.startswith('__')) and getattr(self.attr, a)!=None:
                d[a] = getattr(self.attr, a)
        return d


    def delete(self, tid):
        self.db.delete('tasks', ['task_id', tid]) 
        self.db.delete('logger_table', ['task_id', tid]) 
        

    
    def table_size(self, order: SortType, uid=0, username=''):
        if not uid and username:
            uid = self.db.username_to_id(username)
        if order == SortType.DEADLINE:
            join = 'join logger_table on tasks.task_id = logger_table.task_id'
            return self.db.get_table_size("tasks", {'id': uid}, join)
        elif order == SortType.CREATION:
            return self.db.get_table_size("tasks")
        elif order == SortType.COMMON:
            return self.db.get_table_size("tasks", {'common': 1})
        else:
            raise ValueError("Wrong SortType")



    def task_headers(self, uid, limit, offset, sort):
        return self.db.sorted_headers(uid, limit, offset, sort)


    def calc_delta(self, delta):
        if delta > timedelta(days=7):
            return f"⏱{delta.days} дней"
        elif delta > timedelta(days=7):
            return "⏱1 неделя"
        elif delta > timedelta(days = 1):
            return f"⏱{delta.days} дней"
        elif delta > timedelta(hours = 1):
            return f"⏱{delta.seconds//3600} часов"
        elif delta > timedelta(seconds = 0):
            return f"⏱{(delta.seconds//60)%60} минут"
        else:
            return ''

        
    def get_status(self):
        status_dict = {
            'done': '\u2705 Выполнено',
            'submit': '\u2705 Выполнено (Ожидает подвтерждения)',
            'proc': '\u25FB В работе',
            'wait': '\u25FB Не принят в работу',
            'hurry': '🟧 В работе',
            'late':  '🟥 Дедлайн истек'
        }
        status = ''
        delta = self.attr.deadline - datetime.now()
        common = datetime.fromtimestamp(0)
        if self.attr.state == TaskState.DONE:
            return status_dict['done']
        elif self.attr.state == TaskState.AWAITING_SUBMIT:
            return status_dict['submit']
        elif self.attr.state ==  TaskState.IN_PROCESS or self.attr.state == TaskState.AWAITING_START:
            if self.attr.deadline != common and delta <= timedelta(days=0):
                return f"{status_dict['late']} {self.calc_delta(delta)}"
            elif self.attr.deadline != common and delta < timedelta(days=2):
                return f"{status_dict['hurry']} {self.calc_delta(delta)}"
            return f"{status_dict['proc']} {self.calc_delta(delta)}"


    def show(self):
        deadline = 'без дедлайна'
        assignees = ''
        if self.attr.deadline != datetime.fromtimestamp(0):
            deadline = self.attr.deadline.strftime(TIMEFORMAT)
        if self.assignees:
            logging.info(self.assignees)
            assignees_list = User().id_to_username(uid_list=self.assignees)
            for i in range(0, len(assignees_list)):
                assignees_list[i] = f'@{assignees_list[i]}'
            assignees = ', '.join(assignees_list)
        creator = User().id_to_username(self.attr.creator)
        s = f"🪧 <b>Задача {self.attr.task_id}:</b> {self.attr.header}\n\n"\
        f"{self.get_status()} (🗓{deadline})\n\n"\
        f"📝<b>Описание</b>: {self.attr.body}\n\n"\
        f"🥷🥷@{creator}  ⏩  {assignees}\n\n"\
        f"<b>Дата создания:</b> {self.attr.createdtime.strftime(TIMEFORMAT)}\n\n"\
        f"<pre>                                &#x200D</pre>"
        return s


    def check_done(tid = 0):
        if not uid:
            tid = self.attr.task_id
            self.attr.state = TaskState.AWAITING_SUBMIT
        state = TaskState.AWAITING_SUBMIT.value
        self.db.update("usr", {'state': state}, {'task_id': tid})
