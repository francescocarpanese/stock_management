from stock_management.layouts import get_test_layout
import PySimpleGUI as sg
import time


def test_session(
    test_events=[],
    test_args=[],
    timeout=None,
):
    layout = get_test_layout()
    window = sg.Window("Test", layout)
    window.finalize()

    tstat = time.time()
    while True:
        event, values = window.read(timeout=100)
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
            if time.time() - tstat > timeout:
                break

        # Running automatic events for test purposes
        for ev, arg in zip(test_events, test_args):
            ev(window, event, values, arg)

    window.close()
