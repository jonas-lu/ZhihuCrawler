import threading
import time


class Sub(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._terminated = False

    def run(self):
        while True:
            if self._terminated:
                print('Terminated gracefully')
                break
            print('Not terminated')
            time.sleep(10)

    def terminate(self):
        self._terminated = True
