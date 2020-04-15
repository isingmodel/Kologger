import hgtk
import pandas as pd
from copy import deepcopy
from pathlib import Path
import pickle as pkl

DOUBLE_JUNG_LIST = list('ㅘㅙㅚㅝㅞㅟㅢ')
DOUBLE_JUNG_DICT = {'ㅘ': ['ㅗ', 'ㅏ'], 'ㅙ': ['ㅗ', 'ㅐ'], 'ㅚ': ['ㅗ', 'ㅣ'], 'ㅝ': ['ㅜ', 'ㅓ'], 'ㅞ': ['ㅜ', 'ㅔ'],
                    'ㅟ': ['ㅜ', 'ㅣ'], 'ㅢ': ['ㅡ', 'ㅣ']}
DOUBLE_JONG_LIST = list('ㄳㄵㄶㄺㄻㄼㄽㄾㄿㅀㅄ')
DOUBLE_JONG_DICT = {'ㄳ': ['ㄱ', 'ㅅ'], 'ㄵ': ['ㄴ', 'ㅈ'], 'ㄶ': ['ㄴ', 'ㅎ'], 'ㄺ': ['ㄹ', 'ㄱ'],
                    'ㄻ': ['ㄹ', 'ㅁ'], 'ㄼ': ['ㄹ', 'ㅂ'], 'ㄽ': ['ㄹ', 'ㅅ'], 'ㄾ': ['ㄹ', 'ㅌ'],
                    'ㄿ': ['ㄹ', 'ㅍ'], 'ㅀ': ['ㄹ', 'ㅎ'], 'ㅄ': ['ㅂ', 'ㅅ']}


def split(letter):
    decomposed = hgtk.letter.decompose(letter)
    filtered = list()
    for alphabet in decomposed:
        if alphabet != '':
            filtered.append(alphabet)
    return filtered


def refine_data_kbd(kbd_data):
    kbd_data_refined = list()
    for i in range(len(kbd_data)):
        if kbd_data[i][1] != "None":
            kbd_data_refined.append(kbd_data[i])
    return kbd_data_refined


def refine_ui_data(ui_data):
    ui_data_refined = list()

    for i in range(len(ui_data)):
        if ui_data[i][1] == '' and ui_data[i][2] == '':
            continue
        elif ui_data[i][2] == 0:
            continue
        else:
            ui_data_refined.append(ui_data[i])

    ui_data_kor_split = list()
    ui_data_copy = deepcopy(ui_data_refined)

    for i in range(len(ui_data_refined)):
        if ui_data_refined[i][2] == "":

            if ui_data_refined[i][1] == " ":
                continue
            if len(ui_data_refined[i][1]) > 1:
                continue

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

            # reformat whole text
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
    # with open(Path("./temp_data/keyboard_recording.pkl"), 'rb') as f_pynput:
    #     pynput_data = pkl.load(f_pynput)
    with open(Path("./temp_data/ui_data.pkl"), 'rb') as f_ui:
        pyqt_data = pkl.load(f_ui)
    #
    for i in pyqt_data:
        print(i)
    # print("start converting")
    # kbd_refined = refine_data_kbd(pynput_data)

    final_ui_data = refine_ui_data(pyqt_data)
    ui_df = list_to_pandas('ui', final_ui_data)
    ui_df.to_csv(Path("./ui_data.csv"))
