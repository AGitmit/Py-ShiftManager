import multiprocessing
import datetime
import dill
from typing import *
import queue
from .worker import Worker_COM, PoisonPill
from .logger import Logger

"""
ShiftManager_Compute:
This module is part of the Py-ShiftManager module for handling IO/Computational tasks -
in managed queued environment.

Handle all your computational tasks without bothering with concurrency, multiprocessing -
or any other higher concept; simply use ShiftManager and enjoy the benefits of fast runtime speeds.

Read the 'Readme.md' file for more documentation and information.
"""

logger = Logger()


class ShiftManager_Compute():
    __pool: multiprocessing.Pool

    def __init__(self, num_of_workers: int = multiprocessing.cpu_count(), daemon: bool = False, input_q_size: int = 10, output_q_size: int = 15) -> NoReturn:
        self.__num_of_workers = num_of_workers
        self.__daemon = daemon
        self.__q_in = multiprocessing.JoinableQueue(maxsize=input_q_size)
        self.__q_out = multiprocessing.Queue(maxsize=output_q_size)
        self.__worker = Worker_COM()
        self.__lock = multiprocessing.Lock()
        self.__put_timeout = 1
        
    def __enter__(self, num_of_workers: int = multiprocessing.cpu_count(), daemon: bool = False, queue_size: int = 10):
        self.manager = ShiftManager_Compute(num_of_workers, daemon, queue_size)
        return self.manager
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> NoReturn:
        if exc_type is not None:
            logger.logger.error(f"An exception of type {exc_type} occurred: {exc_val}")
        self.manager.handle_work()
        self.manager.end_shift()

    def __repr__(self):
        return f"""ShiftManagerCOM;daemonized={self.__daemon};workers={self.__num_of_workers}"""

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
    def new_task(self, func: Callable, *args, force: bool = False, **kwargs) -> NoReturn:
        new_task = {"arrival_time": int(datetime.datetime.now().timestamp()), "func": dill.dumps(func), "args": args, "kwargs": kwargs}
        self.__submit_task(new_task, force)

    def new_batch(self, tasks: List[Tuple[Callable, Tuple, Dict[str, Any]]], force: bool = False) -> NoReturn:
        for task in tasks:
            func, args, kwargs = task
            self.new_task(func, *args, force=force, **kwargs)


    def handle_work(self) -> NoReturn:
        """ start pool without close() to enable continuous acceptance of new submitted tasks """
        self.__pool = multiprocessing.Pool(processes=self.__num_of_workers, initializer=self.__worker.work,
                                    initargs=(self.__q_in, self.__q_out))

    def get_results(self) -> List:
        results = []
        with self.__lock:
            while not self.__q_out.empty():
                results.append(self.__q_out.get())
        return results

    def end_shift(self) -> NoReturn:
        """ inject PoisonPill to input-queue and close() pool """
        for _ in range(self.__num_of_workers):
            self.__q_in.put(PoisonPill())
        self.__pool.close()
        self.__pool.join()

    def __flush_queue(self) -> NoReturn:
        while not self.__q_in.empty():
            self.__q_in.get_nowait()

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
        super().__autoscale(arrival_rate, avg_queue_time, avg_service_time)
