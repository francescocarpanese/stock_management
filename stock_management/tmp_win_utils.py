from stock_management.layouts import get_test_layout
from stock_management.__init__ import Session, Status
import PySimpleGUI as sg
import time

class TestSession(Session):
    
    def __init__(self):
        self.status = Status.INITIALIZING

        self.layout = get_test_layout()
        self.window = sg.Window("Test", self.layout)
        self.window.finalize()

        self.tstat = time.time()

    def Run(self, test_events, test_args, timeout):
        self.status = Status.RUNNING

        while True:
            event, values = self.window.read(timeout=100)
            if event == sg.WIN_CLOSED:
                break
            elif event == "-but_exit_test-":
                print("exit win Test")
                break
            elif event == "-but_confirm_test-":
                # values contains the values in the different widgets of the windows. It is not the returned value of a read event.
                # See how values is used to retrive the input value inside the text box
                print(f"text in input text {values['-input_test_tmp_win-']}")
                break
            if timeout:
                if time.time() - self.tstat > timeout:
                    break

            self.RunTests(test_events, test_args)

    def __del__(self):
        self.status = Status.FINISHED
        self.window.close()

def test_session(
    test_events=[],
    test_args=[],
    timeout=None,
):
    testSession = TestSession()
    testSession.Run(test_events, test_args, timeout)
    del testSession
