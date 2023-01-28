from init import Form, alarm_dict, dp, bot, Kb
from constants.keys import cmdkey, inline
from custom_filters.chat_type import IsPrivateChat
from classes.user import User
from classes.alarm import Alarm
from aiogram import types


async def setup_bot_commands():
    bot_commands = [
        types.BotCommand(command="/start", description="Start Bot"),
    ]
    await bot.set_my_commands(bot_commands)


async def send_welcome(message: types.Message):
    updated_user = User(from_user=message.from_user)
    updated_user.to_database()
    s = f"Привет, {updated_user.attr.first_name}&#128075!"\
        f"\n\n&#128311 Я - <b>НБ-Помощник</b>🤖.\n"\
        f"&#128311 Я храню список твоих задач и напоминаю тебе об их выполнении.\n\n"\
        f"Вот что я могу:\n\n"\
        f'[<i>{cmdkey["all"]}</i>] -  показывает все существующие задачи\n\n'\
        f'[<i>{cmdkey["my"]}</i>] -  показывает задачи, которые'\
        ' создали для тебя или ты создал для других.\n\n'\
        f"[<i>{cmdkey['common']}</i>] - здесь можно посмотреть задачи, не"\
        " имеющие конкретных исполнителей\n\n"\
        f"[<i>{cmdkey['create']}</i>] - меню для добавления"\
        " новой задачи в список, с возможностью выбора"\
        f" дедлайна и ответственных за выполнение\n\n"\
        f"[<i>{cmdkey['settings']}</i>] - здесь можно редактировать участников,"\
        f" а также включить персональные уведомления о приближающихся дедлайнах"
    await setup_bot_commands()
    await Form.default.set()
    alarm = Alarm(updated_user.attr.id)
    alarm_dict[updated_user.attr.id] = alarm.set_alarms()
    await message.answer(s, reply_markup=Kb.main)


async def initialization(message: types.Message):
    s = 'Привет, я бот задач!\n'\
        'Я ещё не активирован. '\
        'Добавь меня в чат своей команды. Так я смогу создать для вас '\
        'рабочее пространство за 2 простых шага'
    await message.answer(s)


@dp.message_handler(IsPrivateChat(), state = '*', commands=['start'])
async def start(message: types.Message):
    if not User().idlist():
        await initialization(message)
    else:
        await send_welcome(message)
