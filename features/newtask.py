from init import bot, dp, Kb, Form
from aiogram import types
from constants.keys import cmdkey, inline
from constants.enums import TIMEFORMAT
from temp.task_queue import NewTaskQueue as TaskQueue
from datetime import datetime
from classes.cquery import Cquery
from classes.task import Task
from aiogram.dispatcher.filters import Text


Tqueue = TaskQueue()


async def get_callback_text(callback):
    rmarkup = callback.message.reply_markup.inline_keyboard
    for row in rmarkup:
        for col in row:
            if col.callback_data == callback.data:
                return col.text


async def print_editing_task(message, task: Task):
    deadline = ''
    if task.attr.deadline:
        deadline = datetime.fromtimestamp(task.attr.deadline).strftime(TIMEFORMAT)
    t = f"<b>Название</b>: {task.attr.header}\n\n"\
        f"<b>Описание</b>: {task.attr.body}\n\n"\
        f"<b>Ответственные</b>: {', '.join(task.ass_usernames)}\n\n"\
        f"<b>Дедлайн</b>: {deadline}"
    t = f'<i>Задача обновлена</i>\n{t}'
    await Form.newtask.set()
    try:
        await bot.delete_message(message.from_user.id, message.message_id)
        await message.answer(t, reply_markup=Kb.newtask())
    except Exception:
        uid = message.from_user.id
        mid = message.message.message_id
        await bot.edit_message_text(t, uid, mid, reply_markup=Kb.newtask())


@dp.message_handler(state = Form.add_task_header)
async def new_task_header(message: types.Message):
    task = Tqueue.getTask(message.from_user.id)
    task.attr.header = message.text
    await Form.newtask.set()
    await print_editing_task(message, task)


@dp.message_handler(state = Form.add_task_body)
async def new_task_body(message: types.Message):
    task = Tqueue.getTask(message.from_user.id)
    task.attr.body = message.text
    await print_editing_task(message, task)


@dp.message_handler(state = Form.add_task_deadline)
async def new_task_deadline(message: types.Message):
    s = 'Неправильный ввод.\nДедлайн должен быть в формате [дд.мм.гггг]:\n\n<i>Пример: 22.02.1942</i>'
    task = Tqueue.getTask(message.from_user.id)
    try:
        task.attr.deadline = datetime.strptime(message.text, TIMEFORMAT).timestamp()
    except ValueError:
        await bot.delete_message(message.from_user.id, message.message_id)
        await message.answer(s)
        return
    await print_editing_task(message, task)


@dp.callback_query_handler(Text(startswith=inline['new_task_l']), state=Form.newtask)
async def new_task_assignees(callback: types.CallbackQuery):
    uid = callback.from_user.id
    mid = callback.message.message_id
    task = Tqueue.getTask(uid)
    cquery = Cquery()
    cq = cquery.decodecq(callback.data)
    user = cq['userid']
    username = await get_callback_text(callback)
    if user:
        if username not in task.ass_usernames:
            task.ass_usernames.append(username)
            task.ass_uids.append(user)
        else:
            task.ass_usernames.remove(username)
            task.ass_uids.remove(user)
        s = f" {', '.join(task.ass_usernames)}"
        text = 'Выбери ответственных:\n\n' + s
        key = Kb.assignees_inline(inline['new_task_l'], True)
        await bot.edit_message_text(text,uid,mid,reply_markup=key)
    else:
        await print_editing_task(callback, task=task)


@dp.callback_query_handler(Text(startswith=inline['addtask']), state=Form.newtask)
async def new_task_buttons(callback: types.CallbackQuery):
    global Tqueue
    uid = callback.from_user.id
    mid = callback.message.message_id
    query = callback.data.replace(f'{inline["addtask"]}_', '')
    if query == 'header':
        await Form.add_task_header.set()
        await bot.edit_message_text("Укажи название задачи:", uid, mid, reply_markup=None)
    if query == 'body':
        await Form.add_task_body.set()
        await bot.edit_message_text("Укажи описание задачи:", uid, mid, reply_markup=None)
    if query == 'assignees':
        s = 'Выбери ответственных:'
        key = Kb.assignees_inline(inline['new_task_l'], True)
        await bot.edit_message_text(s, uid, mid, reply_markup=key)
    if query == 'deadline':
        s = 'Укажи дедлайн в формате [дд.мм.ггг]:\n\n<i>Пример: 22.02.1942</i>'
        await bot.edit_message_text(s, uid, mid, reply_markup=None)
        await Form.add_task_deadline.set()
    if query == 'save' or query == 'back':
        s = 'Задача отменена'
        task = Tqueue.getTask(uid)
        if query == 'save':
            task.save_to_db()
            s = 'Задача сохранена'
        Tqueue.delTask(uid)
        await Form.default.set()
        await bot.delete_message(uid, mid)
        await bot.send_message(uid, s, reply_markup=Kb.main(User(uid)))


@dp.message_handler(Text(equals=cmdkey['create'], ignore_case=True), state=Form.default)
async def new_task(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message_id)
    global Tqueue
    task = Tqueue.newTask(message.from_user.id)
    task.attr.creator = message.from_user.id
    await Form.newtask.set()
    await message.answer('Создать задачу:', reply_markup=Kb.newtask())
