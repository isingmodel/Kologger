import datetime
import json
import logging
import os
import pickle as pkl
import platform
import time
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import freeze_support
from pathlib import Path
from queue import Empty

import src.keyboard_recorder as kr
import src.mouse_recorder as mr
import src.qt_text_ui as ui

logging.getLogger(__name__).addHandler(logging.NullHandler())
current_path = Path(os.path.dirname(os.path.abspath(__file__)))
config_path = current_path / "config.json"
with open(config_path, 'r') as f_config:
    config = json.load(f_config)

if config["get_window_name"]:
    if platform.system() != "Windows":
        logger = logging.getLogger()
        logger.error("getting current windows name only works on Windows")
        raise NotImplementedError
    else:
        # TODO: update requirements.txt & os-specific install
        import win32gui


# TODO: use log!
def get_data_from_queue(d_q, temp_queue):
    pynput_data = list()
    pyqt_data = list()
    mouse_data = list()
    window_name_data = list()
    subject_name = None
    count = 0
    while True:
        try:
            data = d_q.get(block=False)
            if data[0] == 0:
                pynput_data.append(data)
            elif data[0] == 1:
                pyqt_data.append(data)
            elif data[0] == 2:
                temp_queue.put("exit")
                print("got exit message")
                break
            elif data[0] == 3:
                subject_name = data[1]
            elif data[0] == 4:
                mouse_data.append(data[1:])
            elif data[0] == 5:
                window_name_data.append(data[1:])
            count += 1
        except Empty:
            pass
        finally:
            time.sleep(0.0005)
    print("temp record saving!")
    d_q.put((3, None))
    now = datetime.datetime.now()
    curr_path = Path(os.path.dirname(os.path.abspath(__file__)))
    save_dir = curr_path / subject_name
    try:
        # TODO: save in separate folders
        os.makedirs(save_dir)
    except FileExistsError:
        pass

    time_now = "{}_{}_{}_{}_{}".format(now.year, now.month, now.day, now.hour, now.minute)
    with open(save_dir / f"{subject_name}_pynput_{time_now}.pkl", 'wb') as f_pynput:
        pkl.dump(pynput_data, f_pynput)
    with open(save_dir / f"{subject_name}_pyqt_{time_now}.pkl", 'wb') as f_ui:
        pkl.dump(pyqt_data, f_ui)
    with open(save_dir / f"{subject_name}_mouse_{time_now}.pkl", 'wb') as f_mouse:
        pkl.dump(mouse_data, f_mouse)
    with open(save_dir / f"{subject_name}_windows_name_{time_now}.pkl", 'wb') as f_windows:
        pkl.dump(window_name_data, f_windows)

    d_q.put(("Kill", None))


def get_current_window_name(d_q: Queue):
    while True:
        pycwnd = win32gui.GetForegroundWindow()
        d_q.put([5, time.time(), win32gui.GetWindowText(pycwnd)])
        time.sleep(0.15)


if __name__ == "__main__":
    freeze_support()

    data_queue = Queue(maxsize=1000)
    temp_queue = Queue(maxsize=5000)
    p_save = Process(target=get_data_from_queue, args=(data_queue, temp_queue))
    p_keyboard = kr.GetKeyboardData(data_queue)
    p_save.daemon = True
    p_keyboard.daemon = True
    p_save.start()
    p_keyboard.start()

    if config["get_mouse_data"]:
        p_mouse = mr.GetMouseData(data_queue)
        p_mouse.daemon = True
        p_mouse.start()
    if config["get_window_name"]:
        p_window_name = Process(target=get_current_window_name, args=(data_queue,))
        p_window_name.daemon = True
        p_window_name.start()

    ui.execute_ui(data_queue)
