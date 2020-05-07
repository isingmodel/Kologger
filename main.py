import pickle as pkl
import time
from multiprocessing import Process
from multiprocessing import Queue
from pathlib import Path
from queue import Empty

import keyboard_recorder as kr
import qt_text_ui as ui
import refine_data as rd

# TODO: use log!

def get_data_from_queue(d_q):
    pynput_data = list()
    pyqt_data = list()
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
        except Empty:
            pass
        finally:
            time.sleep(0.001)
    print("temp record saving!")
    d_q.put((3, None))
    with open(Path("./temp_data/keyboard_recording.pkl"), 'wb') as f_pynput:
        pkl.dump(pynput_data, f_pynput)
    with open(Path("./temp_data/ui_data.pkl"), 'wb') as f_ui:
        pkl.dump(pyqt_data, f_ui)

    print("start converting")
    # kdb, ui = rd.refine_data(pynput_data, pyqt_data)

    # r_ui_data = rd.refine_ui_data(pyqt_data)
    refined_data = rd.refine_all_data(pyqt_data, pynput_data)

    ui_df = rd.list_to_pandas('ui', refined_data)
    ui_df.to_csv(Path("./ui_data.csv"))
    d_q.put((4, None))


if __name__ == "__main__":
    data_queue = Queue(maxsize=200)
    p_save = Process(target=get_data_from_queue, args=(data_queue,))
    p_keyboard = kr.GetKeyboardData(data_queue)
    p_save.daemon = True
    p_keyboard.daemon = True
    p_save.start()
    p_keyboard.start()
    ui.execute_ui(data_queue, p_save, p_keyboard)
