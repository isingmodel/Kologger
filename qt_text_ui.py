from sys import exit as sysExit

from PyQt5.QtCore import Qt
# from PyQt5.QtGui     import
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QPlainTextEdit, QHBoxLayout, QPushButton
from PyQt5 import QtCore
import pickle as pkl

import time
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
        self.objCntrPane.textChanged.connect(self.add_realtime_text)
        self.button = QPushButton('save&exit', self)
        self.button.clicked.connect(self.save_and_exit)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.objCntrPane)
        hbox.addWidget(self.button)
        self.objCntrPane.insertPlainText("write something")


    def add_realtime_text(self):
        # print(self.objCntrPane.toPlainText(), time.time(), "\n")
        # self.data.append((self.objCntrPane.toPlainText(), time.time()))
        # print(self.objCntrPane.cursorRect())
        self.data_queue.put(('pyqt', self.objCntrPane.toPlainText(), time.time()))

    def save_and_exit(self):
        self.data_queue.put(("exit",))
        time.sleep(0.5)
        sys.exit(0)



class MainWindow(QMainWindow):
    def __init__(self, data_queue, p_save, p_keyboard, parent=None):
        super(MainWindow, self).__init__(parent)
        winLeft = 100
        winTop = 100
        winWidth = 700
        winHeight = 600
        data = list()

        self.setWindowTitle('Main Window')
        self.setGeometry(winLeft, winTop, winWidth, winHeight)
        self.setCentralWidget(CenterPane(data_queue))


def execute_ui(data_queue, p_save, p_keyboard):
    app = QApplication([])
    GUI = MainWindow(data_queue, p_save, p_keyboard)
    GUI.show()

    sysExit(app.exec_())


if __name__ == "__main__":
    app = QApplication([])

    GUI = MainWindow()
    GUI.show()

    sysExit(app.exec_())