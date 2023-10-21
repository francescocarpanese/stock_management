from stock_management.layouts import get_test_layout
import PySimpleGUI as sg

def test_session():
    layout = get_test_layout()
    window = sg.Window("Test", layout)
    window.finalize()

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "-but_exit_test-":
            break
        elif event == "-but_confirm_test-":
            print("you pressed", values[0])
        else:
            print("Unexpected event occurred", event, "values", values);

    window.close()