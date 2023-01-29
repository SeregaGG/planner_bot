from aiogram import executor
from init import *
from features import settings, newtask, tasklist_menu, public_chat, start
from constants.keys import cmdkey
from custom_filters.chat_type import IsPrivateChat
from aiogram import types


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

