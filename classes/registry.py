from init import bot, dp, Form, middlewares
from middlewares import AccessMiddleware
from classes.db import Db
from classes.user import User
import logging


class Registry:
    def __init__(self, mes = 0):
        self.register_list = []
        self.username_list = []
        self.message = mes
        self.db = Db()


    def add_member(self, user):
        logging.info(self.register_list)
        logging.info(self.username_list)
        if user not in self.register_list:
            self.username_list.append(f'🥷@{user.username}')
            self.register_list.append(user)
            return 1
        return 0


    def show(self):
        return '\n'.join(self.username_list)
            
    async def delete(self):
        await bot.delete_message(self.message.chat.id, self.message.message_id)


    async def get_admins(self, cid):
        admins = await bot.get_chat_administrators(cid)
        admin_list = []
        for admin in admins:
            admin_list.append(admin['user']['id'])
        return admin_list


    async def set_motherchat(self, cid):
        logging.info(f'inserting {cid} into motherchat')
        self.db.insert("motherchat", {'motherid': cid})


    async def register(self, cid):
        admin_list = await self.get_admins(cid)
        for u in self.register_list:
            user = User(from_user=u)
            if user.attr.id in admin_list:
                user.attr.admin = True
            user.attr.blacklist = 0
            logging.info(user.as_dict())
            user.to_database()
        logging.info(User().idlist())
        middlewares.access_ids = User().idlist()
        await Form.default.set()
        motherchat = await self.read_motherchat()
        if not motherchat:
            await self.set_motherchat(cid)

        
    async def read_motherchat(self):
        return self.db.get_table_column('motherchat', 'motherid')
