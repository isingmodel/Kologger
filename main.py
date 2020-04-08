import qt_text_ui as ui
import keyboard_recorder as kr
import mouse_recorder as mr
from pynput import keyboard
from multiprocessing import Process
import time
from sys import exit as sysExit


def make_listener_run(listener):
    listener.join()


if __name__ == "__main__":
    listener = kr.start_keyboard_logging("nothing")
    p = Process(target=make_listener_run, args=(listener,))
    p.start()
    ui.execute_ui('nothing')
    listener.join()
