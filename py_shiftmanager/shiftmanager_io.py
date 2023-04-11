import datetime
import queue
import multiprocessing
import threading
import dill
from typing import *

from .worker import Worker_IO
from .exceptions import QueueFullError
from .logger import Logger

"""
ShiftManager_IO:
This module is part of the Py_ShiftManager module for handling IO/Computational tasks -
in managed queued environment.

Handle all your I/O tasks without bothering with concurrency, multithreading -
or any other higher concept; simply use ShiftManager and enjoy the benefits of fast runtime speeds.

Read the 'Readme.md' file for more documentation and information.
"""

logger = Logger()


class ShiftManager_IO:
    _num_of_workers: int
    _q_in: queue.Queue
    _q_out: multiprocessing.Queue

    def __init__(self, num_of_workers: int = 2, daemon: bool = False, queue_size: int = 10) -> NoReturn:
        self._num_of_workers = num_of_workers
        self.daemon = daemon
        self.queue_size = queue_size
        self._q_in = queue.Queue(maxsize=self.queue_size)
        self._q_out = multiprocessing.Queue(maxsize=int(self.queue_size * 1.5))
        self.worker = Worker_IO()
        self.workers = []
        self._lock = threading.Lock()
        
    def __enter__(self, num_of_workers: int = 2, daemon: bool = False, queue_size: int = 10):
        self.manager = ShiftManager_IO(num_of_workers, daemon, queue_size)
        return self.manager
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> NoReturn:
        if exc_type is not None:
            logger.logger.error(f"An exception of type {exc_type} occurred: {exc_val}")
        self.manager.handle_work()
        self.manager.end_shift()

    def __repr__(self):
        return f"""ShiftManagerIO;daemonized={self.daemon};workers={self._num_of_workers}"""

    """ Manual scaling of workers """
    def __add__(self, x: int) -> NoReturn:
        self._num_of_workers += x

    def __sub__(self, x: int) -> NoReturn:
        self._num_of_workers -= x

    def __mul__(self, x: int) -> NoReturn:
        self._num_of_workers *= x

    def __divmod__(self, x: int) -> NoReturn:
        self._num_of_workers /= x

    """ Task and queue management """
    def new_task(self, func: Callable, *args) -> NoReturn:
        new_task = {"arrival_time": int(datetime.datetime.now().timestamp()), "func": dill.dumps(func), "args": args}
        try:
            with self._lock:
                self._q_in.put(new_task)
        except QueueFullError:
            logger.logger.warn("INPUT-QUEUE IS FULL.")

    def new_batch(self, tasks: List[tuple]) -> NoReturn:
        for task in tasks:
            self.new_task(*task)

    def queue_in_size(self) -> int or NoReturn:
        try:
            return self._q_in.qsize()
        except NotImplementedError:
            logger.logger.error("Input-queue .qsize() not implemented; exited gracefully.")

    def queue_out_size(self) -> int or NoReturn:
        try:
            return self._q_out.qsize()
        except NotImplementedError:
            logger.logger.error("Output-queue .qsize() not implemented; exited gracefully.")

    def handle_work(self) -> NoReturn:
        for i in range(self._num_of_workers):
            worker = threading.Thread(target=self.worker.work, args=(self._q_in, self._q_out))
            worker.daemon = self.daemon
            worker.start()
            self.workers.append(worker)

        if self._q_in.qsize() > 0:
            self._q_in.join()

    def get_results(self) -> List:
        # self._q_in.join()
        results = []
        with self._lock:
            while not self._q_out.empty():
                results.append(self._q_out.get())
        return results

    def join_all_workers(self) -> NoReturn:
        for worker in self.workers:
            worker.join()

    def end_shift(self) -> NoReturn:
        self._q_in.join()
        with self._lock:
            for _ in range(self._num_of_workers):
                self._q_in.put(None)
        self.join_all_workers()
        self.workers.clear()
        self.flush_queue()

    # def del_task(self, task: Any) -> NoReturn:
    #     temp_queue = queue.Queue()
    #     with self._lock:
    #         while not self._q_in.empty():
    #             current_item = self._q_in.get()
    #             self._q_in.task_done()
    #             if current_item == task:
    #                 continue
    #             temp_queue.put(current_item)
    #
    #         while not temp_queue.empty():
    #             self._q_in.put(temp_queue.get())

    def flush_queue(self) -> NoReturn:
        with self._lock:
            self._q_in.queue.clear()

    def autoscale(self, arrival_rate: float, avg_queue_time: float, avg_service_time: float) -> NoReturn:
        """
        [!] Currently unavailable.

        This method auto-calculates the number of workers/processes needed for the kind of tasks provided -
        and auto-scales them each time it's called.

        Params:
        :param arrival_rate: float
        :param avg_queue_time: float
        :param avg_service_time: float

        :return:
            No return.
        """
        pass
