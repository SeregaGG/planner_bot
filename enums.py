from enum import Enum

TIMEFORMAT = "%d.%m.%Y"

class TaskState(Enum):
    AWAITING_START = 0
    IN_PROCESS = 1
    AWAITING_SUBMIT = 2
    DONE = 3


class SortType(Enum):
    DEADLINE = 0
    CREATION = 1
    DONE_FIRST = 2
    DONE_LAST = 3
    COMMON = 4
    SETTER = 5
