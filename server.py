import logging
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import ChatNotFound, MessageNotModified
from aiogram.dispatcher.filters import Text
from middlewares import AccessMiddleware
import keyboards
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
import stickers as stickers
import commands
import emoji
import re
import datetime


class Form(StatesGroup):
    default = State()
    add_task = State()
    admin = State()
    rem_task = State()
    others_tasks = State()
    usr_list_perm = State()
    usr_choose_perm = State()
    add_task_header = State()
    add_task_body = State()
    add_task_assignees = State()
    add_task_deadline = State()


API_TOKEN="1115198779:AAHPsbIAg3UBSb4A-ZsulryV1LQdi3Ck2Hc"
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
dp.middleware.setup(AccessMiddleware(commands.get_ids()))
new_task_dict = {} 

async def get_keyboard(uid):
    if (commands.is_admin(uid)):
        return keyboards.admin_keyboard
    else:
        return keyboards.user_keyboard

async def get_info_from_inline(callback):
    info = callback.message.reply_markup.inline_keyboard
    for elem in info:
        if len(elem)==3:
            return elem[1]['text'].split(' ')
    return []


async def get_current_task_number(callback):
    info = callback.message.reply_markup.inline_keyboard
    if len(info[-1]) == 1:
        return int(info[-1][0]['callback_data'].replace('btn_checkout_', ''))
    return 0


async def send_long(text, message, new_markup=""):
    if text and len(text) > 4096:
        for x in range(0, len(text), 4096):
            await message.answer(text[x:x+4096],disable_web_page_preview=True,reply_markup=new_markup)
    else:
        await message.answer(text, disable_web_page_preview=True, reply_markup=new_markup )


async def print_editing_task():
    s = f"<b>Название</b>:\n {new_task_dict['header']}\n"\
        f"<b>Описание</b>:\n {new_task_dict['body']}\n"\
        f"<b>Ответственные</b>:\n {', '.join(new_task_dict['assignees'])}\n"\
        f"<b>Дедлайн</b>: {new_task_dict['deadline']}"
    return s


@dp.message_handler(state = '*', commands=['start'])
async def send_welcome(message: types.Message):
    await Form.default.set()
    user_id = message.from_user.id
    key = await get_keyboard(message.from_user.id)
    logging.warning(f'{user_id}')
    s = f"Привет, {message.from_user.first_name}&#128075!"\
            f"\n\n&#128311 Я - <b>НБ-Помощник</b>.\n"\
            f"&#128311 Я буду хранить список твоих партийных задач.\n"\
            f"&#128311 Слава всем нам! "
    await message.answer(s, reply_markup=key['main'])


@dp.callback_query_handler(Text(startswith='btn_checkout'), state='*')
async def check_done(callback: types.CallbackQuery):
    usr = ''
    chat_id = callback.from_user.id
    message_id = callback.message.message_id
    info = await get_info_from_inline(callback)
    if len(info)>1:
        user = info[1][1:-1]
    offset = int(info[0])
    key = keyboards.form_tasks_keyboard(offset, usr)
    tnum = callback.data.replace('btn_checkout_', '')
    commands.check_done(tnum)
    task = commands.get_task_by_tid(tnum)
    await bot.edit_message_text(task, chat_id, message_id, reply_markup = key)
    


@dp.callback_query_handler(Text(startswith='task_btn_shift'), state='*')
async def show_task_shift(callback: types.CallbackQuery):
    chat_id = callback.from_user.id
    message_id = callback.message.message_id
    usr = ''
    check_tnum = await get_current_task_number(callback)
    info = await get_info_from_inline(callback)
    if len(info)>1:
        user = info[1][1:-1]
    if 'forward' in callback.data:
        query = int(callback.data.replace('task_btn_shift_forward_', ''))
        key = keyboards.form_tasks_keyboard(query+1, usr, check_tnum)
    else:
        query = int(callback.data.replace('task_btn_shift_back_', ''))
        key = keyboards.form_tasks_keyboard(query-1, usr, check_tnum)
    try:
        await bot.edit_message_reply_markup(chat_id, message_id, reply_markup = key)
    except MessageNotModified:
        pass


@dp.callback_query_handler(Text(startswith='task_btn_show'), state='*')
async def show_task(callback: types.CallbackQuery):
    user = ''
    chat_id = callback.from_user.id
    message_id = callback.message.message_id
    info = await get_info_from_inline(callback)
    if len(info)>1:
        user = info[1][1:-1]
    offset = int(info[0])
    query = callback.data.replace('task_btn_show_', '')
    task = commands.get_task_by_tid(query)
    if commands.is_owner(callback.from_user.id, query):
        key = keyboards.form_tasks_keyboard(offset, user, query)
    else:
        key = keyboards.form_tasks_keyboard(offset, user)
    try:
        await bot.edit_message_text(task, chat_id, message_id, reply_markup = key)
    except MessageNotModified:
        pass


@dp.message_handler(Text(equals='Все задачи', ignore_case=True), state='*')
@dp.message_handler(state = '*', commands=['all_tasks'])
async def print_all_tasks(message: types.Message):
    await Form.default.set()
    key = keyboards.form_tasks_keyboard()
    await message.answer('Все задачи:', reply_markup=key)


@dp.message_handler(Text(equals='Мои задачи', ignore_case=True), state='*')
@dp.message_handler(state='*', commands=['my_tasks', 'Мои_задачи'])
async def print_my_tasks(message: types.Message):
    await Form.default.set()
    key = keyboards.form_tasks_keyboard(1, '@'+message.from_user.username)
    await message.answer(f'Задачи @{message.from_user.username}', reply_markup=key)


@dp.message_handler(Text(equals='Общие задачи', ignore_case=True), state='*')
@dp.message_handler(state='*', commands=['common_tasks'])
async def print_common_tasks(message: types.Message):
    await Form.default.set()
    key = keyboards.form_tasks_keyboard(1, 'common')
    await message.answer('Общие задачи:', reply_markup=key)


@dp.message_handler(state = Form.add_task_header)
async def new_task_header(message: types.Message):
    new_task_dict['header'] = message.text
    t = await print_editing_task()
    await message.answer(f'Задача обновлена\n{t}',
                                reply_markup=keyboards.AddTasksKb)


@dp.message_handler(state = Form.add_task_body)
async def new_task_body(message: types.Message):
    new_task_dict['body'] = message.text
    t = await print_editing_task()
    await message.answer(f'Задача обновлена\n{t}',
                                reply_markup=keyboards.AddTasksKb)


@dp.message_handler(state = Form.add_task_deadline)
async def new_task_deadline(message: types.Message):
    new_task_dict['deadline'] = datetime.datetime.strptime(message.text, "%d.%m.%Y").date()
    t = await print_editing_task()
    await message.answer(f'Задача обновлена\n{t}',
                                reply_markup=keyboards.AddTasksKb)


@dp.message_handler(state = Form.add_task_assignees)
async def new_task_assignees(message: types.Message):
    new_task_dict['assignees'] = re.split('\s*,*\s+', message.text) 
    t = await print_editing_task()
    await message.answer(f'Задача обновлена\n{t}',
                                reply_markup=keyboards.AddTasksKb)


@dp.callback_query_handler(Text(startswith='add_task'), state='*')
async def new_task_buttons(callback: types.CallbackQuery):
    chat_id = callback.from_user.id
    mes_id = callback.message.message_id
    query = callback.data.replace('add_task_', '')
    if query == 'header':
        await bot.send_message(chat_id, "Напиши название задачи:")
        await Form.add_task_header.set()
    if query == 'body':
        await bot.send_message(chat_id, "Напиши описание задачи:")
        await Form.add_task_body.set()
    if query == 'assignees':
        await Form.add_task_assignees.set()
        await bot.send_message(chat_id, "Укажи никнеймы исполнителей через пробел:")
    if query == 'deadline':
        await bot.send_message(chat_id, "Укажи дедлайн задачи:")
        await Form.add_task_deadline.set()
    if query == 'back':
        key = await get_keyboard(callback.from_user.id)
        await bot.edit_message_text("Задача отменена", chat_id, mes_id, reply_markup=None)
        await Form.admin.set()
    if query == 'save':
        commands.insert_new_task(new_task_dict, callback.from_user.username)
        key = await get_keyboard(callback.from_user.id)
        await Form.admin.set()
        await bot.send_message(chat_id,"Задача сохранена.", reply_markup=key['main'])


@dp.message_handler(Text(equals='Создать задачу', ignore_case=True), state=Form.default)
async def new_task(message: types.Message):
    global new_task_dict
    new_task_dict= {
        'header': '',
        'body': '',
        'assignees': [],
        'deadline': '',
        'creator': '',
        'created_datetime': ''
    }
    await message.answer('Создать задачу:', reply_markup=keyboards.AddTasksKb)


@dp.message_handler(Text(equals='Ещё', ignore_case=True), state=Form.default)
async def advanced_markup(message: types.Message):
    await Form.admin.set()
    key = await get_keyboard(message.from_user.id)
    if commands.is_admin(message.from_user.id):
        await message.answer("Админ", reply_markup=key['more'])


@dp.message_handler(Text(equals='Назад', ignore_case=True), state=Form.admin)
async def back_to_default_markup(message: types.Message):
    await Form.default.set()
    key = await get_keyboard(message.from_user.id)
    await message.answer("Назад", reply_markup=key['main'])


@dp.message_handler(state=Form.others_tasks)
async def others_tasks(message: types.Message):
    if message.text not in commands.list_usernames():
        if message.text == 'Назад':
            key = await get_keyboard(message.from_user.id)
            await Form.default.set()
            await message.answer('Назад', reply_markup=key['main'])
        else:
            await message.answer('Ошибка: выбери имя из предложенного списка')
    else:
        key = keyboards.form_tasks_keyboard(1, '@'+message.text)
        await message.answer(f'Задачи @{message.text}', reply_markup=key)



@dp.message_handler(Text(equals='Чужие задачи', ignore_case=True), state=Form.default)
async def others_tasks_button(message: types.Message):
    usernames = commands.list_usernames()
    kboard = keyboards.create_usrname_kboard(usernames)
    await Form.others_tasks.set()
    await message.answer("Выберите пользователя", reply_markup=kboard)


@dp.message_handler(state=Form.usr_list_perm)
async def change_admins(message: types.Message):
    mes = message.text.split(' ')
    usernames = commands.list_usernames()
    if(mes[0] in usernames):
        if len(mes) == 2:
            commands.make_admin(mes[0], 0)
            kboard = keyboards.create_usrname_kboard(usernames, mark_admins=True)
            await message.answer(f'{mes[0]} удален из админов', reply_markup=kboard)
        else:
            commands.make_admin(mes[0], 1)
            kboard = keyboards.create_usrname_kboard(usernames, mark_admins=True)
            await message.answer(f'{mes[0]} теперь админ', reply_markup=kboard)

    elif (message.text == 'Назад'):
        key = await get_keyboard(message.from_user.id)
        if commands.is_admin(message.from_user.id):
            await Form.admin.set()
            await message.answer("Назад", reply_markup=key['more'])
        else:
            await Form.default.set()
            await message.answer("Назад", reply_markup=key['main'])



@dp.message_handler(state=Form.rem_task)
async def delete_task(message: types.Message):
    pattern = re.compile('^[0-9]*$')
    if (message.text == 'Назад'):
        await Form.admin.set()
        await message.answer("Назад", reply_markup = keyboards.Ak)
    elif (pattern.match(message.text)):
        commands.delete_task(message.text)
        await Form.admin.set()
        await message.answer('Задача удалена')
    else:
        await message.answer("Неверный ввод. Укажите номер задачи числом. Пример: 12")

@dp.message_handler(Text(equals='Удалить задачу', ignore_case=True), state=Form.admin)
async def delete_task_button(message: types.Message):
    await Form.rem_task.set()
    await message.answer("Напишите номер задачи:", reply_markup=keyboards.MBack)



@dp.message_handler(Text(equals='Редактировать права', ignore_case=True), state=Form.admin)
async def edit_permissions_ulist(message:types.Message):
    usernames = commands.list_usernames()
    kboard = keyboards.create_usrname_kboard(usernames, mark_admins=True)
    await Form.usr_list_perm.set()
    await message.answer('Нажмите на кнопку, чтобы изменить права пользователя', reply_markup=kboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
