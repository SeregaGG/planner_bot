"""Аутентификация — пропускаем сообщения только от одного Telegram аккаунта"""
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
import logging


class AccessMiddleware(BaseMiddleware):
    def __init__(self, access_ids: list):
        self.access_ids = access_ids
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        if message.from_user.id not in self.access_ids:
            logging.info("Processing a message")
            #logging.warning(f"{message.from_user.id} attempted to login")
            #commands.report_trespasser(message.from_user)
            #raise CancelHandler()


