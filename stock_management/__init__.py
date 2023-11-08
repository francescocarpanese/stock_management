from abc import ABC, abstractmethod
from enum import Enum

class Status(Enum):
    INITIALIZING = 1,
    RUNNING = 2,
    FINISHED = 3

class SessionType(Enum):
    MAIN = 1,
    TEST = 2

class Session:
    @abstractmethod
    def __init__(self, test_events, test_args, session_type):
        pass

    @abstractmethod
    def Run(self):
        pass

    @abstractmethod
    def __del__(self):
        pass

    def RunTests(self,
        event=None,
        values=None,
    ):
        for ev, arg in zip(self.test_events, self.test_args):
            ev(self.window, event, values, arg)