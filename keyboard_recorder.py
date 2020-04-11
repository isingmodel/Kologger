from pynput import keyboard
import time
import pickle as pkl
from multiprocessing import Process
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
            self.data_queue.put(('pynput', key_value, time.time()))
            # print(key_value, time.time())
            # key_value_list.append((key_value, ts))
            # key_value_list_press.append((key_value, key_type, ts))

    def on_release(self, key_data):
        ts = time.time()
        key_value_raw = str(key_data)
        if key_value_raw.startswith("'") and key_value_raw.endswith("'"):
            key_value = key_value_raw.strip("'") + '_'
        else:
            key_value = key_value_raw + '_'

        key_value_list.append((key_value, ts))

        if key_data == keyboard.Key.esc:
            with open("./temp_data/keyboard_recording.pkl", "wb") as f:
                pkl.dump(key_value_list, f)
            return False

    def run(self):
        print("keyboard listener start!")
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()
        listener.join()

        return listener

#
# if __name__ == "__main__":
#     p = Process(target=start_keyboard_logging, args=('nothing',))
#     p.start()
#     p.join()
#     time.sleep(0.5)
#     keyboard_button.press("w")
#     keyboard_button.release("w")
#     time.sleep(3)
#     keyboard_button.press(keyboard_key.esc)
#     keyboard_button.release(keyboard_key.esc)
#     # listener, keyboard_log_data = start_keyboard_logging()
