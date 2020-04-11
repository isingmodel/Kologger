import pickle as pkl
import time
from multiprocessing import Process
from multiprocessing import Queue
from queue import Empty

import keyboard_recorder as kr
import qt_text_ui as ui
import pandas as pd


def get_data_from_queue(d_q):
    pynput_data = list()
    pyqt_data = list()
    while True:
        try:
            data = d_q.get(block=False)

            if data[0] == 0:
                pynput_data.append(data)
            elif data[0] == 1:

                pyqt_data.append(data)

            elif data[0] == "exit":
                break
        except Empty:
            pass

        time.sleep(0.001)
    with open("./temp_data/keyboard_recording.pkl", 'wb') as f_pynput:
        pkl.dump(pynput_data, f_pynput)
    with open("./temp_data/ui_data.pkl", 'wb') as f_ui:
        pkl.dump(pyqt_data, f_ui)


def refine_data(kbd_data, ui_data):
    ui_data_refined = list()
    kbd_data_refined = list()
    for i in range(len(ui_data)):
        if ui_data[i][1] == '' and ui_data[i][2] == '':
            continue
        elif ui_data[i][2] == 0:
            continue
        else:
            ui_data_refined.append(ui_data[i])

    for i in range(len(kbd_data)):
        if kbd_data[i][1] != "None":
            kbd_data_refined.append(kbd_data[i])
    return kbd_data_refined, ui_data_refined


def list_to_pandas(d_type, d_list):
    pass


def align_two_timeseries(kbd_data, ui_data):
    pass


if __name__ == "__main__":
    data_queue = Queue(maxsize=200)
    p_save = Process(target=get_data_from_queue, args=(data_queue,))
    p_keyboard = kr.GetKeyboardData(data_queue)
    p_save.daemon = True
    p_keyboard.daemon = True
    p_save.start()
    p_keyboard.start()
    ui.execute_ui(data_queue, p_save, p_keyboard)
