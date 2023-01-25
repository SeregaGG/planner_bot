from aiogram.types.reply_keyboard import ReplyKeyboardMarkup as RKM
from aiogram.types.inline_keyboard import InlineKeyboardMarkup as IKM
from aiogram.types.inline_keyboard import  InlineKeyboardButton as IK
from enums import SortType
from enums import TaskState as TS
from task import Task
from user import User
from keys import cmdkey, inline
import logging
from cquery import Cquery


class Keyboard:
    def __init__(self, limit=10):
        self.limit = limit
        self.user_main_kb = self.user_main_kb()
        self.admin_main_kb = self.admin_main_kb()
        self.admin_set_kb = self.admin_settings_kb()
        self.user_set_kb = None #todo
        self.new_task_inline = self.new_task_inline()
        self.my_tasks =  self.my_tasks_inline()


    def main(self, user: User):
        if (user.is_admin()):
            return self.admin_main_kb
        return self.user_main_kb


    def stngs(self, user):
        return self.admin_set_kb


    def newtask(self):
        return self.new_task_inline


    def user_main_kb(self):
        '''Reply keyboard for general user'''
        Mk = RKM(resize_keyboard=True)
        Mk.row(cmdkey['my'], cmdkey['all'], cmdkey['common'])
        Mk.row(cmdkey['others'], cmdkey['create'], cmdkey['settings'])
        return Mk


    def admin_main_kb(self):
        #Reply keyboard for admin
        Mk = RKM(resize_keyboard=True)
        Mk.row(cmdkey['my'], cmdkey['all'], cmdkey['common'])
        Mk.row(cmdkey['others'], cmdkey['create'], cmdkey['settings'])
        return Mk


    def admin_settings_kb(self):
        Ak = IKM()
        noti = IK('🔈Уведомления', callback_data='settings_notifications')
        delete = IK('🚫Удалить задачу', callback_data='settings_delete')
        admin = IK('🌚Админы', callback_data='settings_admins')
        back = IK('↩Назад', callback_data='settings_back')
        deluser = IK('👮Удалить участника', callback_data = 'settings_deluser')
        Ak.row(noti, admin,)
        Ak.row(deluser, delete)
        Ak.row(back)
        return Ak


    def new_task_inline(self):
        '''Creating Inline keyboard for adding task command'''
        AddTasksKb = IKM(resize_keyboard=True)
        btn1 = IK('Название', callback_data=f'{inline["addtask"]}_header')
        btn2 = IK('Описание', callback_data=f'{inline["addtask"]}_body')
        btn3 = IK('Ответственные', callback_data=f'{inline["addtask"]}_assignees')
        btn4 = IK('Дедлайн', callback_data=f'{inline["addtask"]}_deadline')
        btn5 = IK('Назад', callback_data=f'{inline["addtask"]}_back')
        btn6 = IK('Сохранить', callback_data=f'{inline["addtask"]}_save')
        AddTasksKb.row(btn1, btn2)
        AddTasksKb.row(btn3, btn4)
        AddTasksKb.row(btn5, btn6)
        return AddTasksKb


    def go_back_kb(self, callback):
        MBack = IKM(resize_keyboard=True)
        MBack.row(IK(cmdkey['back'], callback_data = callback))
        return MBack

    def adminlist(self):
        kb = IKM()
        a = User().adminlist()
        for i in range(0, len(a), 2):
            callback = Cquery({'userid': a[i]['id'], 'is_admin': a[i]['admin']}, inline['chadmin'])
            text = f"🌚@{a[i]['username']}" if a[i]['admin'] else f"@{a[i]['username']}"
            k1 = IK(text, callback_data=callback.generatecq())
            if i+1 < len(a):
                callback = Cquery({'userid': a[i+1]['id'], 'is_admin': a[i+1]['admin']}, 
                                                                                inline['chadmin'])
                text = f"🌚@{a[i+1]['username']}" if a[i+1]['admin'] else f"@{a[i+1]['username']}"
                k2 = IK(text, callback_data=callback.generatecq())
            else:
                k2 = IK(' ', callback_data=f'empty')
            kb.row(k1, k2)
        callback = Cquery({'userid': 0}, inline['chadmin'])
        kb.row(IK(cmdkey['back'], callback_data=callback.generatecq()))
        logging.info(kb)
        return kb


    def my_tasks_inline(self):
        cq1 = Cquery({'order': SortType.DEADLINE.value}, inline['mytask'])
        cq2 = Cquery({'order': SortType.SETTER.value}, inline['mytask'])
        a = IK('Я - исполнитель', callback_data=cq1.generatecq())
        b = IK('Я - постановщик', callback_data=cq2.generatecq())
        return IKM().row(a, b)


    def assignees_inline(self, cmd='', save_option = 0):
        kb = IKM()
        users = User().userlist()
        for i in range(0, len(users), 2):
            callback = Cquery({'userid': users[i]['id']}, cmd)
            k1 = IK(f"@{users[i]['username']}", callback_data=callback.generatecq())
            if i+1 < len(users):
                callback = Cquery({'userid': users[i+1]['id']}, cmd)
                k2 = IK(users[i+1]['username'], callback_data=callback.generatecq())
            else:
                k2 = IK(' ', callback_data=f'empty')
            kb.row(k1, k2)
        if save_option:
            callback = Cquery({'userid': 0}, cmd)
            kb.row(IK('Сохранить', callback_data = callback.generatecq()))
        return kb
        
        
    def form_menu(self,tasks_size, cq):
        if cq['offset'] > 1:
            cq['dir'] = -1
            callback = Cquery(cq, inline['shift'])
            back = IK('<', callback_data=callback.generatecq())
        else:
            back = IK('_', callback_data='empty')
        if tasks_size-(cq['offset']*self.limit) > 0:
            cq['dir'] = 1
            callback = Cquery(cq, inline['shift'])
            forward = IK('>', callback_data=callback.generatecq())
        else:
            forward = IK('_', callback_data='empty')
        count = IK(f"{cq['offset']}/{tasks_size//self.limit+1}", callback_data='empty')
        return back, forward, count


    def form_tasks(self, TasksKb, tsize, cq):
        tasks = Task().task_headers(cq['owneruid'], self.limit, cq['offset']-1, SortType(cq['order']))
        for header in tasks:
            T = Task()
            T.load_from_header(header)
            status = T.get_status()
            s = f"{status[0]}[#{T.attr.task_id}] {T.attr.header}"
            cq['btntid'] = T.attr.task_id
            callback = Cquery(cq, inline['show'])
            TasksKb.row(IK(s, callback_data = callback.generatecq()))
        return TasksKb


    def submit_button(self, uid, cq, TasksKb):
        user = User(uid)
        task = Task(cq['tid'])
        task.load_from_db()
        user.from_database()
        logic1 =  user.is_assignee(cq['tid']) and task.attr.state == TS.IN_PROCESS
        logic2 = uid == task.attr.creator and task.attr.state == TS.AWAITING_SUBMIT 
        logic3 = user.is_assignee(cq['tid']) and task.attr.state == TS.AWAITING_START
        logic4 = uid == task.attr.creator and task.attr.common == 1 and task.attr.state != TS.DONE
        if logic1: 
            text = f"☑ Сдать задачу #{cq['tid']}"
            cq['state'] = TS.AWAITING_SUBMIT.value
            callback = Cquery(cq, inline['state'])
            TasksKb.row(IK(text, callback_data=callback.generatecq()))
        elif logic2 or logic4:
            text = f'✅Принять #{cq["tid"]}'
            cq['state'] = TS.DONE.value
            callback = Cquery(cq, inline['state'])
            gen1 = callback.generatecq()
            if logic2:
                text2 = f'❌Вернуть #{cq["tid"]}'
                cq['state'] = TS.IN_PROCESS.value
                callback = Cquery(cq, inline['state'])
                gen2 = callback.generatecq()
                TasksKb.row(IK(text, callback_data=gen1),IK(text2, callback_data=gen2))
            else:
                TasksKb.row(IK(text, callback_data=gen1))
        elif logic3:
            text = f'🏋Приступить к задаче'
            cq['state'] = TS.IN_PROCESS.value
            callback = Cquery(cq, inline['state'])
            TasksKb.row(IK(text, callback_data=callback.generatecq()))


    def tasklist_inline(self, uid, tid=0, offset=1, owner_uid=0, order=SortType.CREATION.value):
        cq = {'offset': offset, 'owneruid': owner_uid, 'tid': tid, 'order': order}
        TasksKb = IKM()
        tasks_size = Task().table_size(SortType(order), uid=owner_uid)
        TasksKb = self.form_tasks(TasksKb, tasks_size, cq)
        back, forward, count = self.form_menu(tasks_size, cq)
        TasksKb.row(back, count, forward)
        if tid:
            self.submit_button(uid, cq, TasksKb)
        return TasksKb

