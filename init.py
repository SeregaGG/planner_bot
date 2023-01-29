import logging
from classes.keyboards import Keyboard
from classes.user import User
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher
from middlewares import AccessMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os


class Form(StatesGroup):
    initialize = State()
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
    notifi = State()


API_TOKEN= os.environ['TELEGRAM_API_TOKEN']
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
middlewares = AccessMiddleware(User().idlist())
dp.middleware.setup(middlewares)
Kb = Keyboard(5)
alarm_dict = {}
