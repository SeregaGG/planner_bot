from classes.db import Db as database
import logging


class Notify_queue:
    def __init__(self):
        self.dict = {}

    def insert(self, uid, fy):
        self.dict[uid] = fy

    def pop(self, uid):
        return self.dict.pop(uid)

    def get(self, uid):
        return self.dict[uid]


class Notifier:
    def __init__(self, uid = 0, value = 0):
        self.uid = uid
        self.value = value
        self.day = 0
        self.day2 = 0
        self.week = 0
        self.exists = True
        self.db = database()


    def load(self):
        value =  self.db.get_table_column('notify', 'value', {'id': self.uid})
        if not value:
            self.value = 0
            self.exists = False
        else:
            self.value = value[0]
            self.process_value()


    def save(self):
        self.value = self.day + 2*self.day2 + 4*self.week
        if self.exists:
            self.db.update('notify', {'value': self.value}, {'id': self.uid})
        else:
            self.db.insert('notify', {'id': self.uid, 'value': self.value})


    def process_value(self):
        value = self.value
        self.day = value % 2
        self.day2 = (value // 2) % 2
        self.week = (value // 4) % 2
