import copy
import pickle as pkl
from copy import deepcopy
from pathlib import Path

import hgtk
import numpy as np
import pandas as pd

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

special_key_dict = dict()
special_key_dict['\x08'] = 'Key.backspace'
special_key_dict['Key.enter'] = 'Key.enter'
special_key_dict[' '] = 'Key.space'


def split(letter):
    decomposed = hgtk.letter.decompose(letter)
    filtered = list()
    for alphabet in decomposed:
        if alphabet != '':
            filtered.append(alphabet)
    return filtered


def refine_data_kbd_init(kbd_data):
    kbd_data_refined = list()
    # delete useless "None"
    for i in range(len(kbd_data)):
        if kbd_data[i][1] != "None":
            kbd_data_refined.append(kbd_data[i])
    return kbd_data_refined


def refine_ui_data_init(ui_data):
    ui_data_refined = list()
    ui_data_kor_split = list()

    # delete usless ""
    for i in range(len(ui_data)):
        if ui_data[i][1] == '':
            continue
        elif ui_data[i][2] == 0:
            continue
        elif ui_data[i][1] == '\x7f':
            continue
        elif ui_data[i][2] == "" and ui_data[i][1] == " ":
            continue
        elif ui_data[i][2] == "" and len(ui_data[i][1]) > 1:
            continue
        else:
            ui_data_refined.append(list(ui_data[i]))

    ui_data_copy = deepcopy(ui_data_refined)
    splitted_ime_saved_before = list("")
    whole_text_before = ""
    for i in range(len(ui_data_refined)):
        if ui_data_refined[i][2] == "":  # korean input converting
            # return korean input alphabet

            splitted_ime = split(ui_data_refined[i][1])

            # double alphabets
            if splitted_ime[-1] in DOUBLE_JONG_LIST:
                last_alphabet = copy.deepcopy(splitted_ime[-1])
                del splitted_ime[-1]
                splitted_ime += DOUBLE_JONG_DICT[last_alphabet]
            elif splitted_ime[-1] in DOUBLE_JUNG_LIST:
                last_alphabet = copy.deepcopy(splitted_ime[-1])
                del splitted_ime[-1]
                splitted_ime += DOUBLE_JUNG_DICT[last_alphabet]

            if len(splitted_ime_saved_before) >= 2 and \
                    splitted_ime_saved_before[-2] == splitted_ime[-1] and \
                    len(splitted_ime_saved_before) > len(splitted_ime) and \
                    whole_text_before == ui_data_copy[i][3]:
                ui_data_copy[i][1] = "\x08"
            else:
                ui_data_copy[i][1] = splitted_ime[-1]

            splitted_ime_saved_before = copy.deepcopy(splitted_ime)
            whole_text_before = copy.deepcopy(ui_data_copy[i][3])

            #             print(splitted_ime, splitted_ime[-1])

            # reformat whole text with input alphabet
            text = ui_data_refined[i][3]
            cursor = ui_data_refined[i][5]
            text_to_list = list(text)
            current_key = ui_data_refined[i][1]

            text_to_list.insert(cursor, current_key)
            text = ''.join(text_to_list)

            ui_data_copy[i] = list(ui_data_copy[i])
            ui_data_copy[i][3] = text
        if ui_data_copy[i][1] == "\r":
            ui_data_copy[i][1] = "Key.enter"

        ui_data_kor_split.append(ui_data_copy[i])
    return ui_data_kor_split


def list_to_pandas(d_type, d_list):
    df = pd.DataFrame(d_list, columns=["is_UI",
                                       'KH_output',
                                       'key_val_pyqt',
                                       'Fullstring',
                                       'KH_StartTime',
                                       "KH_position",
                                       'KH_ReleaseTime'])
    return df


def match_pynput_press_release(key_d):
    key_data = [list(i) for i in key_d if i[4] == 'press']
    # print(key_d)
    release_data = [list(i) for i in key_d if i[4] == 'release']
    press_data_len = len(key_data)
    for idx, press_key in enumerate(key_data):
        #     print(idx, release_data[idx])
        idx_search = idx - 3
        while True:
            #             print(press_key[1], release_data[idx_search][1], release_data[idx_search][4])
            if press_key[1] == release_data[idx_search][1] and release_data[idx_search][4] == "release":
                key_data[idx][4] = release_data[idx_search][3]
                release_data[idx_search][4] = "done"
                break
            elif press_data_len == idx_search:
                print(press_data_len, idx_search, press_key, idx)
                print("find release key error")
                break

            else:
                idx_search += 1
    # print(key_data)
    return key_data


def refine_all_data(ui_d, key_d):
    ui_d_refined = refine_ui_data_init(ui_d)
    key_d_refined = match_pynput_press_release(refine_data_kbd_init(key_d))

    ts = [click[4] for click in ui_d_refined]
    ts_eng_press = [click[3] for click in key_d_refined]
    ts_eng_release = [click[4] for click in key_d_refined]
    Engkey = [click[1] for click in key_d_refined]
    Korkey = [click[1] for click in ui_d_refined]

    # todo: delete this conversion
    ui_d_refined_2 = ui_d_refined
    key_d_refined_2 = key_d_refined

    # press, release time init
    for click in ui_d_refined_2:
        click += [0., 0.]
    for click in key_d_refined_2:
        click += [0., 0.]

    for kor_idx in range(len(Korkey)):

        if Korkey[kor_idx] == "\x08":
            target_key = special_key_dict[Korkey[kor_idx]]
        elif Korkey[kor_idx] in eng:
            target_key = Korkey[kor_idx]
        elif Korkey[kor_idx] in kor:
            target_key = kor_to_eng_dict[Korkey[kor_idx]]
        elif len(Korkey[kor_idx]) == 1 and Korkey[kor_idx] != " ":
            target_key = Korkey[kor_idx]
        else:
            target_key = special_key_dict[Korkey[kor_idx]]
        #             print(Korkey[kor_idx], target_key)
        #         print(kor_idx, Korkey[kor_idx], "target_key", target_key)
        candidate = np.searchsorted(ts_eng_press, ts[kor_idx], side='right')
        for key_idx in range(max(candidate - 3, 0), candidate):
            if target_key == Engkey[key_idx] and key_d_refined_2[key_idx][5] == 0:
                ui_d_refined_2[kor_idx][4] = ts_eng_press[key_idx]
                ui_d_refined_2[kor_idx][6] = ts_eng_release[key_idx]
                key_d_refined_2[key_idx][5] = 1

                ui_d_refined_2[kor_idx][7] = 1  # need it?
                break

    ts_refined = np.array([i[4] for i in ui_d_refined_2])
    temp = ts_refined.argsort()
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(len(ts_refined))

    ui_d_refined_3 = list()
    for rank in ranks:
        ui_d_refined_3.append(ui_d_refined_2[rank][:7])

    for i in range(len(ui_d_refined_3)):
        if ui_d_refined_3[i][1] == '\r':
            ui_d_refined_3[i][1] = 'Key.enter'
        if ui_d_refined_3[i][1] == '\x08':
            ui_d_refined_3[i][1] = 'Key.backspace'
    for pynput_key in key_d_refined_2:
        if pynput_key[1].startswith("Key"):
            # todo: check this one
            if pynput_key[1] not in ['Key.enter', 'Key.backspace']:
                ui3_ts = np.array([u[4] for u in ui_d_refined_3])
                key_idx = np.searchsorted(ui3_ts, pynput_key[3])
                # todo: need to support key_idx = 0
                if key_idx != 0:
                    ui_before = ui_d_refined_3[key_idx - 1]
                    new_input = [1, pynput_key[1], "", ui_before[3], pynput_key[3], ui_before[5], pynput_key[4]]
                else:
                    new_input = [1, pynput_key[1], "", "", pynput_key[3], 0, pynput_key[4]]
                ui_d_refined_3.insert(key_idx, new_input)

    return ui_d_refined_3


if __name__ == "__main__":
    ui_p = "./temp_data_sj/ui_data.pkl"
    key_p = "./temp_data_sj/keyboard_recording.pkl"

    with open(ui_p, 'rb') as f:
        ui_d = pkl.load(f)
    with open(key_p, 'rb') as f:
        key_d = pkl.load(f)
    # print(key_d)
    # print(refine_data_kbd_init(key_d))
    refined_data = refine_all_data(ui_d, key_d)
    # pprint(refined_data)
    ui_df = list_to_pandas('ui', refined_data)
    ui_df.to_csv(Path("./ui_data_test.csv"))
