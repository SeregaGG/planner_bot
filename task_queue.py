from datetime import datetime
from date_string import DateStr
from task import Task


class NewTaskQueue:

    def __init__(self):
        self.tasks = {}


    def getTask(self, uid):
        return self.tasks[uid]


    def newTask(self, uid):
        task = Task()
        self.tasks[uid] = task
        return task


    def delTask(self, uid):
        del self.tasks[uid]

