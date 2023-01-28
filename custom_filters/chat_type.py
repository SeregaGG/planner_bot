from aiogram.dispatcher.filters import Filter
from aiogram import types
import logging

class IsPublicChat(Filter):
    async def check(self, message: types.Message):
        return not(message.from_user.id == message.chat.id)


class IsPrivateChat(Filter):
    async def check(self, message:types.Message):
        return message.from_user.id == message.chat.id
