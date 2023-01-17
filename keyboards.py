from aiogram.types.reply_keyboard import ReplyKeyboardMarkup
from aiogram.types.inline_keyboard import InlineKeyboardMarkup
from aiogram.types.inline_keyboard import  InlineKeyboardButton
import commands
import logging


def create_usrname_kboard(usernames, mark_admins = False):
    kboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in usernames:
        if mark_admins and commands.is_admin(commands.get_id_from_usrname(name)):
            kboard.row(name+' (админ)')
        else:
            kboard.row(name)
    kboard.row('Назад')
    return kboard

def form_permission_choice(is_admin):
    UsrEdit = ReplyKeyboardMarkup(resize_keyboard=True)
    if is_admin:
        choice = ReplyKeyboardButton('Снять админа', callback_data='Снять админа')
        back = ReplyKeyboardButton('Назад', callback_data='Назад')
    else:
        choice = ReplyKeyboardButton('Сделать админом', callback_data='Сделать админом')
        back = ReplyKeyboardButton('Назад', callback_data='Назад')
    UsrEdit.row(choice, back)
    return UsrEdit


def form_task_row(task):
    status = commands.get_status(task['deadline'], task['done'])[0]
    s = f"{status}[M{task['task_id']}] {task['header'] }"
    return InlineKeyboardButton(s, callback_data = f"task_btn_show_{task['task_id']}")


def form_shifting_menu(limit, offset, tasks_size, user):
    back = forward = count = 0
    if offset>1:
        back = InlineKeyboardButton('<', callback_data = f'task_btn_shift_back_{offset}')
    else:
        back = InlineKeyboardButton('_', callback_data = f'btn_empty')
    if tasks_size - (offset*limit) > 0:
        forward = InlineKeyboardButton('>', callback_data = f'task_btn_shift_forward_{offset}')
    else:
        forward = InlineKeyboardButton('_', callback_data = 'btn_empty')
    if user:
        count = InlineKeyboardButton(f'{offset} ({user})', callback_data = 'task_btn_offset')
    else:
        count = InlineKeyboardButton(f'{offset}', callback_data = 'task_btn_offset')
    return back, forward, count



def form_tasks_keyboard(offset=1, user = '', check_done=0):
    limit = 10
    if user!='' and user!='common':
        tasks = commands.list_headers(limit=limit, offset=offset-1, uid = user, sort='deadline')
    else:
        tasks = commands.list_headers(limit=limit, offset=offset-1, uid = user)
    tasks_size = commands.get_table_size('tasks', user)
    TasksKb = InlineKeyboardMarkup()
    if user!='' and user!='общее':
        for task in reversed(tasks):
            TasksKb.row(form_task_row(task))
    else:
        for task in tasks:
            TasksKb.row(form_task_row(task))
    back, forward,  count = form_shifting_menu(limit, offset, tasks_size, user)
    TasksKb.row(back, count, forward)
    if int(check_done)>0 and not commands.is_done(check_done):
        check_btn = InlineKeyboardButton(f'Отметить M{check_done} выполненным',
                                            callback_data=f'btn_checkout_{check_done}')
        TasksKb.row(check_btn)
    return TasksKb



#Reply keyboard for general user
Uk = ReplyKeyboardMarkup(resize_keyboard=True)
Uk.row('Мои задачи', 'Все задачи')
Uk.row('Чужие задачи', 'Общие задачи')

#Reply keyboard for admin
Mk = ReplyKeyboardMarkup(resize_keyboard=True)
Mk.row('Мои задачи', 'Все задачи', 'Общие задачи')
Mk.row('Чужие задачи', 'Создать задачу', 'Ещё')

Ak = ReplyKeyboardMarkup(resize_keyboard=True)
Ak.row('Редактировать права')
Ak.row('Удалить задачу')
Ak.row('Назад')

MBack = ReplyKeyboardMarkup(resize_keyboard=True)
MBack.row('Назад')

#Creating Inline keyboard for adding task command
AddTasksKb = InlineKeyboardMarkup(resize_keyboard=True)
btn1 = InlineKeyboardButton('Название', callback_data='add_task_header')
btn2 = InlineKeyboardButton('Описание', callback_data='add_task_body')
btn3 = InlineKeyboardButton('Исполнители', callback_data='add_task_assignees')
btn4 = InlineKeyboardButton('Дедлайн', callback_data='add_task_deadline')
btn5 = InlineKeyboardButton('Назад', callback_data='add_task_back')
btn6 = InlineKeyboardButton('Сохранить', callback_data='add_task_save')
AddTasksKb.row(btn1, btn2)
AddTasksKb.row(btn3, btn4)
AddTasksKb.row(btn5, btn6)



user_keyboard = {'main': Uk, 'back': MBack}
admin_keyboard = {'main': Mk, 'more': Ak, 'back': MBack}

