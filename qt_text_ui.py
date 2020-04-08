from sys import exit as sysExit

from PyQt5.QtCore import Qt
# from PyQt5.QtGui     import
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QPlainTextEdit, QHBoxLayout, QPushButton
from PyQt5 import QtCore
import pickle as pkl

import time


class textbox(QPlainTextEdit):
    def __init__(self):
        QPlainTextEdit.__init__(self)

        self.setAttribute(QtCore.Qt.WA_InputMethodEnabled, True)
        self.inputMethodQuery(Qt.ImEnabled)


class CenterPane(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.data = list()

        self.objCntrPane = textbox()
        self.objCntrPane.textChanged.connect(self.add_realtime_text)
        self.button = QPushButton('save', self)
        self.button.clicked.connect(self.save_realtime_text)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.objCntrPane)
        hbox.addWidget(self.button)
        self.objCntrPane.insertPlainText("write something")

    def add_realtime_text(self):
        print(self.objCntrPane.toPlainText(), time.time(), "\n")
        self.data.append((self.objCntrPane.toPlainText(), time.time()))
        # print(self.objCntrPane.cursorRect())

    def save_realtime_text(self):
        data = self.data
        with open("./temp_data/ui_data.pkl", 'wb') as f:
            pkl.dump(data, f)





class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        winLeft = 100
        winTop = 100
        winWidth = 700
        winHeight = 600
        data = list()

        self.setWindowTitle('Main Window')
        self.setGeometry(winLeft, winTop, winWidth, winHeight)
        self.setCentralWidget(CenterPane())




def execute_ui(nothing):
    app = QApplication([])
    print(123)
    GUI = MainWindow()
    GUI.show()

    sysExit(app.exec_())


if __name__ == "__main__":
    app = QApplication([])

    GUI = MainWindow()
    GUI.show()

    sysExit(app.exec_())