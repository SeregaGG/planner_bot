import logging
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import ChatNotFound
from aiogram.dispatcher.filters import Text
from middlewares import AccessMiddleware
import keyboards
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
import stickers as stickers
import commands
import emoji
import re


class Form(StatesGroup):
    default = State()
    new_task = State()
    admin = State()
    rem_task = State()
    others_tasks = State()
    usr_list_perm = State()
    usr_choose_perm = State()


API_TOKEN="5815160368:AAH5dyj4l1Ha-XLTutUjTsCaO-9-uEzdyvg"
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
dp.middleware.setup(AccessMiddleware(commands.get_ids()))
logging.info(f"allowed users: {str(commands.get_ids())}")

async def get_keyboard(uid):
    if (commands.is_admin(uid)):
        return keyboards.admin_keyboard
    else:
        return keyboards.user_keyboard


async def send_long(text, message, new_markup=""):
    if text and len(text) > 4096:
        for x in range(0, len(text), 4096):
            await message.answer(text[x:x+4096],disable_web_page_preview=True,reply_markup=new_markup)
    else:
        await message.answer(text, disable_web_page_preview=True, reply_markup=new_markup )


@dp.message_handler(state = '*', commands=['help'])
async def print_help(message: types.Message):
    helpmes = '<u><b>Вот, что я умею</b></u>:\n\n'\
        '&#128311 Хранить список наших задач\n'\
        '&#128311 Отмечать задачи, как выполненные\n'\
        '&#128311 Уведомлять о новых задачах\n\n'\
        '<u><b>Список комманд:</b></u>\n\n'\
        '&#128311 <b>Мои задачи</b> - вывести список задач,'\
        ' которые относятся только ко мне\n'\
        '&#128311 <b>Все задачи</b> - вывести список всех задач\n'\
        '&#128311 <b>Общие задачи</b> - вывести задачи, которые относятся ко всем\n'\
        '&#128311 <b>Чужие задачи</b> - посмотреть задачи отдельного человека\n'\
        '&#128311 <b>N+</b> - отметить задачу с номером N как сделанную\n'\
        '<b>Внимание: нумерация как в списке "Мои задачи"\n\n</b>'

    adminmes = '<u><b>Функции админа</b></u>\n\n&#128311 <b>Ещё</b> - вывести меню админа\n'\
            '&#128311 <b>Создать задачи</b> - добавить новые задачи. Каждая задача должна'\
            'начинаться с новой строки (на компьютере - ctrl+Enter)\n'\
            '&#128311 <b>Снять задачи</b> - убрать старые задачи из выдачи. убранные задачи'\
            'останутся в базе данных, но не будут видны в боте\n'\
            'Чтобы убрать все задачи - отправь "*"\n'\
            '&#128311 <b>Редактировать права</b> - добавить или убрать админов'
    await bot.send_sticker(chat_id = message.from_user.id, sticker = stickers.help_sticker)

    if (commands.is_admin(message.from_user.id)):
        await message.answer(helpmes+adminmes)
    else:
        await message.answer(helpmes)


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

@dp.message_handler(Text(equals='Все задачи', ignore_case=True), state='*')
@dp.message_handler(state = '*', commands=['all_tasks'])
async def print_all_tasks(message: types.Message):
    await Form.default.set()
    key = await get_keyboard(message.from_user.id)
    ans = commands.list_tasks()
    if ans:
        await send_long(ans, message, new_markup=key['main'])
    else:
        await bot.send_sticker(chat_id=message.from_user.id, sticker=stickers.all_tasks_empty)
        await send_long('Список задач пуст.', message, new_markup=key['main'])


@dp.message_handler(Text(equals='Мои задачи', ignore_case=True), state='*')
@dp.message_handler(state='*', commands=['my_tasks', 'Мои_задачи'])
async def print_my_tasks(message: types.Message):
    await Form.default.set()
    user_id = message.from_user.id
    key = await get_keyboard(user_id)
    mes = commands.list_tasks(user_id)
    if mes:
        await bot.send_sticker(chat_id = message.from_user.id,\
                sticker=stickers.my_tasks_sticker)
        await send_long(mes, message, new_markup = key['main'])
    else:
        await bot.send_sticker(chat_id = message.from_user.id,\
                sticker=stickers.my_tasks_sticker_empty)
        await send_long('Список задач пуст', message,  new_markup = key['main'])


@dp.message_handler(Text(equals='Общие задачи', ignore_case=True), state='*')
@dp.message_handler(state='*', commands=['common_tasks'])
async def print_common_tasks(message: types.Message):
    await Form.default.set()
    user_id = message.from_user.id
    key = await get_keyboard(user_id)
    mes = commands.list_common_tasks()
    if mes:
        await send_long(mes, message, new_markup = key['main'])
    else:
        bot.send_sticker(user_id = message.from_usr.id,\
                sticker=stickers.all_tasks_empty)
        await send_long('Список задач пуст.', message, new_markup=key['main'])


@dp.message_handler(state=Form.new_task)
async def new_task(message: types.Message):
    key = await get_keyboard(message.from_user.id)
    if message.text != 'Назад':
        length = commands.add_task(message.text)
        await message.answer(f"Создано {length} задач", reply_markup=key['more'])
    await Form.admin.set()


@dp.message_handler(Text(equals='Создать задачи', ignore_case=True), state=Form.admin)
async def new_task_button(message: types.Message):
    await Form.new_task.set()
    key = await get_keyboard(message.from_user.id)
    await bot.send_sticker(chat_id=message.from_user.id,\
            sticker=stickers.create_tasks_sticker)
    await message.answer(f"Напиши задачу или несолько задач.\n\
            Каждая задача начинается с новой строки")

@dp.message_handler(Text(equals='Ещё', ignore_case=True), state=Form.default)
async def advanced_markup(message: types.Message):
    await Form.admin.set()
    key = await get_keyboard(message.from_user.id)
    if commands.is_admin(message.from_user.id):
        await message.answer("Админ", reply_markup=key['more'])


@dp.message_handler(Text(equals='Снять задачи', ignore_case=True), state=Form.admin)
async def remove_tasks_button(message: types.Message):
    if commands.is_admin(message.from_user.id):
        key = await get_keyboard(message.from_user.id)
        s = "Напиши мне номера задач, которые нужно снять. Каждый номер с новой строки\n"\
                "Если нужно снять все задачи, отправь символ *"
        await Form.rem_task.set()
        await send_long(commands.list_tasks(), message)
        await message.answer(s, reply_markup=key['back'])


@dp.message_handler(state=Form.rem_task)
async def remove_task(message: types.Message):
    key = await get_keyboard(message.from_user.id)
    pattern = re.compile('\d\d*')
    if message.text == "Назад":
        await message.answer("Админ", reply_markup = key['more'])
        await Form.admin.set()
    elif pattern.match(message.text) or message.text == '*':
        if message.text == '*':
            res = commands.remove_all()
        else:
            res = commands.remove_task(message.from_user.id, message.text)
        if res:
            await message.answer("Готово", reply_markup = key['more'])
        elif res == -1:
            await message.answer("Что-то пошло не так", reply_markup = key['more'])
        await Form.admin.set()
    else:
        await message.answer("Неправильный ввод")


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
        usrname = commands.get_id_from_usrname(message.text)
        mes = commands.list_tasks(usrname)
        if mes:
            await send_long(mes, message)
        else:
            await message.answer('Список задач пуст.')



@dp.message_handler(Text(equals='Чужие задачи', ignore_case=True), state=Form.default)
async def others_tasks_button(message: types.Message):
    usernames = commands.list_usernames()
    kboard = keyboards.create_usrname_kboard(usernames)
    await Form.others_tasks.set()
    await message.answer("Выберите пользователя", reply_markup=kboard)


@dp.message_handler(state=Form.usr_list_perm)
async def change_admins(message: types.Message):
    mes = message.text.split(' ')
    logging.info(mes)
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
        logging.info(key)
        if commands.is_admin(message.from_user.id):
            await Form.admin.set()
            await message.answer("Назад", reply_markup=key['more'])
        else:
            await Form.default.set()
            await message.answer("Назад", reply_markup=key['main'])



@dp.message_handler(Text(equals='Редактировать права', ignore_case=True), state=Form.admin)
async def edit_permissions_ulist(message:types.Message):
    usernames = commands.list_usernames()
    kboard = keyboards.create_usrname_kboard(usernames, mark_admins=True)
    await Form.usr_list_perm.set()
    await message.answer('Нажмите на кнопку, чтобы изменить права пользователя', reply_markup=kboard)


async def notify_admins(message, tid):
    mes = f'@{message.from_user.username} ВЫПОЛНИЛ ЗАДАНИЕ:\n'\
            f'<i>"{commands.get_task(tid)}"</i>'
    admins = commands.list_admins()
    logging.info(admins)
    for admin in admins:
        try:
            await bot.send_message(chat_id=admin, text=mes)
        except ChatNotFound:
            logging.error(f'Admin {admin} cannot be reached')


@dp.message_handler(state=Form.default)
async def check_task(message: types.Message):
    pattern = re.compile('\d\d*\s*\+')
    key = await get_keyboard(message.from_user.id)
    if(pattern.match(message.text)):
        num = message.text.replace('+', '').replace(' ', '')
        tid = commands.check_done(message.from_user.id, num)
        if (tid):
            mes = f"ЗАДАЧА №{num} ВЫПОЛНЕНА.\nПартия гордится тобой!"
            await notify_admins(message, tid)
            await bot.send_sticker(chat_id=message.from_user.id,\
                    sticker = stickers.check_done_success)
            await message.answer(mes,reply_markup=key['main'] )
        else:
            await bot.send_sticker(chat_id=message.from_user.id,\
                    sticker = stickers.check_done_fail)
            await message.answer(f"У тебя нет задачи №{num}, либо ты её уже выполнил",\
                    reply_markup=key['main'])



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
