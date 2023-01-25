from init import bot, dp, Kb, Form
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified
from aiogram import types
from constants.keys import cmdkey, inline
from constants.enums import SortType, TaskState as TS
from classes.cquery import Cquery
from classes.user import User
from classes.task import Task


async def show_task(tid):
    task = Task(tid)
    task.load_from_db()
    return task.show()


@dp.callback_query_handler(Text(startswith=inline['state']), state=Form.newtask)
@dp.callback_query_handler(Text(startswith=inline['state']), state=Form.admin)
@dp.callback_query_handler(Text(startswith=inline['state']), state=Form.default)
async def accept_task(callback: types.CallbackQuery):
    cquery = Cquery()
    cq = cquery.decodecq(callback.data)
    uid = callback.from_user.id
    mid = callback.message.message_id
    Task().set_task_state(cq['tid'], TS(cq['state']))
    text = await show_task(cq['tid'])
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
    key = Kb.tasklist_inline(uid, cq['btntid'], cq['offset'],cq['owneruid'], cq['order'])
    task = await show_task(cq['btntid'])
    try:
        await bot.edit_message_text(task, uid, mid, reply_markup = key)
    except MessageNotModified:
        if cq['owneruid']:
            stats = User().show_stats(cq['owneruid'])
        else:
            stats = User().show_stats()
        await bot.edit_message_text(stats, uid, mid, reply_markup = key)


@dp.message_handler(Text(equals=cmdkey['all'], ignore_case=True), state=Form.default)
async def print_all_tasks(message: types.Message):
    await Form.default.set()
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
    stats = User().show_stats(uid)
    await bot.delete_message(uid, mid)
    await bot.send_message(uid, stats, reply_markup=key)


@dp.message_handler(Text(equals=cmdkey['my'], ignore_case=True), state=Form.default)
async def print_my_tasks(message: types.Message):
    uid = message.from_user.id
    username = message.from_user.username
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer('Выбери тип задач', reply_markup=Kb.my_tasks)


@dp.message_handler(Text(equals=cmdkey['common'], ignore_case=True), state=Form.default)
async def print_common_tasks(message: types.Message):
    s = "Общие задачи:\n<pre>                                &#x200D</pre>"
    await Form.default.set()
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


@dp.message_handler(Text(equals=cmdkey['others'], ignore_case=True), state=Form.default)
async def others_tasks_button(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message_id)
    key = Kb.assignees_inline(inline['other'])
    await message.answer(f"{cmdkey['others'][0]}Выберите пользователя", reply_markup=key)
