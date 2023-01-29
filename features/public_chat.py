from init import bot, dp, Form, API_TOKEN, Kb
from classes.registry import Registry
from aiogram.dispatcher.filters import Text
from aiogram import types
from custom_filters.chat_type import IsPublicChat
import logging
from classes.registry import Registry


reg = None


header1 = '<b>Привет, это НБ-помощник!</b>🤖✋\n\n'\
    '👷Пришло время добавить новых ребят? Поехали!\n\n Ничего нового:\n\n'\

header2 = '<b>Привет, это НБ-помощник!</b>🤖✋\n\n'\
    '👷Я создам для вас рабочее пространство. Для этого нужно сделать 2 простых шага:\n\n'\

invite_mes = '🔷1)пусть каждый из чата нажмет на кнопку "Добавить меня";\n'\
    '🔷2)Когда все добавятся, нажмите "Создать рабочее пр-во", и я'\
    ' активирую его. Эту кнопку может нажать только админ чата\n'\
    '🔷3)После этого вы сможете смотреть и создавать задачи в личных сообщениях с ботом\n\n'\
    '✅Зарегистрировались:\n'



async def check_for_admin(cid, uid):
    admins = await bot.get_chat_administrators(cid)
    access = 0
    for admin in admins:
        if uid ==  admin['user']['id']:
            return 1
    return 0


async def report_success(cid, mid):
    botinfo = await bot.get_me()
    botname = botinfo['username']
    s = f'✅Готово! Рабочее пространство созадно для:\n\n'\
        f'{reg.show()}\n\n'\
        f'\n\n✅Теперь каждый может смотреть и создавать задачи в личных сообщениях со мной\n'\
        f'📌 Не забудьте закрепить меня в ветке сообщений, чтобы я не потерялся:)\n'\
        f'👶Чтобы добавить новых участников, вы можете снова написать в'\
        f' этом чате команду /start@{botname}. Сейчас вы можете меня удалить. '\
        f'Когда я понадоблюсь, просто добавьте меня в чат снова\n'\
        f'⚠Обратите внимание, что бот работает только для этого чата.\n'\
        f'Чтобы настроить бот в других чатах, свяжитесь с разработчиками'

    await bot.edit_message_text(s, cid, mid, reply_markup=None)


@dp.callback_query_handler(Text(startswith='register'))
async def register_user(callback: types.CallbackQuery):
    global reg
    cid = callback.message.chat.id
    mid = callback.message.message_id
    query = callback.data.replace('register_', '')
    if query == 'submit':
        success = reg.add_member(callback.from_user)
        if success:
            s = invite_mes + reg.show()
            await bot.edit_message_text(s, cid, mid, reply_markup=Kb.register_kb())
    elif query == 'creat':
        if await check_for_admin(cid, callback.from_user.id):
            await reg.register(cid)
            await report_success(cid, mid)
            reg = None


@dp.message_handler(IsPublicChat(), commands=['start'], state='*')
async def send_welcome(message: types.Message):
    global reg
    motherchat = await Registry().read_motherchat()
    if motherchat and motherchat[0] != message.chat.id:
        await bot.send_message(message.chat.id, 'Вы кто такие? Я вас не знаю!...')
        return
    if not await check_for_admin(message.chat.id, message.from_user.id):
        await message.reply('У вас недостаточно прав для выполнения команды')
        return
    key = Kb.register_kb()
    if motherchat:
        mes = await bot.send_message(message.chat.id, header1+invite_mes,  reply_markup=key)
    else:
        mes = await bot.send_message(message.chat.id, header2+invite_mes,  reply_markup=key)
    if reg != None:
        await reg.delete()
    reg = Registry(mes)


