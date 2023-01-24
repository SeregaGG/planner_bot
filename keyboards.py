from aiogram.types.reply_keyboard import ReplyKeyboardMarkup as RKM
from aiogram.types.inline_keyboard import InlineKeyboardMarkup as IKM
from aiogram.types.inline_keyboard import  InlineKeyboardButton as IK
from enums import TaskState, SortType
from task import Task
from user import User
from keys import cmdkey
import logging


class Keyboard:
    def __init__(self, limit=10):
        self.limit = limit
        self.user_main_kb = self.user_main_kb()
        self.admin_main_kb = self.admin_main_kb()
        self.admin_set_kb = self.admin_settings_kb()
        self.user_set_kb = None #todo
        self.new_task_inline = self.new_task_inline()


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
        btn1 = IK('Название', callback_data='add_task_header')
        btn2 = IK('Описание', callback_data='add_task_body')
        btn3 = IK('Ответственные', callback_data='add_task_assignees')
        btn4 = IK('Дедлайн', callback_data='add_task_deadline')
        btn5 = IK('Назад', callback_data='add_task_back')
        btn6 = IK('Сохранить', callback_data='add_task_save')
        AddTasksKb.row(btn1, btn2)
        AddTasksKb.row(btn3, btn4)
        AddTasksKb.row(btn5, btn6)
        return AddTasksKb


    def go_back_kb(self, callback):
        MBack = IKM(resize_keyboard=True)
        MBack.row(IK(cmdkey['back'], callback_data = callback))
        return MBack

    def adminlist(self):
        kboard = IKM()
        admins = User().adminlist()
        row = []
        for i, a in enumerate(admins, 0):
            callback = f"ch_admins_{a['id']}_{a['admin']}"
            if a['admin']:
                text = f"🌚@{a['username']}"
            else:
                text = f"@{a['username']}"
            row.append(IK(text, callback_data=callback))
            if i>0 and i%2 == 0:
                if len(row)>1:
                    kboard.row(row[0], row[1])
                else:
                    kboard.row(row[0], IK(' ', callback_data='empty'))
                row = []
        kboard.row(IK(cmdkey['back'], callback_data='ch_admins_save'))
        return kboard


    def assignees_inline(self, command=''):
        kb = IKM()
        usernames = User().usernamelist(mention=1)
        for i in range(0, len(usernames), 2):
            k1 = IK(usernames[i], callback_data=f'{command}_assignees_{usernames[i]}')
            if i+1 < len(usernames):
                k2 = IK(usernames[i+1], callback_data=f'{command}_assignees_{usernames[i+1]}')
            else:
                k2 = IK(' ', callback_data=f'empty')
            kb.row(k1, k2)
        kb.row(IK('Сохранить', callback_data = f'{command}_assignees_save'))
        return kb
        
        

    def form_permission_choice(self, is_admin):
        UsrEdit = RKM(resize_keyboard=True)
        if is_admin:
            choice = ReplyKeyboardButton('Снять админа', callback_data='Снять админа')
            back = ReplyKeyboardButton('Назад', callback_data='Назад')
        else:
            choice = ReplyKeyboardButton('Сделать админом', callback_data='Сделать админом')
            back = ReplyKeyboardButton('Назад', callback_data='Назад')
        UsrEdit.row(choice, back)
        return UsrEdit


    def form_menu(self, offset, tasks_size, username, tid):
        ch = {'more': '>', 'less': '<', 'under': '_',
            'ou': f'{offset}/{tasks_size//self.limit+1} ({username})',
            'o': f'{offset}/{tasks_size//self.limit+1}'}
        cb = {
            'more': f'task_btn_shift_forward_{tid}',
            'less': f'task_btn_shift_back_{tid}',
            'under': 'btn_empty',
            'ofbtn': 'task_btn_offset'
        }
        back = IK(ch['less'], callback_data=cb['less']) \
            if offset>1 else IK(ch['under'], callback_data=cb['under'])
        forward = IK(ch['more'], callback_data=cb['more']) \
            if tasks_size-(offset*self.limit) > 0 else IK(ch['under'], callback_data=cb['under'])
        count = IK(ch['ou'], callback_data=cb['ofbtn']) if username \
            else IK(ch['o'], callback_data=cb['ofbtn'])
        return back, forward, count


    def form_tasks(self, TasksKb, order, uid, offset, tsize):
        tasks = Task().task_headers(uid, self.limit, offset-1, order)
        for header in tasks:
            T = Task()
            T.load_from_header(header)
            status = T.get_status()
            s = f"{status[0]}[#{T.attr.task_id}] {T.attr.header}"
            TasksKb.row(IK(s, callback_data = f"task_btn_show_{T.attr.task_id}"))
        return TasksKb


    def submit_button(self, uid, tid):
        text = callback = ''
        user = User(uid)
        user.from_database()
        if  tid != 0 and user.is_assignee(tid):
            text = f'Сдать задачу #{tid}'
            callback = f'btn_submit_{tid}'
        else:
            return None
            callback = f'btn_submit_{tid}'
        return IK(text, callback_data=callback)


    def tasklist_inline(self, uid, tid=0, offset=1, username='', order=SortType.CREATION):
        TasksKb = IKM()
        tasks_size = Task().table_size(order, username=username)
        if username:
            others_username = User().username_to_id(username)
            TasksKb = self.form_tasks(TasksKb, order, others_username, offset, tasks_size)
        else:
            TasksKb = self.form_tasks(TasksKb, order, uid, offset, tasks_size)
            
        if order == SortType.COMMON:
            back, forward, count = self.form_menu(offset, tasks_size, 'общ', tid)
        else:
            back, forward, count = self.form_menu(offset, tasks_size, username, tid)
        TasksKb.row(back, count, forward)
        submitbut = self.submit_button(uid, tid)
        if submitbut:
            TasksKb.row(submitbut)
        return TasksKb

