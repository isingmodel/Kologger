import time
from queue import Empty
from sys import exit as sysExit

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtWidgets import QPlainTextEdit, QHBoxLayout, QPushButton, QVBoxLayout
import sys


class textbox(QPlainTextEdit):
    def __init__(self):
        QPlainTextEdit.__init__(self)

        self.setAttribute(QtCore.Qt.WA_InputMethodEnabled, True)
        self.inputMethodQuery(Qt.ImEnabled)


class CenterPane(QWidget):
    def __init__(self, data_queue):
        QWidget.__init__(self)
        self.data_queue = data_queue
        self.data = list()

        self.objCntrPane = textbox()
        self.objCntrPane.installEventFilter(self)

        self.button = QPushButton('save and exit', self)
        self.button.clicked.connect(self.save_and_exit)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.objCntrPane)
        hbox.addWidget(self.button)
        # self.objCntrPane.insertPlainText("write something")

    def save_and_exit(self):
        print("save and exit button clicked!")
        self.objCntrPane.removeEventFilter(self)
        self.data_queue.put((2, None))  # exit
        # TODO: Use different queue to exit safe!
        count = 0
        while True:
            try:
                data = self.data_queue.get(block=False)

                if data[0] == "Kill":
                    print("exit!!")
                    break
            except Empty:
                count += 1
                if count > 2000:
                    self.data_queue.put((2, None))
                    time.sleep(3.5)
                    break

            finally:
                time.sleep(0.01)

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
            # print(event.AttributeType.Language)
            # print(event.commitString())
            # if event.key() == QtCore.Qt.Key_Return and self.objCntrPane.hasFocus():
            #     print('Enter pressed')
            pass
        return super().eventFilter(obj, event)


class InsertName(QWidget):
    def __init__(self, data_queue):
        QWidget.__init__(self)
        self.data_queue = data_queue
        self.data = list()

        self.objCntrPane = textbox()

        self.button = QPushButton('ok', self)
        self.button.clicked.connect(self.show_next)
        self.text_box_widget = CenterPane(self.data_queue)
        self.text_box_widget.setGeometry(250, 450, 1000, 700)
        hbox = QVBoxLayout(self)
        self.textlabel = QLabel("이름을 입력하고 ok를 누르세요.")
        hbox.addWidget(self.objCntrPane)
        hbox.addWidget(self.textlabel)
        hbox.addWidget(self.button)
        # self.objCntrPane.setPlainText("이름을 입력하고 ok를 누르세요.")

    def show_next(self):
        subject_name = self.objCntrPane.toPlainText()
        # if subject_name == "":
        subject_name = "default"
        self.data_queue.put((3, subject_name))
        self.hide()
        self.text_box_widget.show()


class MainWindow(QMainWindow):
    def __init__(self, data_queue, p_save, p_keyboard, parent=None):
        super(MainWindow, self).__init__(parent)
        winLeft = 250
        winTop = 450
        winWidth = 400  # 700
        winHeight = 200  # 600

        self.setWindowTitle('Kologer')
        # self.setGeometry(winLeft, winTop, 400, 200)
        # self.setCentralWidget(CenterPane(data_queue))
        self.setGeometry(winLeft, winTop, winWidth, winHeight)
        self.setCentralWidget(InsertName(data_queue))


def execute_ui(data_queue, p_save, p_keyboard):
    app = QApplication([])
    GUI = MainWindow(data_queue, p_save, p_keyboard)
    GUI.show()

    sysExit(app.exec_())
