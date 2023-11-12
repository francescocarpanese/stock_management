from abc import ABC, abstractmethod
from enum import Enum
import time
import PySimpleGUI as sg


class Status(Enum):
    INITIALIZED = 1
    RUNNING = 2
    FINISHED = 3


class Session:
    def __init__(self, layout_fun, win_name):
        self.status = Status.INITIALIZED
        self.layout = layout_fun()
        self.window = sg.Window(win_name, self.layout)
        self.window.finalize()
        self.tstat = time.time()

    def run(
        self,
        timeout=None,
        test_events=[],
        test_args=[],
    ):
        self.status = Status.RUNNING

        while True:
            event, values = self.window.read(timeout=100)

            # Perform event actions
            self.act_on_event(event, values)

            # Running externally triggered events for test purposes
            for ev, arg in zip(test_events, test_args):
                ev(self.window, event, values, arg)

            if timeout:
                if time.time() - self.tstat > timeout:
                    self.status = Status.FINISHED

            # Break the loop when end is triggered
            if self.status == Status.FINISHED:
                break

        # Close the window and end status
        self.end()

    @abstractmethod
    def act_on_event(event, values):
        pass

    def end(self):
        self.status = Status.FINISHED
        self.window.close()

    def __del__(self):
        self.end()
