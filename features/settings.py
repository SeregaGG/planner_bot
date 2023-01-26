from init import bot, dp, Kb, Form
from aiogram import types
from aiogram.dispatcher.filters import Text
from constants.keys import cmdkey, inline
from temp.deluser_queue import DeluserRow
from classes.cquery import Cquery
from classes.user import User
from classes.task import Task
from middlewares import AccessMiddleware
import logging
import re


Delqueue = DeluserRow()


async def get_callback_text(callback):
    rmarkup = callback.message.reply_markup.inline_keyboard
    for row in rmarkup:
        for col in row:
            if col.callback_data == callback.data:
                return col.text


@dp.message_handler(state=Form.rem_task)
async def delete_task(message: types.Message):
    pattern = re.compile('^[0-9]*$')
    uid = message.from_user.id
    await bot.delete_message(uid, message.message_id)
    if (pattern.match(message.text)):
        response = Task().delete(int(message.text), uid)
        if response:
            await Form.admin.set()
            await message.answer('Задача удалена', reply_markup=Kb.stngs(uid))
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
        key = Kb.admin_set_kb
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
        dp.middleware.setup(AccessMiddleware(User().idlist()))
        await Form.admin.set()
        s = '<i>*Участник удалён*</i>\n'
        await bot.edit_message_text(s+cmdkey['settings'], uid, mid, reply_markup=Kb.admin_set_kb)


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
    elif query == 'back':
        await bot.delete_message(uid, mid)
        await Form.default.set()
    elif query == 'back_rem':
        await Form.admin.set()
        key = Kb.admin_set_kb
        await bot.edit_message_text(cmdkey['settings'], uid, mid, reply_markup=key)


@dp.message_handler(Text(equals=cmdkey['settings'], ignore_case=True), state=Form.default)
async def settings_markup(message: types.Message):
    await Form.admin.set()
    await bot.delete_message(message.from_user.id, message.message_id)
    key = Kb.admin_set_kb
    await message.answer(cmdkey['settings'], reply_markup=key)
