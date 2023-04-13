import datetime
import queue
import multiprocessing
import threading
import dill
from typing import *

from .worker import Worker_IO
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
    def __init__(self, num_of_workers: int = 2, daemon: bool = False, input_q_size: int = 10, output_q_size: int = 15) -> NoReturn:
        self.__num_of_workers = num_of_workers
        self.__daemon = daemon
        self.__q_in = queue.Queue(maxsize=input_q_size)
        self.__q_out = multiprocessing.Queue(maxsize=output_q_size)
        self.__worker = Worker_IO()
        self.__workers = []
        self.__lock = threading.Lock()
        self.__put_timeout = 1
        
    def __enter__(self, num_of_workers: int = 2, daemon: bool = False, queue_size: int = 10):
        self.manager = ShiftManager_IO(num_of_workers, daemon, queue_size)
        return self.manager
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> NoReturn:
        if exc_type is not None:
            logger.logger.error(f"An exception of type {exc_type} occurred: {exc_val}")
        self.manager.handle_work()
        self.manager.end_shift()

    def __repr__(self):
        return f"""ShiftManagerIO;daemonized={self.__daemon};workers={self.__num_of_workers}"""

    """ Manual scaling of workers """
    def __add__(self, x: int) -> NoReturn:
        self.__num_of_workers += x

    def __sub__(self, x: int) -> NoReturn:
        self.__num_of_workers -= x

    def __mul__(self, x: int) -> NoReturn:
        self.__num_of_workers *= x

    def __divmod__(self, x: int) -> NoReturn:
        self.__num_of_workers /= x

    def __submit_task(self, new_task, force: bool = False) -> NoReturn:
        try:
            if force:
                self.__lock.acquire()
                self.__q_in.put_nowait(new_task)
            else:
                self.__lock.acquire()
                self.__q_in.put(new_task, timeout=self.__put_timeout)
        except queue.Full:
            logger.logger.error("INPUT-QUEUE IS FULL.")
        finally:
            self.__lock.release()
            
    def configure(self, **kwargs) -> NoReturn:
        if kwargs['put_timeout']:
            self.__put_timeout = kwargs['put_timeout']
        if kwargs['num_of_workers']:
            self.__num_of_workers = kwargs['num_of_workers']
        if kwargs['daemon']:
            self.__daemon = kwargs['daemon']

    """ Task and queue management """
    def new_task(self, func: Callable, *args, force: bool = False) -> NoReturn:
        new_task = {"arrival_time": int(datetime.datetime.now().timestamp()), "func": dill.dumps(func), "args": args}
        self.__submit_task(new_task, force)

    def new_batch(self, tasks: List[tuple], force: bool = False) -> NoReturn:
        for task in tasks:
            self.new_task(*task, force=force)

    # def queue_in_size(self) -> int or NoReturn:
    #     try:
    #         return self.__q_in.qsize()
    #     except NotImplementedError:
    #         logger.logger.error("Input-queue .qsize() not implemented; exited gracefully.")

    def handle_work(self) -> NoReturn:
        for _ in range(self.__num_of_workers):
            worker = threading.Thread(target=self.__worker.work, args=(self.__q_in, self.__q_out))
            worker.daemon = self.__daemon
            worker.start()
            self.__workers.append(worker)

        # if self.__q_in.qsize() > 0:
        #     self.__q_in.join()

    def get_results(self) -> List:
        results = []
        with self.__lock:
            while not self.__q_out.empty():
                results.append(self.__q_out.get())
        return results

    def __join_all_workers(self) -> NoReturn:
        for worker in self.__workers:
            worker.join()

    def end_shift(self) -> NoReturn:
        self.__q_in.join()
        with self.__lock:
            for _ in range(self.__num_of_workers):
                self.__q_in.put(None)
        self.__join_all_workers()
        self.__workers.clear()
        self.__flush_queue()

    def __flush_queue(self) -> NoReturn:
        with self.__lock:
            self.__q_in.queue.clear()

    def __autoscale(self, arrival_rate: float, avg_queue_time: float, avg_service_time: float) -> NoReturn:
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
