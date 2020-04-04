import qt_text_ui as ui
import keyboard_recorder as kr
import mouse_recorder as mr
from pynput import keyboard
from multiprocessing import Process
import time
from sys import exit as sysExit

if __name__ == "__main__":
    p = Process(target=ui.execute_ui, args=('nothing',))
    p.start()
    # time.sleep(0.5)

    kr.start_keyboard_logging("nothing")