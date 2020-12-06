import time
from multiprocessing import Process

from pynput import mouse
from loguru import logger


class GetMouseData(Process):
    def __init__(self, data_queue, parent=None):
        super(Process, self).__init__(parent)
        self.data_queue = data_queue

    def on_move(self, x, y):
        ts = time.time()
        self.data_queue.put([4, x, y, 'move', ts])

    def on_click(self, x, y, button, pressed):
        ts = time.time()
        self.data_queue.put([4, x, y, str(button), ts])

    def on_scroll(self, x, y, dx, dy):
        ts = time.time()
        self.data_queue.put([4, dx, dy, "scroll", ts])

    def run(self):
        logger.info("Mouse listener start!")
        listener = mouse.Listener(on_move=self.on_move,
                                  on_click=self.on_click,
                                  on_scroll=self.on_scroll)
        listener.start()
        listener.join()

        return listener
