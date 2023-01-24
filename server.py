import logging
from dataclasses import dataclass
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import MessageNotModified
from aiogram.dispatcher.filters import Text
from middlewares import AccessMiddleware
from keyboards import Keyboard
from aiogram import Bot, Dispatcher, executor, types
import re
from datetime import datetime
import asyncio
from task_queue import NewTaskQueue as TaskQueue
from user import User
from task import Task
from enums import SortType, TIMEFORMAT
from keys import cmdkey
from deluser_queue import DeluserRow


@dataclass
class CalbInfo:
    uid: int = 0
    offset: int = 0
    mes_id: int = 0
    tid: int = 0
    order: str = ''
    username: str = ''
    task: str = ''


class Form(StatesGroup):
    default = State()
    add_task = State()
    admin = State()
    rem_task = State()
    usr_list_perm = State()
    newtask = State()
    add_task_header = State()
    add_task_body = State()
    add_task_assignees = State()
    add_task_deadline = State()
    deluser = State()


API_TOKEN="1115198779:AAHPsbIAg3UBSb4A-ZsulryV1LQdi3Ck2Hc"
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
dp.middleware.setup(AccessMiddleware(User().idlist()))
Tqueue = TaskQueue()
Delqueue = DeluserRow()
Kb = Keyboard(5)


async def show_task(tid):
    task = Task(tid)
    task.load_from_db()
    return task.show()
    

async def get_info_from_inline(callback):
    info = callback.message.reply_markup.inline_keyboard
    button_words = []
    for elem in info:
        if len(elem)==3:
            button_words =  elem[1]['text'].split(' ')
            break
    button_words[0] = button_words[0].split('/')[0]
    return_dict = {'offset': int(button_words[0]), 'username': '', 'order': SortType.CREATION }
    if (len(button_words) > 1):
        if button_words[1][1:-1] == 'общ':
            return_dict['order'] = SortType.COMMON
        else:
            return_dict['username'] = button_words[1][1:-1]
            return_dict['order'] = SortType.DEADLINE
    return return_dict


async def get_callback_info(callback: types.CallbackQuery):
    info = CalbInfo()
    info.uid = callback.from_user.id
    info.mes_id = callback.message.message_id
    dic= await get_info_from_inline(callback)
    info.offset, info.username, info.order = dic['offset'], dic['username'], dic['order']
    info.tid = int(re.sub("[a-zA-Z_]+_", "", callback.data))
    if info.tid:
        info.task = await show_task(info.tid)
    return info


async def get_current_task_number(callback):
    info = callback.message.reply_markup.inline_keyboard
    if len(info[-1]) == 1:
        return int(info[-1][0]['callback_data'].replace('btn_submit', ''))
    return 0


async def send_long(text, message, new_markup=""):
    if text and len(text) > 4096:
        for x in range(0, len(text), 4096):
            await message.answer(text[x:x+4096],disable_web_page_preview=True,reply_markup=new_markup)
    else:
        await message.answer(text, disable_web_page_preview=True, reply_markup=new_markup )


async def print_editing_task(message, task: Task):
    deadline = ''
    assignees = []
    if task.attr.deadline:
        deadline = datetime.fromtimestamp(task.attr.deadline).strftime(TIMEFORMAT)
    if task.assignees:
        for i in range(0, len(task.assignees)):
            assignees.append(f'@{task.assignees[i]}')

    t = f"<b>Название</b>: {task.attr.header}\n\n"\
        f"<b>Описание</b>: {task.attr.body}\n\n"\
        f"<b>Ответственные</b>: {', '.join(assignees)}\n\n"\
        f"<b>Дедлайн</b>: {deadline}"
    t = f'<i>Задача обновлена</i>{t}'
    await Form.newtask.set()
    try:
        await bot.delete_message(message.from_user.id, message.message_id)
        await message.answer(t, reply_markup=Kb.newtask())
    except Exception:
        uid = message.from_user.id
        mid = message.message.message_id
        await bot.edit_message_text(t, uid, mid, reply_markup=Kb.newtask())


@dp.message_handler(state = '*', commands=['start'])
async def send_welcome(message: types.Message):
    await Form.default.set()
    new_user = User(message=message)
    new_user.to_database()
    s = f"Привет, {new_user.attr.first_name}&#128075!"\
            f"\n\n&#128311 Я - <b>НБ-Помощник</b>.\n"\
            f"&#128311 Я буду хранить список твоих партийных задач.\n"\
            f"&#128311 Слава всем нам! "
    await message.answer(s, reply_markup=Kb.main(new_user))


@dp.callback_query_handler(Text(startswith='btn_submit'), state=Form.newtask)
@dp.callback_query_handler(Text(startswith='btn_submit'), state=Form.admin)
@dp.callback_query_handler(Text(startswith='btn_submit'), state=Form.default)
async def submit_task(callback: types.CallbackQuery):
    i = await get_callback_info(callback)
    Task().set_done(i.tid)
    i.task = await show_task(i.tid)
    key = Kb.tasklist_inline(i.uid, i.tid, i.offset, i.username, i.order)
    await bot.edit_message_text(i.task, i.uid, i.mes_id, reply_markup = key)
    

@dp.callback_query_handler(Text(startswith='task_btn_shift'), state=Form.newtask)
@dp.callback_query_handler(Text(startswith='task_btn_shift'), state=Form.default)
@dp.callback_query_handler(Text(startswith='task_btn_shift'), state=Form.admin)
async def show_task_shift(callback: types.CallbackQuery):
    i = await get_callback_info(callback)
    offset = i.offset + (1 if ('forward' in callback.data) else -1)
    key = Kb.tasklist_inline(i.uid, i.tid, offset, i.username, i.order)
    try:
        await bot.edit_message_reply_markup(i.uid, i.mes_id, reply_markup = key)
    except MessageNotModified:
        pass


@dp.callback_query_handler(Text(startswith='task_btn_show'), state=Form.newtask)
@dp.callback_query_handler(Text(startswith='task_btn_show'), state=Form.default)
@dp.callback_query_handler(Text(startswith='task_btn_show'), state=Form.admin)
async def task_button_show(callback: types.CallbackQuery):
    i = await get_callback_info(callback)
    key = Kb.tasklist_inline(i.uid, i.tid, i.offset, i.username, i.order)
    i.task = await show_task(i.tid)
    try:
        await bot.edit_message_text(i.task, i.uid, i.mes_id, reply_markup = key)
    except MessageNotModified:
        if i.username:
            stats = User().show_stats(i.username)
        else:
            stats = User().show_stats()
        await bot.edit_message_text(stats, i.uid, i.mes_id, reply_markup = key)


@dp.message_handler(Text(equals=cmdkey['all'], ignore_case=True), state=Form.default)
async def print_all_tasks(message: types.Message):
    await Form.default.set()
    key = Kb.tasklist_inline(message.from_user.id)
    stats = User().show_stats()
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer(stats, reply_markup=key)


@dp.message_handler(Text(equals=cmdkey['my'], ignore_case=True), state=Form.default)
async def print_my_tasks(message: types.Message):
    await Form.default.set()
    uid = message.from_user.id
    username = message.from_user.username
    key = Kb.tasklist_inline(uid, username=username, order=SortType.DEADLINE)
    stats = User().show_stats(username)
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer(stats, reply_markup=key)


@dp.message_handler(Text(equals=cmdkey['common'], ignore_case=True), state=Form.default)
async def print_common_tasks(message: types.Message):
    s = "Общие задачи:\n<pre>                                &#x200D</pre>"
    await Form.default.set()
    key = Kb.tasklist_inline(message.from_user.id, order=SortType.COMMON)
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer('Общие задачи:', reply_markup=key)


@dp.callback_query_handler(Text(startswith='otherstasks_assignees_'), state=Form.default)
async def others_tasks(callback: types.CallbackQuery):
    uid = callback.from_user.id
    mid = callback.message.message_id
    username = callback.data.replace('otherstasks_assignees_@', '')
    key = Kb.tasklist_inline(uid, username=username, order=SortType.DEADLINE)
    stats = User().show_stats(username)
    await bot.edit_message_text(stats, uid, mid, reply_markup=key)



@dp.message_handler(Text(equals=cmdkey['others'], ignore_case=True), state=Form.default)
async def others_tasks_button(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message_id)
    key = Kb.assignees_inline('otherstasks')
    await message.answer(f"{cmdkey['others'][0]}Выберите пользователя", reply_markup=key)


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


@dp.callback_query_handler(Text(startswith='new_task_assignees_'), state=Form.newtask)
async def new_task_assignees(callback: types.CallbackQuery):
    uid = callback.from_user.id
    mid = callback.message.message_id
    task = Tqueue.getTask(uid)
    user = callback.data.replace('new_task_assignees_@', '')
    if user != 'new_task_assignees_save':
        if user not in task.assignees:
            task.assignees.append(user)
        else:
            task.assignees.remove(user)
        s = f" {', '.join(task.assignees)}".replace(' ', ' @')
        text = 'Выбери ответственных:\n\n' + s
        await bot.edit_message_text(text, uid, mid, reply_markup=Kb.assignees_inline('new_task'))
    else:
        await print_editing_task(callback, task=task)


@dp.callback_query_handler(Text(startswith='add_task'), state='*')
async def new_task_buttons(callback: types.CallbackQuery):
    global Tqueue
    uid = callback.from_user.id
    mid = callback.message.message_id
    query = callback.data.replace('add_task_', '')
    if query == 'header':
        await Form.add_task_header.set()
        await bot.edit_message_text("Укажи название задачи:", uid, mid, reply_markup=None)
    if query == 'body':
        await Form.add_task_body.set()
        await bot.edit_message_text("Укажи описание задачи:", uid, mid, reply_markup=None)
    if query == 'assignees':
        s = 'Выбери ответственных:'
        await bot.edit_message_text(s, uid, mid, reply_markup=Kb.assignees_inline('new_task'))
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


@dp.callback_query_handler(Text(startswith='ch_admins'), state=Form.usr_list_perm)
async def change_admins(callback: types.CallbackQuery):
    info = callback.data.replace('ch_admins_', '').split('_')
    uid = callback.from_user.id
    mid = callback.message.message_id
    if info[0] != 'save':
        User().make_admin(int(info[0]), not int(info[1]))
        await bot.edit_message_reply_markup(uid, mid, reply_markup=Kb.adminlist())
    else:
        await Form.admin.set()
        key = Kb.admin_set_kb
        await bot.edit_message_text(cmdkey['settings'], uid, mid, reply_markup=key)
        

@dp.callback_query_handler(Text(startswith='deluser'), state=Form.deluser)
async def deluser(callback: types.CallbackQuery):
    uid = callback.from_user.id
    mid = callback.message.message_id
    info = callback.data.replace('deluser_assignees_@', '')
    logging.info(Delqueue.row)
    if info != 'deluser_assignees_save':
        dellist = Delqueue.add(uid, info)
        s = f"Вы собираетесь удалить:\n {', '.join(dellist)}".replace(' ', ' @')
        await bot.edit_message_text(s, uid, mid, reply_markup=Kb.assignees_inline('deluser'))
    else:
        User().del_users(Delqueue.pop(uid))
        await Form.admin.set()
        await bot.edit_message_text(cmdkey['settings'], uid, mid, reply_markup=Kb.admin_set_kb)





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
        await bot.edit_message_text(s, uid, mid, reply_markup=Kb.assignees_inline('deluser'))
    elif query == 'back':
        await bot.delete_message(uid, mid)
        await Form.default.set()
    elif query == 'back_rem':
        await Form.admin.set()
        key = Kb.admin_set_kb
        await bot.edit_message_text(cmdkey['settings'], uid, mid, reply_markup=key)
            


@dp.message_handler(Text(equals=cmdkey['settings'], ignore_case=True), state=Form.default)
async def advanced_markup(message: types.Message):
    await Form.admin.set()
    await bot.delete_message(message.from_user.id, message.message_id)
    key = Kb.admin_set_kb
    await message.answer(cmdkey['settings'], reply_markup=key)


if __name__ == '__main__':
    #loop = asyncio.get_event_loop()
    #loop.create_task(alarm())
    executor.start_polling(dp, skip_updates=True)
