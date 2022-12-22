from aiogram.types.reply_keyboard import ReplyKeyboardMarkup
from aiogram.types.inline_keyboard import InlineKeyboardMarkup
from aiogram.types.inline_keyboard import  InlineKeyboardButton
import commands
import logging


def create_usrname_kboard(usernames, mark_admins = False):
    kboard = ReplyKeyboardMarkup()
    for name in usernames:
        if mark_admins and commands.is_admin(commands.get_id_from_usrname(name)):
            kboard.row(name+' (админ)')
        else:
            kboard.row(name)
    kboard.row('Назад')
    return kboard

def form_permission_choice(is_admin):
    UsrEdit = ReplyKeyboardMarkup()
    if is_admin:
        choice = ReplyKeyboardButton('Снять админа', callback_data='Снять админа')
        back = ReplyKeyboardButton('Назад', callback_data='Назад')
    else:
        choice = ReplyKeyboardButton('Сделать админом', callback_data='Сделать админом')
        back = ReplyKeyboardButton('Назад', callback_data='Назад')
    UsrEdit.row(choice, back)
    return UsrEdit


Uk = ReplyKeyboardMarkup()
Uk.row('Мои задачи', 'Все задачи')
Uk.row('Чужие задачи', 'Общие задачи')

Mk = ReplyKeyboardMarkup()
Mk.row('Мои задачи', 'Все задачи', 'Общие задачи')
Mk.row('Чужие задачи', 'Ещё')

Ak = ReplyKeyboardMarkup()
Ak.row('Создать задачи')
Ak.row('Снять задачи')
Ak.row('Редактировать права')
Ak.row('Назад')

MBack = ReplyKeyboardMarkup()
MBack.row('Назад')

user_keyboard = {'main': Uk, 'back': MBack}
admin_keyboard = {'main': Mk, 'more': Ak, 'back': MBack}

