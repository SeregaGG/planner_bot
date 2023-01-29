from init import bot, dp, Kb, Form, alarm_dict, middlewares
from aiogram import types
from aiogram.dispatcher.filters import Text
from constants.keys import cmdkey, inline
from temp.deluser_queue import DeluserRow
from classes.cquery import Cquery
from classes.user import User
from classes.task import Task
from classes.alarm import Alarm
from classes.notifier import Notifier, Notify_queue
from middlewares import AccessMiddleware
import logging
import re
from custom_filters.chat_type import IsPrivateChat


Delqueue = DeluserRow()
NotiQueue = Notify_queue()


async def get_callback_text(callback):
    rmarkup = callback.message.reply_markup.inline_keyboard
    for row in rmarkup:
        for col in row:
            if col.callback_data == callback.data:
                return col.text


async def get_keyboard(from_user):
    user = User(from_user = from_user)
    if user.is_admin():
        return Kb.admin_settings_kb(1)
    return Kb.admin_settings_kb(0)


@dp.message_handler(state=Form.rem_task)
async def delete_task(message: types.Message):
    pattern = re.compile('^[0-9]*$')
    uid = message.from_user.id
    await bot.delete_message(uid, message.message_id)
    if (pattern.match(message.text)):
        response = Task().delete(int(message.text), uid)
        if response:
            await Form.admin.set()
            key = await get_keyboard(message.from_user)
            await message.answer('Задача удалена', reply_markup=key)
        else:
            s = "Вы не можете удалить эту задачу, поскольку не создавали её,"\
                    " либо такой задачи не существует"
            await message.answer(s)
    else:
        await message.answer("Неверный ввод. Укажите номер задачи числом. Пример: 12")


@dp.callback_query_handler(Text(startswith=inline['chadmin']), state=Form.usr_list_perm)
async def change_admins(callback: types.CallbackQuery):
    uid = callback.from_user.id
    mid = callback.message.message_id
    cquery = Cquery()
    cq = cquery.decodecq(callback.data)
    if cq['userid']:
        User().make_admin(cq['userid'] , not cq['is_admin'])
        await bot.edit_message_reply_markup(uid, mid, reply_markup=Kb.adminlist())
    else:
        await Form.admin.set()
        key = await get_keyboard(callback.from_user)
        await bot.edit_message_text(cmdkey['settings'], uid, mid, reply_markup=key)


@dp.callback_query_handler(Text(startswith=inline['del']), state=Form.deluser)
async def deluser(callback: types.CallbackQuery):
    uid = callback.from_user.id
    mid = callback.message.message_id
    cq = Cquery().decodecq(callback.data)
    user = cq['userid']
    username = await get_callback_text(callback)
    if user:
        dellist = Delqueue.add(uid, username)
        s = f"Вы собираетесь удалить:\n {', '.join(dellist)}"
        key = Kb.assignees_inline(inline['del'], True)
        await bot.edit_message_text(s, uid, mid, reply_markup=key)
    else:
        d = Delqueue.pop(uid)
        User().del_users(d)
        middlewares.access_ids = User().idlist()
        await Form.admin.set()
        s = '<i>*Участник удалён*</i>\n'
        key = await get_keyboard(callback.from_user)
        await bot.edit_message_text(s+cmdkey['settings'], uid, mid, reply_markup=key)


@dp.callback_query_handler(Text(startswith='notifi_'), state=Form.notifi)
async def notification_menu(callback: types.CallbackQuery):
    uid = callback.from_user.id
    mid = callback.message.message_id
    fy = NotiQueue.get(uid)
    query = callback.data.replace('notifi_', '')
    if query == 'week':
        fy.week = not fy.week
    elif query == '1':
        fy.day = not fy.day
    elif query == '2':
        fy.day2 = not fy.day2
    if query != 'back':
        await bot.edit_message_reply_markup(uid, mid, reply_markup=Kb.notification_menu(fy))
    else:
        fy.save()
        a = Alarm(uid)
        a.reset_alarms(alarm_dict,fy)
        NotiQueue.pop(uid)
        await Form.admin.set()
        key = await get_keyboard(callback.from_user)
        await bot.edit_message_text(cmdkey['settings'], uid, mid, reply_markup=key)


@dp.callback_query_handler(Text(startswith='settings'), state=Form.admin)
@dp.callback_query_handler(Text(startswith='settings'), state=Form.rem_task)
@dp.callback_query_handler(Text(startswith='settings'), state=Form.usr_list_perm)
async def handle_settings(callback: types.CallbackQuery):
    query = callback.data.replace("settings_", '')
    uid = callback.from_user.id
    mid = callback.message.message_id
    if query == 'delete':
        s = 'Пришли мне номер задачи, которую надо удалить'
        await Form.rem_task.set()
        await bot.edit_message_text(s, uid, mid, reply_markup=Kb.go_back_kb('settings_back_rem'))

    elif query == 'admins':
        s = 'Нажми на имя, чтобы назначить или снять его с должности админа:\n'\
            '🌚 <i>- стоит рядом с админами</i>'
        await Form.usr_list_perm.set()
        await bot.edit_message_text(s, uid, mid, reply_markup=Kb.adminlist())
    elif query == 'deluser':
        s = f'Выберите пользователей, которых хотите удалить:'
        await Form.deluser.set()
        key = Kb.assignees_inline(inline['del'], True)
        await bot.edit_message_text(s, uid, mid, reply_markup=key)
    elif query == 'notifications':
        s = 'С какой периодичностью уведомлять вас о задачах?'
        fy = Notifier(uid)
        fy.load()
        NotiQueue.insert(uid, fy)
        await Form.notifi.set()
        await bot.edit_message_text(s, uid, mid, reply_markup=Kb.notification_menu(fy))
    elif query == 'back':
        await bot.delete_message(uid, mid)
        await Form.default.set()
    elif query == 'back_rem':
        await Form.admin.set()
        key = await get_keyboard(callback.from_user)
        await bot.edit_message_text(cmdkey['settings'], uid, mid, reply_markup=key)


@dp.message_handler(IsPrivateChat(),Text(equals=cmdkey['settings']), state=Form.default)
async def settings_markup(message: types.Message):
    await Form.admin.set()
    await bot.delete_message(message.from_user.id, message.message_id)
    key = await get_keyboard(message.from_user)
    await message.answer(cmdkey['settings'], reply_markup=key)
