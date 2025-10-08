import threading

class Future:
    def __init__(self):
        self._done = False
        self._result = None
        self._callbacks = []

    def set_result(self, result):
        self._done = True
        self._result = result
        for cb in self._callbacks:
            cb(result)

    def add_done_callback(self, fn):
        if self._done:
            fn(self._result)
        else:
            self._callbacks.append(fn)

    def result(self):
        return self._result

    def done(self):
        return self._done


class CommandEngine:
    def submit(self, func, *args, **kwargs):
        future = Future()
        def run():
            res = func(*args, **kwargs)
            future.set_result(res)
        threading.Thread(target=run).start()
        return future
