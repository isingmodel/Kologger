import time
from queue import Empty
from sys import exit as sysExit

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QPlainTextEdit, QHBoxLayout, QPushButton
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
        self.data_queue.put((2, None)) # exit
        time.sleep(1.5)
        # TODO: Use different queue to exit safe!
        while True:
            try:
                data = self.data_queue.get(block=False)

                if data[0] == 4:
                    break

            except Empty:
                pass
            finally:
                time.sleep(0.01)

        # QtCore.QCoreApplication.instance().quit()
        sys.exit(0)

    def eventFilter(self, obj, event):
        if event.type() == 7:  # 7, 51, 6 is Eng, other input QkeyEvent
            cursor_position = self.objCntrPane.textCursor().anchor()
            self.data_queue.put((1,
                                 event.text(),
                                 event.key(),
                                 self.objCntrPane.toPlainText(),
                                 time.time(),
                                 cursor_position,
                                 ))

        if event.type() == 83 and obj is self.objCntrPane:  # IME language input
            cursor_position = self.objCntrPane.textCursor().anchor()

            self.data_queue.put((1,
                                 event.preeditString(),
                                 "",
                                 self.objCntrPane.toPlainText(),
                                 time.time(),
                                 cursor_position,
                                 ))
            # print(event.AttributeType.Language)
            # print(event.commitString())
            # if event.key() == QtCore.Qt.Key_Return and self.objCntrPane.hasFocus():
            #     print('Enter pressed')
            pass
        return super().eventFilter(obj, event)


class MainWindow(QMainWindow):
    def __init__(self, data_queue, p_save, p_keyboard, parent=None):
        super(MainWindow, self).__init__(parent)
        winLeft = 200
        winTop = 200
        winWidth = 700
        winHeight = 600

        self.setWindowTitle('Main Window')
        self.setGeometry(winLeft, winTop, winWidth, winHeight)
        self.setCentralWidget(CenterPane(data_queue))


def execute_ui(data_queue, p_save, p_keyboard):
    app = QApplication([])
    GUI = MainWindow(data_queue, p_save, p_keyboard)
    GUI.show()

    sysExit(app.exec_())
