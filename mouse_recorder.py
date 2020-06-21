import time
from multiprocessing import Process

from pynput import mouse


class GetMouseData(Process):
    def __init__(self, data_queue, parent=None):
        super(Process, self).__init__(parent)
        self.data_queue = data_queue

    def on_move(self, x, y):
        ts = time.time()
        # print([x, y, 'move'])
        self.data_queue.put([x, y, 'move', ts])

    def on_click(self, x, y, button, pressed):
        ts = time.time()
        # print([x, y, str(button)])
        self.data_queue.put([x, y, str(button), ts])

    def on_scroll(self, x, y, dx, dy):
        ts = time.time()
        # print([x, y, dx, dy])
        self.data_queue.put([dx, dy, "scroll", ts])

    def run(self):
        print("Mouse listener start!")
        listener = mouse.Listener(on_move=self.on_move,
                                  on_click=self.on_click,
                                  on_scroll=self.on_scroll)
        listener.start()
        listener.join()

        return listener
