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
lock3 = multiprocessing.Lock()
lock4 = multiprocessing.Lock()


class Worker_IO:
    def __init__(self):
        self.__is_hired = True
        self.__is_working = False
        self.__role = "IO"

    def __repr__(self):
        return f"Worker;role={self.__role};is_working={self.__is_working};is_hired={self.__is_hired}"
    
    def work(self, qu_in: queue.Queue, qu_out: multiprocessing.Queue) -> NoReturn:
        self.__is_hired = True
        while self.__is_hired:
            try:
                lock1.acquire()
                task = qu_in.get(timeout=1)
            except queue.Empty:
                if lock1.locked():
                    lock1.release()
                continue
            else:
                lock1.release()
                if task is None:
                    qu_in.task_done()
                    self.__is_hired = False
                    break
                self.__is_working = True
                func = dill.loads(task['func'])
                args = task['args']
                kwargs = task['kwargs']
                try:
                    result = func(*args, **kwargs)
                except Exception as err:
                    result = {"error": err, "task": func.__name__, "args": args}
                qu_in.task_done()
                try:
                    lock2.acquire()
                    qu_out.put(result, timeout=1)
                except queue.Full:
                    logger.logger.error("OUTPUT-QUEUE IS FULL.")
                finally:
                    if lock2.locked():
                        lock2.release()
                    self.__is_working = False


class Worker_COM():
    __is_working: bool
    
    def __init__(self):
        self.__is_hired = True
        self.__role = "COM"

    def __repr__(self):
        return f"Worker;role={self.__role};is_working={self.__is_working};is_hired={self.__is_hired}"

    def work(self, qu_in: queue.Queue, qu_out: multiprocessing.Queue) -> NoReturn:
        self.__is_hired = True
        while self.__is_hired:
            try:
                lock3.acquire()
                task = qu_in.get(timeout=1)
            except queue.Empty:
                lock3.release()
                continue
            else:
                lock3.release()
                if isinstance(task, PoisonPill):
                    self.__is_hired = False
                    qu_in.task_done()
                    break
                self.__is_working = True
                func = dill.loads(task['func'])
                args = task['args']
                kwargs = task['kwargs']
                result = func(*args, **kwargs)
                qu_in.task_done()
                try:
                    lock4.acquire()
                    qu_out.put(result, timeout=1)
                    lock4.release()
                except queue.Full:
                    lock4.release()
                    logger.logger.error("OUTPUT-QUEUE IS FULL.")
                self.__is_working = False
