import sys
import time
from sys import exit as sysExit

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
# from PyQt5.QtGui     import
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QPlainTextEdit, QHBoxLayout, QPushButton


class textbox(QPlainTextEdit):
    def __init__(self):
        QPlainTextEdit.__init__(self)

        self.setAttribute(QtCore.Qt.WA_InputMethodEnabled, True)
        self.inputMethodQuery(Qt.ImEnabled)

from PyQt5 import QtGui
class CenterPane(QWidget):
    def __init__(self, data_queue):
        QWidget.__init__(self)
        self.data_queue = data_queue
        self.data = list()

        self.objCntrPane = textbox()
        # self.objCntrPane.textChanged.connect(self.add_realtime_text)
        # self.objCntrPane.keyPressed.connect(self.add_realtime_text)
        self.objCntrPane.installEventFilter(self)

        self.button = QPushButton('save and exit', self)
        self.button.clicked.connect(self.save_and_exit)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.objCntrPane)
        hbox.addWidget(self.button)
        # self.objCntrPane.insertPlainText("write something")

    # def add_realtime_text(self):
    #     self.data_queue.put((1, self.objCntrPane.toPlainText(), time.time()))

    def save_and_exit(self):
        self.data_queue.put(("exit",))
        time.sleep(0.5)
        sys.exit(0)

    def eventFilter(self, obj, event):
        # print("allevt", event.type(), event)
        if event.type() == 7: # 7, 51, 6 is QkeyEvent
            cursor_position = self.objCntrPane.textCursor().anchor()
            self.data_queue.put((1,
                                 event.text(),
                                 event.key(),
                                 self.objCntrPane.toPlainText(),
                                 time.time(),
                                 cursor_position,
                                 ))

        if event.type() == 83 and obj is self.objCntrPane:

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
