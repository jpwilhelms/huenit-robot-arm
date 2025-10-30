import threading


class ThreadSafeBufferOfSizeOne:
    def __init__(self):
        self.buffer = [None]
        self.lock = threading.Lock()

    def add(self, item):
        with self.lock:
            self.buffer[0] = item

    def get(self):
        with self.lock:
            return self.buffer[0]
