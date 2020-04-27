import hgtk
import pandas as pd
from copy import deepcopy
from pathlib import Path
import pickle as pkl
import numpy as np
DOUBLE_JUNG_LIST = list('ㅘㅙㅚㅝㅞㅟㅢ')
DOUBLE_JUNG_DICT = {'ㅘ': ['ㅗ', 'ㅏ'], 'ㅙ': ['ㅗ', 'ㅐ'], 'ㅚ': ['ㅗ', 'ㅣ'], 'ㅝ': ['ㅜ', 'ㅓ'], 'ㅞ': ['ㅜ', 'ㅔ'],
                    'ㅟ': ['ㅜ', 'ㅣ'], 'ㅢ': ['ㅡ', 'ㅣ']}
DOUBLE_JONG_LIST = list('ㄳㄵㄶㄺㄻㄼㄽㄾㄿㅀㅄ')
DOUBLE_JONG_DICT = {'ㄳ': ['ㄱ', 'ㅅ'], 'ㄵ': ['ㄴ', 'ㅈ'], 'ㄶ': ['ㄴ', 'ㅎ'], 'ㄺ': ['ㄹ', 'ㄱ'],
                    'ㄻ': ['ㄹ', 'ㅁ'], 'ㄼ': ['ㄹ', 'ㅂ'], 'ㄽ': ['ㄹ', 'ㅅ'], 'ㄾ': ['ㄹ', 'ㅌ'],
                    'ㄿ': ['ㄹ', 'ㅍ'], 'ㅀ': ['ㄹ', 'ㅎ'], 'ㅄ': ['ㅂ', 'ㅅ']}

kor = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎㅛㅕㅑㅐㅒㅔㅖㅗㅓㅏㅣㅠㅜㅡ")
eng = list("rRseEfaqQtTdwWczxvgyuioOpPhjklbnm")
eng_alphabet = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
kor_to_eng_dict = dict()
for i in range(len(eng)):
    kor_to_eng_dict[kor[i]] = eng[i]

kor_to_eng_dict['?'] = "?"
kor_to_eng_dict['!'] = "!"
kor_to_eng_dict['@'] = "@"
kor_to_eng_dict['#'] = "#"
kor_to_eng_dict['$'] = "$"
kor_to_eng_dict['%'] = "%"
kor_to_eng_dict['^'] = "^"
kor_to_eng_dict['&'] = "&"
kor_to_eng_dict['*'] = "*"
kor_to_eng_dict['('] = "("
kor_to_eng_dict[')'] = ")"
kor_to_eng_dict['.'] = "."
kor_to_eng_dict[','] = ","
kor_to_eng_dict['~'] = "~"
kor_to_eng_dict[':'] = ":"
kor_to_eng_dict['/'] = "/"


kor_to_eng_dict['\x08'] = 'Key.backspace'
kor_to_eng_dict['\r'] = 'Key.enter'
kor_to_eng_dict[' '] = 'Key.space'


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
        if ui_data[i][1] == '':
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


def refine_all_data(ui_d, key_d):

    ui_d_refined = refine_ui_data(ui_d)
    key_d_refined = refine_data_kbd(key_d)

    ts = [click[4] for click in ui_d_refined]
    ts_eng = [click[3] for click in key_d_refined]
    Engkey = [click[1] for click in key_d_refined]
    ui_d_refined_2 = [list(click) for click in ui_d_refined]
    key_d_refined_2 = [list(click) for click in key_d_refined]
    for click in ui_d_refined_2:
        click.append(0)
    for click in key_d_refined_2:
        click.append(0)
    Korkey = [click[1] for click in ui_d_refined_2]


    for i in range(len(Korkey)):
        if Korkey[i] not in eng:
            target_key = kor_to_eng_dict[Korkey[i]]
        else: 
            target_key = Korkey[i]
        candidate = np.searchsorted(ts_eng, ts[i], side='right')
        
        for key_idx in range(max(candidate-5, 0), candidate):
            if target_key == Engkey[key_idx] and key_d_refined_2[key_idx][4] == 0:
                ui_d_refined_2[i][4] = ts_eng[key_idx]
                key_d_refined_2[key_idx][4] = 1
                ui_d_refined_2[i][6] = 1
                break

    ts_refined = np.array([i[4] for i in ui_d_refined_2])
    temp = ts_refined.argsort()
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(len(ts_refined))

    ui_d_refined_3 = list()
    for rank in ranks:
        ui_d_refined_3.append(ui_d_refined_2[rank][:6])

    for i in range(len(ui_d_refined_3)):
        if ui_d_refined_3[i][1] == '\r':
            ui_d_refined_3[i][1] = 'Enter_Key'


    return ui_d_refined_3
        
                

if __name__ == "__main__":
    ui_p = "./_temp_sj/ui_data.pkl"
    key_p = "./_temp_sj/keyboard_recording.pkl"

    with open(ui_p, 'rb') as f:
        ui_d = pkl.load(f)
    with open(key_p, 'rb') as f:
        key_d = pkl.load(f)
    refined_data = refine_all_data(ui_d, key_d)
    ui_df = list_to_pandas('ui', refined_data)
    ui_df.to_csv(Path("./ui_data_sj.csv"))


