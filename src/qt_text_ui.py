import sys
import time
from queue import Empty
from sys import exit as sysExit

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtWidgets import QPlainTextEdit, QHBoxLayout, QPushButton, QVBoxLayout
from loguru import logger


class textbox(QPlainTextEdit):
    def __init__(self):
        QPlainTextEdit.__init__(self)

        self.setAttribute(QtCore.Qt.WA_InputMethodEnabled, True)
        self.inputMethodQuery(Qt.ImEnabled)


class CenterPane(QWidget):
    # DURATION_INT = 605
    DURATION_INT = 25

    def __init__(self, data_queue):
        QWidget.__init__(self)
        self.time_left_int = self.DURATION_INT
        self.data_queue = data_queue
        self.data = list()

        self.objCntrPane = textbox()
        self.objCntrPane.installEventFilter(self)

        self.time_passed_qll = QLabel(self.sec_to_str(self.DURATION_INT))

        self.exit_button = QPushButton('저장 및 글쓰기 종료', self)
        self.exit_button.clicked.connect(self.save_and_exit)

        hbox = QHBoxLayout()
        hbox.addWidget(self.time_passed_qll)
        hbox.addWidget(self.exit_button)

        vbox = QVBoxLayout(self)
        vbox.addLayout(hbox)
        vbox.addWidget(self.objCntrPane)

        self.setWindowTitle('Kologger')

        self.timer_start()
        self.update_gui()

        # self.objCntrPane.insertPlainText("write something")

    def save_and_exit(self):
        logger.info("save and exit button clicked!")
        self.my_qtimer.stop()
        self.close()
        self.objCntrPane.removeEventFilter(self)
        self.data_queue.put(("q", None))  # exit
        logger.debug("app kill message sent!")
        # TODO: Use different queue to exit safe!
        count = 0
        while True:
            try:
                data = self.data_queue.get(block=False)

                if data[0] == "Kill":
                    logger.info("Kologger termination")
                    logger.debug("got ui kill message")
                    break
            except Empty:
                count += 1
                if count > 2000:
                    logger.info("Kologger slower termination")
                    self.data_queue.put((2, None))
                    time.sleep(2.5)
                    break

            finally:
                time.sleep(0.001)

        # QtCore.QCoreApplication.instance().quit()
        sys.exit(0)

    def eventFilter(self, obj, event):
        if event.type() == 7:  # 7, 51, 6 is Eng, other input QkeyEvent
            cursor_position = self.objCntrPane.textCursor().anchor()
            self.data_queue.put([1,
                                 event.text(),
                                 event.key(),
                                 self.objCntrPane.toPlainText(),
                                 time.time(),
                                 cursor_position,
                                 ])

        if event.type() == 83 and obj is self.objCntrPane:  # IME language input
            cursor_position = self.objCntrPane.textCursor().anchor()

            self.data_queue.put([1,
                                 event.preeditString(),
                                 "",
                                 self.objCntrPane.toPlainText(),
                                 time.time(),
                                 cursor_position,
                                 ])
        return super().eventFilter(obj, event)

    def timer_start(self):
        self.time_left_int = self.DURATION_INT

        self.my_qtimer = QtCore.QTimer(self)
        self.my_qtimer.timeout.connect(self.timer_timeout)
        self.my_qtimer.start(1000)

        self.update_gui()

    def sec_to_str(self, time_left):
        min = time_left // 60
        sec = time_left % 60
        return f"남은시간: {min}분 {sec}초"

    def timer_timeout(self):
        self.time_left_int -= 1

        if self.time_left_int == 0:
            logger.info(f"termination due to timeout")
            self.my_qtimer.timeout.connect(self.save_and_exit)
        self.update_gui()

    def update_gui(self):
        self.time_passed_qll.setText(self.sec_to_str(self.time_left_int))


class InsertName(QWidget):
    def __init__(self, data_queue):
        QWidget.__init__(self)
        self.data_queue = data_queue
        self.data = list()



        self.button = QPushButton('ok', self)
        self.button.clicked.connect(self.show_next)
        self.text_box_widget = CenterPane(self.data_queue)
        self.text_box_widget.setGeometry(250, 450, 1000, 700)
        hbox = QVBoxLayout(self)
        self.textlabel = QLabel("이름을 입력하고 ok를 누르세요.")
        self.objCntrPane = textbox()
        hbox.addWidget(self.objCntrPane)
        hbox.addWidget(self.textlabel)
        hbox.addWidget(self.button)

    def show_next(self):
        subject_name = self.objCntrPane.toPlainText()
        if subject_name == "":
            subject_name = "default"
        self.data_queue.put(("3", subject_name))
        self.text_box_widget.show()
        self.close()


class MainWindow(QMainWindow):
    def __init__(self, data_queue, p_save, p_keyboard, parent=None):
        super(MainWindow, self).__init__(parent)
        winLeft = 250
        winTop = 450
        winWidth = 400  # 700
        winHeight = 200  # 600

        self.setWindowTitle('Kologger')
        # self.setGeometry(winLeft, winTop, 400, 200)
        # self.setCentralWidget(CenterPane(data_queue))
        self.setGeometry(winLeft, winTop, winWidth, winHeight)
        self.setCentralWidget(InsertName(data_queue))


def execute_ui(data_queue, p_save, p_keyboard):
    app = QApplication([])
    GUI = MainWindow(data_queue, p_save, p_keyboard)
    GUI.show()

    sysExit(app.exec_())
