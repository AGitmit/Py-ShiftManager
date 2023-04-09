import dill
import queue
import multiprocessing
import threading
from typing import *

from .logger import Logger


class PoisonPill:
    """ This is used to kill worker process when end_shift() is called. """
    pass


logger = Logger()
lock = threading.Lock()


class Worker_IO:
    is_hired: bool
    is_working: bool
    role: str

    def __init__(self):
        self.is_hired = True
        self.is_working = False
        self.role = "IO"

    def __repr__(self):
        return f"Worker;role={self.role};is_working={self.is_working};is_hired={self.is_hired}"

    def work(self, qu_in: queue.Queue, qu_out: multiprocessing.Queue) -> NoReturn:
        self.is_hired = True
        while self.is_hired:
            try:
                lock.acquire()
                task = qu_in.get(timeout=0.1)
            except queue.Empty:
                lock.release()
                continue
            else:
                if task is None:
                    qu_in.task_done()
                    lock.release()
                    self.is_hired = False
                    break
                self.is_working = True
                func = dill.loads(task['func'])
                args = task['args']
                result = func(*args)
                try:
                    qu_out.put(result)
                except queue.Full:
                    logger.logger.error("OUTPUT-QUEUE IS FULL.")
                qu_in.task_done()
                lock.release()
                self.is_working = False


class Worker_COM(Worker_IO):
    def __init__(self):
        super().__init__()
        self.role = "COM"

    def __repr__(self):
        super().__repr__()

    def work(self, qu_in: queue.Queue, qu_out: multiprocessing.Queue) -> NoReturn:
        self.is_hired = True
        while self.is_hired:
            try:
                task = qu_in.get(timeout=0.1)
            except queue.Empty:
                continue
            else:
                if isinstance(task, PoisonPill):
                    self.is_hired = False
                    qu_in.task_done()
                    # qu_in.put(task)  # Put the PoisonPill back into the queue for other workers to receive
                    break
                self.is_working = True
                func = dill.loads(task['func'])
                args = task['args']
                result = func(*args)
                qu_in.task_done()
                try:
                    qu_out.put(result)
                except queue.Full:
                    logger.logger.error("OUTPUT-QUEUE IS FULL.")
                self.is_working = False
