import datetime
import os
import pickle as pkl
import platform
import random
import sys
import time
import zipfile
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import freeze_support
from pathlib import Path
from queue import Empty

import win32gui
from loguru import logger
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import src.keyboard_recorder as kr
import src.mouse_recorder as mr
import src.qt_text_ui as ui


def get_data_from_queue(d_q, temp_queue):
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("./add_on_dist/mycreds.txt")
    gauth.LoadClientConfigFile(client_config_file="./add_on_dist/client_secrets.json")
    drive = GoogleDrive(gauth)

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
                logger.info("got exit message")
                break
            elif data[0] == 3:
                logger.info(f"subject name: {data[1]}")
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
    logger.info("temp record saving!")
    d_q.put((3, None))
    now = datetime.datetime.now()
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    defaultname = "default"
    save_dir = current_path / defaultname
    try:
        os.makedirs(save_dir)
    except FileExistsError:
        pass

    time_now = "{}_{}_{}_{}_{}".format(now.year, now.month, now.day, now.hour, now.minute)
    with open(save_dir / f"default_pynput_{time_now}.pkl", 'wb') as f_pynput:
        pkl.dump(pynput_data, f_pynput)
    with open(save_dir / f"default_pyqt_{time_now}.pkl", 'wb') as f_ui:
        pkl.dump(pyqt_data, f_ui)
    with open(save_dir / f"default_mouse_{time_now}.pkl", 'wb') as f_mouse:
        pkl.dump(mouse_data, f_mouse)
    with open(save_dir / f"default_windows_name_{time_now}.pkl", 'wb') as f_windows:
        pkl.dump(window_name_data, f_windows)
    with open(save_dir / "sub_info.txt", 'w') as f_sub:
        f_sub.write(subject_name)
    logger.info("zipping start")
    zip_file_name = f'result_{random.random()}.zip'
    zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
    zipdir(f"./{defaultname}", zipf)
    zipf.close()
    cool_image = drive.CreateFile()
    cool_image.SetContentFile(zip_file_name)  # load local file data into the File instance
    cool_image.Upload()

    d_q.put(("Kill", None))
    d_q.put(("Kill", None))


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def temp_data_saving(temp_queue):
    count = 0
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    save_dir = current_path / "default"
    try:
        os.makedirs(save_dir)
    except FileExistsError:
        pass
    while True:
        try:
            data = temp_queue.get(block=False)
            if data == "exit":
                logger.info("temp exit")
                break
            count += 1
            with open(save_dir / f"{count}_temp.pkl", 'wb') as f:
                pkl.dump(data, f)

        except Empty:
            pass
        finally:
            time.sleep(0.05)


def get_current_window_name(d_q: Queue):
    while True:
        pycwnd = win32gui.GetForegroundWindow()
        d_q.put([5, time.time(), win32gui.GetWindowText(pycwnd)])
        time.sleep(0.15)


def main():
    data_queue = Queue(maxsize=1000)
    temp_queue = Queue(maxsize=5000)
    p_save = Process(target=get_data_from_queue, args=(data_queue, temp_queue))
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


if __name__ == "__main__":
    freeze_support()
    if platform.system() != "Windows":
        logger.error("This program runs only on Windows!!")
        sys.exit(0)
    main()

