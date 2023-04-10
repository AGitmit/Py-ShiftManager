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
""" using thread locks to make queue interaction thread safe. 1 for in 1 for out. """
lock1 = threading.Lock()
lock2 = threading.Lock()
lock3 = threading.Lock()
lock4 = threading.Lock()


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
                lock1.acquire()
                task = qu_in.get()
            except queue.Empty:
                if lock1.locked():
                    lock1.release()
                continue
            else:
                lock1.release()
                if task is None:
                    qu_in.task_done()
                    self.is_hired = False
                    break
                self.is_working = True
                func = dill.loads(task['func'])
                args = task['args']
                try:
                    result = func(*args)
                except Exception as err:
                    result = {"error": err, "task": func.__name__, "args": args}
                qu_in.task_done()
                try:
                    lock2.acquire()
                    qu_out.put(result)
                except queue.Full:
                    logger.logger.error("OUTPUT-QUEUE IS FULL.")
                finally:
                    if lock2.locked():
                        lock2.release()
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
                lock3.acquire()
                task = qu_in.get(timeout=0.1)
            except queue.Empty:
                if lock3.locked():
                    lock3.release()
                continue
            else:
                lock3.release()
                if isinstance(task, PoisonPill):
                    self.is_hired = False
                    qu_in.task_done()
                    break
                self.is_working = True
                func = dill.loads(task['func'])
                args = task['args']
                # insert timeout func here <<<<
                result = func(*args)
                qu_in.task_done()
                try:
                    lock4.acquire()
                    qu_out.put(result)
                except queue.Full:
                    logger.logger.error("OUTPUT-QUEUE IS FULL.")
                finally:
                    if lock4.locked():
                        lock4.release()
                self.is_working = False
