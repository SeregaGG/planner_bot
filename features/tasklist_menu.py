from init import bot, dp, Kb, Form
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified, ChatNotFound
from aiogram import types
from constants.keys import cmdkey, inline
from constants.enums import SortType, TaskState as TS
from classes.cquery import Cquery
from classes.user import User
from classes.task import Task
from classes.alarm import Alarm
from custom_filters.chat_type import IsPrivateChat
import logging


async def show_task(tid):
    task = Task(tid)
    task.load_from_db()
    return task.show()


async def notify_users(task: Task, newstate):
    msg = f'<b>Задача #[{task.attr.task_id}]</b>: "{task.attr.header}":\n\n'\
            f'Статус изменен:'
    if newstate == TS.IN_PROCESS and task.attr.state == TS.AWAITING_START:
        info = 'в работе'
    if newstate == TS.IN_PROCESS and task.attr.state == TS.AWAITING_SUBMIT:
        info = 'возвращено на доработку'
    elif newstate == TS.AWAITING_SUBMIT:
        info = 'ожидает вашего подтверждения'
    elif newstate == TS.DONE:
        info = 'задача принята'

    msg = f'{msg} <b>{info}</b>'

    if (newstate == TS.IN_PROCESS and task.attr.state == TS.AWAITING_SUBMIT) or newstate==TS.DONE:
        for ass in task.ass_uids:
            try:
                await bot.send_message(ass, msg)
            except ChatNotFound:
                pass
    else:
        await bot.send_message(task.attr.creator, msg)
        

@dp.callback_query_handler(Text(startswith=inline['state']), state=Form.newtask)
@dp.callback_query_handler(Text(startswith=inline['state']), state=Form.admin)
@dp.callback_query_handler(Text(startswith=inline['state']), state=Form.default)
async def accept_task(callback: types.CallbackQuery):
    cquery = Cquery()
    cq = cquery.decodecq(callback.data)
    uid = callback.from_user.id
    mid = callback.message.message_id
    task = Task(cq['tid'])
    task.load_from_db()
    newstate = TS(cq['state'])
    await notify_users(task, newstate)
    if newstate == TS.DONE:
        alarm = Alarm(uid)
        alarm.delete_alarms(task)
    task.attr.state = newstate
    task.set_task_state(newstate)
    text = task.show()
    key = Kb.tasklist_inline(uid, cq['tid'], cq['offset'], cq['owneruid'], cq['order'])
    await bot.edit_message_text(text, uid, mid, reply_markup = key)


@dp.callback_query_handler(Text(startswith=inline['shift']), state=Form.newtask)
@dp.callback_query_handler(Text(startswith=inline['shift']), state=Form.default)
@dp.callback_query_handler(Text(startswith=inline['shift']), state=Form.admin)
async def show_task_shift(callback: types.CallbackQuery):
    cquery = Cquery()
    cq = cquery.decodecq(callback.data)
    uid = callback.from_user.id
    mid = callback.message.message_id
    offset = cq['offset'] + cq['dir']
    key = Kb.tasklist_inline(uid, cq['tid'], offset, cq['owneruid'], cq['order'])
    try:
        await bot.edit_message_reply_markup(uid, mid, reply_markup = key)
    except MessageNotModified:
        pass


@dp.callback_query_handler(Text(startswith=inline['show']), state=Form.newtask)
@dp.callback_query_handler(Text(startswith=inline['show']), state=Form.default)
@dp.callback_query_handler(Text(startswith=inline['show']), state=Form.admin)
async def task_button_show(callback: types.CallbackQuery):
    cquery = Cquery()
    cq = cquery.decodecq(callback.data)
    uid = callback.from_user.id
    mid = callback.message.message_id
    if cq['tid'] == cq['btntid']:
        key = Kb.tasklist_inline(uid, 0, cq['offset'],cq['owneruid'], cq['order'])
    else:
        key = Kb.tasklist_inline(uid, cq['btntid'], cq['offset'],cq['owneruid'], cq['order'])
    task = await show_task(cq['btntid'])
    if cq['tid'] == cq['btntid']:
        cq['tid'] = 0
        if cq['owneruid']:
            stats = User().show_stats(cq['owneruid'], cq['order'])
        else:
            stats = User().show_stats()
        await bot.edit_message_text(stats, uid, mid, reply_markup = key)
    else:
        await bot.edit_message_text(task, uid, mid, reply_markup = key)

@dp.message_handler(IsPrivateChat(), Text(equals=cmdkey['all']), state=Form.default)
async def print_all_tasks(message: types.Message):
    key = Kb.tasklist_inline(message.from_user.id)
    stats = User().show_stats()
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer(stats, reply_markup=key)


@dp.callback_query_handler(Text(startswith=inline['mytask']), state=Form.default)
async def print_my_tasks(callback: types.CallbackQuery):
    uid = callback.from_user.id
    mid = callback.message.message_id
    cquery = Cquery()
    cq = cquery.decodecq(callback.data)
    key = Kb.tasklist_inline(uid, owner_uid=uid, order=cq['order'])
    stats = User().show_stats(uid, SortType(cq['order']))
    await bot.delete_message(uid, mid)
    await bot.send_message(uid, stats, reply_markup=key)


@dp.message_handler(IsPrivateChat(), Text(equals=cmdkey['my']), state=Form.default)
async def print_my_tasks(message: types.Message):
    uid = message.from_user.id
    username = message.from_user.username
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer(f'{cmdkey["my"][0]}Выбери тип задач', reply_markup=Kb.my_tasks)


@dp.message_handler(IsPrivateChat(), Text(equals=cmdkey['common']), state=Form.default)
async def print_common_tasks(message: types.Message):
    s = "Общие задачи:\n<pre>                                &#x200D</pre>"
    key = Kb.tasklist_inline(message.from_user.id, order=SortType.COMMON.value)
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer('Общие задачи:', reply_markup=key)


@dp.callback_query_handler(Text(startswith=inline['other']), state=Form.default)
async def others_tasks(callback: types.CallbackQuery):
    uid = callback.from_user.id
    mid = callback.message.message_id
    cquery = Cquery()
    cq = cquery.decodecq(callback.data)
    key = Kb.tasklist_inline(uid, owner_uid = cq['userid'], order = SortType.DEADLINE.value)
    stats = User().show_stats(cq['userid'])
    await bot.edit_message_text(stats, uid, mid, reply_markup=key)


@dp.message_handler(IsPrivateChat(), Text(equals=cmdkey['others']), state=Form.default)
async def others_tasks_button(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message_id)
    key = Kb.assignees_inline(inline['other'])
    await message.answer(f"{cmdkey['others'][0]}Выберите пользователя", reply_markup=key)
