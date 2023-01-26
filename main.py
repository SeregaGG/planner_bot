from aiogram import executor, types
from classes.user import User
from classes.task import Task
from constants.keys import cmdkey, inline
from init import *
from features import settings, newtask, tasklist_menu
import logging

async def setup_bot_commands():
    bot_commands = [
        types.BotCommand(command="/start", description="Start Bot"),
        types.BotCommand(command="/help", description="Get info about me"),
    ]
    await bot.set_my_commands(bot_commands)


@dp.message_handler(state = '*', commands=['start'])
async def send_welcome(message: types.Message):
    await Form.default.set()
    await setup_bot_commands()
    new_user = User(message=message)
    new_user.to_database()
    s = f"Привет, {new_user.attr.first_name}&#128075!"\
            f"\n\n&#128311 Я - <b>НБ-Помощник</b>.\n"\
            f"&#128311 Я буду хранить список твоих партийных задач.\n"\
            f"&#128311 Слава всем нам! "
    await message.answer(s, reply_markup=Kb.main(new_user))


if __name__ == '__main__':
    #loop = asyncio.get_event_loop()
    #loop.create_task(alarm())
    executor.start_polling(dp, skip_updates=True)
