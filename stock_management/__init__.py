from abc import ABC, abstractmethod
from enum import Enum

class Status(Enum):
    INITIALIZING = 1,
    RUNNING = 2,
    FINISHED = 3

class Session:
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def Run(self):
        pass

    @abstractmethod
    def __del__(self):
        pass

    def RunTests(self,
        test_events=[],
        test_args=[]
    ):
        for ev, arg in zip(test_events, test_args):
            ev(window, event, values, arg)