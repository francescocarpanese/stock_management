from stock_management.__init__ import Session, Status
import PySimpleGUI as sg
import time


class TestSession(Session):
    def act_on_event(self, event, values):
        if event == sg.WIN_CLOSED:
            self.status = Status.FINISHED
        elif event == "-but_exit_test-":
            print("exit win Test")
            self.status = Status.FINISHED
        elif event == "-but_confirm_test-":
            # values contains the values in the different widgets of the windows. It is not the returned value of a read event.
            # See how values is used to retrive the input value inside the text box
            print(f"text in input text {values['-input_test_tmp_win-']}")
            self.status = Status.FINISHED
