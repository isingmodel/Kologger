import datetime
import os
import pickle as pkl
import platform
import sys
import time
from multiprocessing import Process
from multiprocessing import Queue
from pathlib import Path
from queue import Empty

import win32gui

import keyboard_recorder as kr
import mouse_recorder as mr
import qt_text_ui as ui
import refine_data as rd
from refine_data_mouse import mouse_list_to_pandas


# TODO: use log!
def get_data_from_queue(d_q):
    pynput_data = list()
    pyqt_data = list()
    mouse_data = list()
    window_name_data = list()
    subject_name = None
    while True:
        try:
            data = d_q.get(block=False)
            # if data[0] == (0 or 3):
            if data[0] == 0:
                pynput_data.append(data)
            elif data[0] == 1:
                pyqt_data.append(data)
            elif data[0] == 2:
                print("got exit message")
                break
            elif data[0] == 3:
                subject_name = data[1]
            elif data[0] == 4:
                mouse_data.append(data[1:])
            elif data[0] == 5:
                window_name_data.append(data[1:])

        except Empty:
            pass
        finally:
            time.sleep(0.001)
    print("temp record saving!")
    d_q.put((3, None))
    now = datetime.datetime.now()
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    time_now = "{}_{}_{}_{}_{}".format(now.year, now.month, now.day, now.hour, now.minute)
    with open(current_path / f"temp_data/{subject_name}_pynput_{time_now}.pkl", 'wb') as f_pynput:
        pkl.dump(pynput_data, f_pynput)
    with open(current_path / f"temp_data/{subject_name}_pyqt_{time_now}.pkl", 'wb') as f_ui:
        pkl.dump(pyqt_data, f_ui)
    with open(current_path / f"temp_data/{subject_name}_mouse_{time_now}.pkl", 'wb') as f_mouse:
        pkl.dump(mouse_data, f_mouse)
    with open(current_path / f"temp_data/{subject_name}_windows_name_{time_now}.pkl", 'wb') as f_windows:
        pkl.dump(window_name_data, f_windows)

    print("mouse start converting")
    mouse_df = mouse_list_to_pandas(mouse_data)
    mouse_df.to_csv(current_path / f"mouse_{subject_name}_{time_now}.csv")
    print("mouse converting Done")
    print("keyboard start converting")
    refined_data = rd.refine_all_data(pyqt_data, pynput_data)
    ui_df = rd.list_to_pandas('ui', refined_data)
    ui_df.to_csv(current_path / f"keyboard_{subject_name}_{time_now}.csv")
    print("keyboard converting done")
    d_q.put(("Kill", None))


def get_current_window_name(d_q: Queue):
    while True:
        pycwnd = win32gui.GetForegroundWindow()
        d_q.put([5, time.time(), win32gui.GetWindowText(pycwnd)])
        time.sleep(0.15)


if __name__ == "__main__":
    if platform.system() != "Windows":
        print("This program runs only on Windows!!")
        sys.exit(0)
    data_queue = Queue(maxsize=400)
    p_save = Process(target=get_data_from_queue, args=(data_queue,))
    p_keyboard = kr.GetKeyboardData(data_queue)
    p_mouse = mr.GetMouseData(data_queue)
    p_window_name = Process(target=get_current_window_name, args=(data_queue,))
    p_save.daemon = True
    p_keyboard.daemon = True
    p_mouse.daemon = True
    p_window_name.daemon = True
    p_save.start()
    p_keyboard.start()
    p_mouse.start()
    p_window_name.start()
    ui.execute_ui(data_queue, p_save, p_keyboard)
