"""Аутентификация — пропускаем сообщения только от одного Telegram аккаунта"""
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
import logging
from datetime import datetime
from db import Db as db


class AccessMiddleware(BaseMiddleware):
    def __init__(self, access_ids: list):
        self.access_ids = access_ids
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        logging.info(self.access_ids)
        logging.info(message.from_user.id)
        if message.from_user.id not in self.access_ids:
            logging.warning(f"{message.from_user.id} attempted to login")
            mes = message.from_user
            column_values = {
                'id': mes.id,
                'first_name': mes.first_name,
                'last_name': mes.last_name,
                'is_bot': mes.is_bot,
                'username': mes.username,
                'language_code': mes.language_code,
                'time': datetime.now().isoformat()
            }
            db().insert('unauthorized_access', column_values)
            raise CancelHandler()


