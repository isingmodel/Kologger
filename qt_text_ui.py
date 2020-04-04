from sys import exit as sysExit

from PyQt5.QtCore import Qt
# from PyQt5.QtGui     import
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QPlainTextEdit, QHBoxLayout
from PyQt5 import QtCore

import time


class CenterObject(QPlainTextEdit):
    def __init__(self):
        QPlainTextEdit.__init__(self)

        self.setAttribute(QtCore.Qt.WA_InputMethodEnabled, True)
        self.inputMethodQuery(Qt.ImEnabled)


class CenterPane(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.objCntrPane = CenterObject()
        self.objCntrPane.textChanged.connect(self.save_realtime_text)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.objCntrPane)
        self.objCntrPane.insertPlainText("write something")

    def save_realtime_text(self):
        print(self.objCntrPane.toPlainText(), time.time(), "\n")
        # print(self.objCntrPane.cursorRect())


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        winLeft = 100
        winTop = 100
        winWidth = 400
        winHeight = 300

        self.setWindowTitle('Main Window')
        self.setGeometry(winLeft, winTop, winWidth, winHeight)
        self.setCentralWidget(CenterPane())

def execute_ui(nothing):
    app = QApplication([])

    GUI = MainWindow()
    GUI.show()

    sysExit(app.exec_())





# This routine needs to be made as simple as possible
if __name__ == "__main__":
    app = QApplication([])

    GUI = MainWindow()
    GUI.show()

    sysExit(app.exec_())