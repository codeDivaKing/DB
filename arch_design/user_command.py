# 一般来说这是需要写代码的涉及到一些多线程编程的题目。大概意思是设计一个允许用户提交command 的引擎。
# 当提交完command后返回一个object 能够查看 这个command 执行的状态，如果完成了，还能掉用用户传的回调函数对结果进行操作。
# chatgpt answer: https://chatgpt.com/s/t_68e70fb0d2548191bf9adcfe173bbe89
# https://g.co/gemini/share/e5e881efe087
import threading
import queue
import traceback

class TaskStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
###

class Future:
    def __init__(self):
        self._status = TaskStatus.PENDING
        self._result = None
        self._exception = None
        self._callbacks = []
        self._lock = threading.Lock()
        self._done_event = threading.Event()

    def set_running(self):
        with self._lock:
            self._status = TaskStatus.RUNNING

    def set_result(self, result):
        with self._lock:
            self._status = TaskStatus.COMPLETED
            self._result = result
        self._done_event.set()
        self._trigger_callbacks()

    def set_exception(self, exception):
        with self._lock:
            self._status = TaskStatus.FAILED
            self._exception = exception
        self._done_event.set()
        self._trigger_callbacks()

    def result(self, timeout=None):
        self._done_event.wait(timeout)
        if self._exception:
            raise self._exception
        return self._result

    def add_done_callback(self, fn):
        with self._lock:
            if self._status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                fn(self)
            else:
                self._callbacks.append(fn)

    def _trigger_callbacks(self):
        for cb in self._callbacks:
            try:
                cb(self)
            except Exception as e:
                print("Callback error:", e)

    def done(self):
        return self._status in (TaskStatus.COMPLETED, TaskStatus.FAILED)

    def status(self):
        with self._lock:
            return self._status


class CommandEngine:
    def __init__(self, max_workers=4):
        self.task_queue = queue.Queue()
        self.workers = []
        for _ in range(max_workers):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self.workers.append(t)

    def submit(self, func, *args, **kwargs):
        future = Future()
        self.task_queue.put((func, args, kwargs, future))
        return future

    def _worker(self):
        while True:
            func, args, kwargs, future = self.task_queue.get()
            if future.status() != TaskStatus.PENDING:
                continue
            try:
                future.set_running()
                result = func(*args, **kwargs)
                future.set_result(result)
            except Exception as e:
                traceback.print_exc()
                future.set_exception(e)
            finally:
                self.task_queue.task_done()
