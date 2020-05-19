import time
from multiprocessing import Process

from pynput import keyboard

key_value_list = list()
key_value_list_press = list()
keyboard_button = keyboard.Controller()
keyboard_key = keyboard.Key


class GetKeyboardData(Process):
    def __init__(self, data_queue, parent=None):
        super(Process, self).__init__(parent)
        self.data_queue = data_queue

    def on_press(self, key_data):
        ts = time.time()
        key_value = None
        key_type = None
        try:
            key_value = str(key_data.char)
            key_type = "char"
        except AttributeError:
            key_value = str(key_data)
            key_type = "else"
        finally:
            self.data_queue.put((0, key_value, key_type, time.time(), 'press'))

    def on_release(self, key_data):
        ts = time.time()
        key_value = None
        key_type = None
        try:
            key_value = str(key_data.char)
            key_type = "char"
        except AttributeError:
            key_value = str(key_data)
            key_type = "else"
        finally:
            self.data_queue.put((0, key_value, key_type, time.time(), 'release'))

    def run(self):
        print("keyboard listener start!")
        listener = keyboard.Listener(on_press=self.on_press,
                                     on_release=self.on_release)
        listener.start()
        listener.join()

        return listener
