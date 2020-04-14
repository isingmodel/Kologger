import pickle as pkl
import time
from multiprocessing import Process
from multiprocessing import Queue
from queue import Empty

import keyboard_recorder as kr
import qt_text_ui as ui
import hgtk
from copy import deepcopy
import pandas as pd

DOUBLE_JUNG_LIST = list('ㅘㅙㅚㅝㅞㅟㅢ')
DOUBLE_JUNG_DICT = {'ㅘ':['ㅗ','ㅏ'],'ㅙ':['ㅗ','ㅐ'],'ㅚ':['ㅗ','ㅣ'],'ㅝ':['ㅜ','ㅓ'],'ㅞ':['ㅜ','ㅔ'],'ㅟ':['ㅜ','ㅣ'],'ㅢ':['ㅡ','ㅣ']}
DOUBLE_JONG_LIST = list('ㄳㄵㄶㄺㄻㄼㄽㄾㄿㅀㅄ')
DOUBLE_JONG_DICT = {'ㄳ': ['ㄱ', 'ㅅ'], 'ㄵ': ['ㄴ', 'ㅈ'], 'ㄶ': ['ㄴ', 'ㅎ'], 'ㄺ': ['ㄹ', 'ㄱ'],
                    'ㄻ': ['ㄹ', 'ㅁ'], 'ㄼ': ['ㄹ', 'ㅂ'], 'ㄽ': ['ㄹ', 'ㅅ'], 'ㄾ': ['ㄹ', 'ㅌ'],
                    'ㄿ': ['ㄹ', 'ㅍ'], 'ㅀ': ['ㄹ', 'ㅎ'], 'ㅄ': ['ㅂ', 'ㅅ']}


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
    print("temp recording!")
    with open("./temp_data/keyboard_recording.pkl", 'wb') as f_pynput:
        pkl.dump(pynput_data, f_pynput)
    with open("./temp_data/ui_data.pkl", 'wb') as f_ui:
        pkl.dump(pyqt_data, f_ui)

    print("start converting")
    # with open("./temp_data/ui_data.pkl", 'rb') as f:
    #     ui_data = pkl.load(f)
    # with open("./temp_data/keyboard_recording.pkl", 'rb') as f:
    #     kbd_data = pkl.load(f)
    kdb, ui = refine_data(pynput_data, pyqt_data)
    final_ui_data = refine_ime_data(ui)
    ui_df = list_to_pandas('ui', final_ui_data)
    ui_df.to_csv("./ui_data.csv")


def split(letter):
    decomposed = hgtk.letter.decompose(letter)
    filtered = list()
    for alphabet in decomposed:
        if alphabet != '':
            filtered.append(alphabet)
    return filtered


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


def refine_ime_data(ui_data_refined):
    ui_data_kor_split = list()
    ui_data_copy = deepcopy(ui_data_refined)

    for i in range(len(ui_data_refined)):
        if ui_data_refined[i][2] == "":
            after = split(ui_data_refined[i][1])

            if after[-1] in DOUBLE_JONG_LIST:
                ui_data_copy[i] = list(ui_data_copy[i])
                ui_data_copy[i][1] = DOUBLE_JONG_DICT[after[-1]][-1]
            elif after[-1] in DOUBLE_JUNG_LIST:
                ui_data_copy[i] = list(ui_data_copy[i])
                ui_data_copy[i][1] = DOUBLE_JUNG_DICT[after[-1]][-1]
            else:
                ui_data_copy[i] = list(ui_data_copy[i])
                ui_data_copy[i][1] = after[-1]
        if ui_data_refined[i][2] == "":
            text = ui_data_refined[i][3]
            cursor = ui_data_refined[i][5]

            text_to_list = list(text)
            text_to_list.insert(cursor, ui_data_refined[i][1])
            text = ''.join(text_to_list)
            ui_data_copy[i] = list(ui_data_copy[i])
            ui_data_copy[i][3] = text

        ui_data_kor_split.append(ui_data_copy[i])
    return ui_data_kor_split


def list_to_pandas(d_type, d_list):
    df = pd.DataFrame(d_list, columns=["is_UI",
                                       'KH_output',
                                       'key_val_pyqt',
                                       'Fullstring',
                                       'KH_StartTime',
                                       "KH_position"])
    return df


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
