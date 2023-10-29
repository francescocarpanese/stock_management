import stock_management.tmp_win_utils as tmp_win_utils
import time
import sys


# This test check that if the "confirm" button is triggered, the message "exit win Test" is printed on the terminal
def test_click_confirm_button(capsys):
    tmp_win_utils.test_session(
        test_events=[
            event_cancel,
        ],
        test_args=[
            [],
        ],
        timeout=1,
    )

    captured = capsys.readouterr()
    last_line = captured.out.strip().split("\n")[-1]
    assert last_line == "exit win Test"


# Test that if  "pippo" is written and  "ok" is clicked, the program write "you pressed pippo" in the terminal
def test_click_confirm_button(capsys):
    # Test to write on the Input widget
    entry_txt = "pippo"

    # Create window, trigger the event fill_and_ok, write pippo and click ok. See the event "fill_and_ok" utility
    tmp_win_utils.test_session(
        test_events=[
            fill_and_ok,
        ],
        test_args=[
            entry_txt,
        ],
        timeout=1,
    )

    # Get the stdout, and check that the program wrote the expected message in the print
    captured = capsys.readouterr()
    last_line = captured.out.strip().split("\n")[-1]
    assert last_line == f"text in input text {entry_txt}"


def event_cancel(window, event, values, args=[]):
    print("Event Ok")
    time.sleep(0.5)
    window.write_event_value("-but_exit_test-", True)


def fill_and_ok(window, event, values, args=[]):
    # Update the value in the Input box with the argument
    window["-input_test_tmp_win-"].update(value=args)
    # Trigger the button ok
    window.write_event_value("-but_confirm_test-", True)