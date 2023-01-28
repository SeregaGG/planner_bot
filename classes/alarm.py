import asyncio
import logging
from datetime import datetime, timedelta
from constants.enums import SortType, TaskState as TS
from classes.db import Db as db
from classes.task import Task
from classes.notifier import Notifier
from init import bot, alarm_dict


class Alarm:
    def __init__(self, uid, tasks=[]):
        self.uid = uid
        self.db = db()
        self.value = Notifier(uid)
        self.value.load()
        self.val_dict = self.get_val_dict(self.value)
        self.val_list = [1, 2, 7]
        if tasks:
            self.tasks = tasks
        else:
            self.tasks = self.get_tasks()


    def get_tasks(self):
        return self.db.sorted_headers(self.uid, 0, 0, SortType.DEADLINE)


    async def alarm(self, time, timedelta, task):
        t = time-timedelta
        s = f'ℹ<b>Задача #[{task["task_id"]}]</b>: '
        sec = t.days*24*3600 + t.seconds
        if timedelta.days == 1:
            s += 'До дедлайна 1 день'
        if timedelta.days == 2:
            s += f'До дедлайна 2 дня'
        if timedelta.days == 7:
            s += f'До дедлайна 7 дней'
        await asyncio.sleep(sec)
        await bot.send_message(self.uid, s)


    def create_task_alarm(self, task):
        loop = asyncio.get_event_loop()
        coro_time = {}
        if task['state'] == TS.DONE:
            return {}
        if task['deadline']:
            tid = task['task_id']
            deadline = datetime.fromtimestamp(task['deadline'])
            delta = deadline - datetime.now()
            for days in self.val_dict.keys():
                border = timedelta(days=days)
                if delta > border and self.val_dict[days]:
                    coro_time[days] = loop.create_task(self.alarm(delta, border, task))
            return coro_time
        

    def set_alarms(self):
        task_coro_dict = {}
        if not self.tasks:
            return {}
        for task in self.tasks:
            if task['state'] != TS.DONE.value and task['deadline'] > datetime.now().timestamp():
                task_coro_dict[task['task_id']] = self.create_task_alarm(task)
        return task_coro_dict


    def get_val_dict(self, fy):
        return {1: fy.day, 2: fy.day2, 7: fy.week}

    
    def reset_alarms(self, alarm_dict, fy):
        loop = asyncio.get_event_loop()
        if self.uid not in alarm_dict.keys():
            return
        tasks = alarm_dict[self.uid]
        for task in tasks.keys():
            task_header = {}
            t = None
            for days in self.val_dict.keys():
                if not self.val_dict[days] and (days in tasks[task]):
                    tasks[task][days].cancel()
                    tasks[task].pop(days)
                elif self.val_dict[days] and not (days in tasks[task]):
                    if not task_header:
                        t = Task(task)
                        t.load_from_db()
                        task_header = t.get_header()
                    deadline = task_header['deadline']
                    delta = deadline - datetime.now()
                    border = timedelta(days=days)
                    if delta > border and self.val_dict[days]:
                        tasks[task][days]= loop.create_task(self.alarm(delta, border, t))



    def delete_alarms(self, task):
        for uid in task.ass_uids:
            if uid not in alarm_dict.keys():
                continue
            for val in self.val_dict:
                alarm_dict[uid][task.attr.task_id][val].cancel()
                alarm_dict[uid][task.attr.task_id].pop(val)
            alarm_dict[uid].pop(task.attr.task_id)

                        
