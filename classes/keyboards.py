from aiogram.types.reply_keyboard import ReplyKeyboardMarkup
from aiogram.types.inline_keyboard import InlineKeyboardMarkup
from aiogram.types.inline_keyboard import InlineKeyboardButton
from constants.enums import SortType, TaskState
from classes.task import Task
from classes.user import User
from constants.keys import cmdkey, inline
from classes.cquery import Cquery


class Keyboard:
    def __init__(self, limit=10):
        self.limit = limit
        self.main = self.create_main_keyboard()
        self.new_task_inline = self.create_task_inline()
        self.my_tasks = self.create_my_tasks_keyboard()

    def new_task(self):
        return self.new_task_inline

    def create_register_keyboard(self):
        register_keyboard = InlineKeyboardMarkup()
        register_keyboard.row(InlineKeyboardButton('Добавить меня', callback_data='register_submit'))
        register_keyboard.row(InlineKeyboardButton('Создать рабочее пр-во\n(админ)', callback_data='register_creat'))
        return register_keyboard

    def create_main_keyboard(self):
        # Reply keyboard for admin
        main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        main_keyboard.row(cmdkey['my'], cmdkey['all'], cmdkey['common'])
        main_keyboard.row(cmdkey['others'], cmdkey['create'], cmdkey['settings'])
        return main_keyboard

    def create_admin_settings_kb(self, is_admin: bool = False):
        admin_keyboard = InlineKeyboardMarkup()
        notification_button = InlineKeyboardButton('🔈Уведомления', callback_data='settings_notifications')
        delete_taks_button = InlineKeyboardButton('🚫Удалить задачу', callback_data='settings_delete')
        admin_button = InlineKeyboardButton('🌚Админы', callback_data='settings_admins')
        back_button = InlineKeyboardButton('↩Назад', callback_data='settings_back')
        delete_user_button = InlineKeyboardButton('👮Удалить участника', callback_data='settings_deluser')
        if is_admin:
            admin_keyboard.row(notification_button, admin_button)
            admin_keyboard.row(delete_user_button, delete_taks_button)
            admin_keyboard.row(back_button)
        else:
            admin_keyboard.row(notification_button, back_button)
        return admin_keyboard

    def create_notification_menu(self, fy):
        notification_menu = InlineKeyboardMarkup()
        emoji = '🌚'
        week_period = emoji + 'За неделю' if fy.week else 'За неделю'
        two_days_period = emoji + 'За 2 дня' if fy.day2 else 'За 2 дня'
        one_day_period = emoji + 'За день' if fy.day else 'За день'
        notification_menu.row(InlineKeyboardButton(week_period, callback_data='notifi_week'))
        notification_menu.row(InlineKeyboardButton(two_days_period, callback_data='notifi_2'))
        notification_menu.row(InlineKeyboardButton(one_day_period, callback_data='notifi_1'))
        notification_menu.row(InlineKeyboardButton('Сохранить и выйти', callback_data='notifi_back'))
        return notification_menu

    def create_task_inline(self):
        '''Creating Inline keyboard for adding task command'''
        add_task_keyboard = InlineKeyboardMarkup(resize_keyboard=True)

        task_title = InlineKeyboardButton('Название', callback_data=f'{inline["addtask"]}_header')
        task_description = InlineKeyboardButton('Описание', callback_data=f'{inline["addtask"]}_body')
        task_assignees = InlineKeyboardButton('Ответственные', callback_data=f'{inline["addtask"]}_assignees')
        task_deadline = InlineKeyboardButton('Дедлайн', callback_data=f'{inline["addtask"]}_deadline')
        back_button = InlineKeyboardButton('Назад', callback_data=f'{inline["addtask"]}_back')
        save_button = InlineKeyboardButton('Сохранить', callback_data=f'{inline["addtask"]}_save')

        add_task_keyboard.row(task_title, task_description)
        add_task_keyboard.row(task_assignees, task_deadline)
        add_task_keyboard.row(back_button, save_button)

        return add_task_keyboard

    def create_back_keyboard(self, callback):
        back_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        back_keyboard.row(InlineKeyboardButton(cmdkey['back'], callback_data=callback))
        return back_keyboard

    def create_admin_list_keyboard(self):
        admins_keyboard = InlineKeyboardMarkup()
        admins = User().adminlist()

        for admin in admins:
            callback = Cquery({'userid': admin['id'], 'is_admin': admin['admin']}, inline['chadmin'])
            admin_info = f"🌚@{admin['username']}" if admin['admin'] else f"@{admin['username']}"
            admin_button = InlineKeyboardButton(admin_info, callback_data=callback.generatecq())
            admins_keyboard.row(admin_button)

        callback = Cquery({'userid': 0}, inline['chadmin'])
        admins_keyboard.row(InlineKeyboardButton(cmdkey['back'], callback_data=callback.generatecq()))
        return admins_keyboard

    def create_my_tasks_keyboard(self):
        deadline_query = Cquery({'order': SortType.DEADLINE.value}, inline['mytask'])
        deadline_setter = Cquery({'order': SortType.SETTER.value}, inline['mytask'])

        task_assignee = InlineKeyboardButton('⛏Я - исполнитель', callback_data=deadline_query.generatecq())
        task_creator = InlineKeyboardButton('🧠Я - постановщик', callback_data=deadline_setter.generatecq())

        my_tasks = InlineKeyboardMarkup().row(task_assignee, task_creator)

        return my_tasks

    def create_assignees_keyboard(self, cmd='', save_option: bool = False):
        assignees_keyboard = InlineKeyboardMarkup()
        users = User().userlist()

        for user in users:
            callback = Cquery({'userid': user['id']}, cmd)
            user_button = InlineKeyboardButton(f"@{user['username']}", callback_data=callback.generatecq())
            assignees_keyboard.row(user_button)

        if save_option:
            callback = Cquery({'userid': 0}, cmd)
            assignees_keyboard.row(InlineKeyboardButton('Сохранить и выйти', callback_data=callback.generatecq()))

        return assignees_keyboard

    def get_form_menu_buttons(self, tasks_size, cq):
        if cq['offset'] > 1:
            cq['dir'] = -1
            callback = Cquery(cq, inline['shift'])
            back_button = InlineKeyboardButton('<', callback_data=callback.generatecq())
        else:
            back_button = InlineKeyboardButton('_', callback_data='empty')
        if tasks_size - (cq['offset'] * self.limit) > 0:
            cq['dir'] = 1
            callback = Cquery(cq, inline['shift'])
            forward_button = InlineKeyboardButton('>', callback_data=callback.generatecq())
        else:
            forward_button = InlineKeyboardButton('_', callback_data='empty')

        limit = tasks_size // self.limit

        is_over_limit = limit != 0

        task_count_button = InlineKeyboardButton(f"{cq['offset']}/{limit + is_over_limit}", callback_data='empty')
        return back_button, forward_button, task_count_button

    def create_form_tasks_keyboard(self, tasks_keyboard, cq):
        all_tasks = Task().task_headers(cq['owneruid'], self.limit, cq['offset'] - 1, SortType(cq['order']))

        for header in all_tasks:
            task = Task()
            task.load_from_header(header)

            status = task.get_status()
            formatted_status = f"{status[0]}[#{task.attr.task_id}] {task.attr.header}"

            cq['btntid'] = task.attr.task_id
            callback = Cquery(cq, inline['show'])

            tasks_keyboard.row(InlineKeyboardButton(formatted_status, callback_data=callback.generatecq()))

        return tasks_keyboard

    def create_submit_button(self, uid, cq, tasks_keyboard):
        user = User(uid)
        task = Task(cq['tid'])
        task.load_from_db()
        user.from_database()
        is_in_process = user.is_assignee(cq['tid']) and task.attr.state == TaskState.IN_PROCESS
        is_awaiting_submit = uid == task.attr.creator and task.attr.state == TaskState.AWAITING_SUBMIT
        is_awaiting_start = user.is_assignee(cq['tid']) and task.attr.state == TaskState.AWAITING_START
        is_done = uid == task.attr.creator and task.attr.common == 1 and task.attr.state != TaskState.DONE
        if is_in_process:
            done_message = f"☑ Сдать задачу #{cq['tid']}"
            cq['state'] = TaskState.AWAITING_SUBMIT.value
            callback = Cquery(cq, inline['state'])
            tasks_keyboard.row(InlineKeyboardButton(done_message, callback_data=callback.generatecq()))
        elif is_awaiting_submit or is_done:
            submit_massage = f'✅Принять #{cq["tid"]}'
            cq['state'] = TaskState.DONE.value
            callback = Cquery(cq, inline['state'])
            gen1 = callback.generatecq()
            if is_awaiting_submit:
                reject_message = f'❌Вернуть #{cq["tid"]}'
                cq['state'] = TaskState.IN_PROCESS.value
                callback = Cquery(cq, inline['state'])
                gen2 = callback.generatecq()
                tasks_keyboard.row(InlineKeyboardButton(submit_massage, callback_data=gen1),
                            InlineKeyboardButton(reject_message, callback_data=gen2))
            else:
                tasks_keyboard.row(InlineKeyboardButton(submit_massage, callback_data=gen1))
        elif is_awaiting_start:
            take_message = f'🏋Приступить к задаче'
            cq['state'] = TaskState.IN_PROCESS.value
            callback = Cquery(cq, inline['state'])
            tasks_keyboard.row(InlineKeyboardButton(take_message, callback_data=callback.generatecq()))

    def tasklist_inline(self, uid, tid=0, offset=1, owner_uid=0, order=SortType.CREATION.value):
        cq = {'offset': offset, 'owneruid': owner_uid, 'tid': tid, 'order': order}
        tasks_keyboard = InlineKeyboardMarkup()
        tasks_size = Task().table_size(SortType(order), uid=owner_uid)
        tasks_keyboard = self.create_form_tasks_keyboard(tasks_keyboard, cq)
        back, forward, count = self.get_form_menu_buttons(tasks_size, cq)
        tasks_keyboard.row(back, count, forward)
        if tid:
            self.create_submit_button(uid, cq, tasks_keyboard)
        return tasks_keyboard
