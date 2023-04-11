import multiprocessing
from typing import *

from .worker import Worker_COM, PoisonPill
from .shiftmanager_io import ShiftManager_IO
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


class ShiftManager_Compute(ShiftManager_IO):
    pool: multiprocessing.Pool

    def __init__(self, num_of_workers: int = multiprocessing.cpu_count(), daemon: bool = False, queue_size: int = 10) -> NoReturn:
        super().__init__(num_of_workers, daemon)
        self._q_in = multiprocessing.JoinableQueue(maxsize=queue_size)
        self._q_out = multiprocessing.Queue(maxsize=int(queue_size * 1.5))
        self.worker = Worker_COM()
        self.workers = []
        self._lock = multiprocessing.Lock()
        
    def __enter__(self, num_of_workers: int = multiprocessing.cpu_count(), daemon: bool = False, queue_size: int = 10):
        self.manager = ShiftManager_Compute(num_of_workers, daemon, queue_size)
        return self.manager
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> NoReturn:
        if exc_type is not None:
            logger.logger.error(f"An exception of type {exc_type} occurred: {exc_val}")
        self.manager.handle_work()
        self.manager.end_shift()

    def __repr__(self):
        return f"""ShiftManagerCOM;daemonized={self.daemon};workers={self._num_of_workers}"""

    """ Manual scaling of workers """
    def __add__(self, x: int) -> NoReturn:
        super().__add__(x)

    def __sub__(self, x: int) -> NoReturn:
        super().__sub__(x)

    def __mul__(self, x: int) -> NoReturn:
        super().__mul__(x)

    def __divmod__(self, x: int) -> NoReturn:
        super().__divmod__(x)

    """ Task and queue management """
    def new_task(self, func: Callable, *args) -> NoReturn:
        super().new_task(func, *args)

    def new_batch(self, tasks: List[tuple]) -> NoReturn:
        super().new_batch(tasks)

    def queue_in_size(self) -> int or str:
        return super().queue_in_size()

    def queue_out_size(self) -> int or str:
        return super().queue_out_size()

    def handle_work(self) -> NoReturn:
        """ start pool without close() to enable continuous acceptance of new submitted tasks """
        self.pool = multiprocessing.Pool(processes=self._num_of_workers, initializer=self.worker.work,
                                    initargs=(self._q_in, self._q_out))

    def get_results(self) -> List:
        results = super().get_results()
        return results

    def end_shift(self) -> NoReturn:
        """ inject PoisonPill to input-queue and close() pool """
        for _ in range(self._num_of_workers):
            self._q_in.put(PoisonPill())
        self.pool.close()
        self.pool.join()

    # def terminate(self) -> NoReturn:
    #     """ send SIGTERM to pool workers """
    #     self.pool.terminate()
    #     self.flush_queue()

    # def del_task(self, task: Any) -> NoReturn:
    #     """
    #     using .task_done() on completed_tasks to sync-up with main process.
    #      """
    #     with self._lock:
    #         # Keep track of completed tasks
    #         completed_tasks = multiprocessing.JoinableQueue()
    #         i = 0  # using i since qsize() not implemented for multiprocessing.Queue()
    #         while not self._q_in.empty():
    #             current_item = self._q_in.get()
    #             if current_item['task'] == task:
    #                 continue
    #             completed_tasks.put(current_item)
    #             i += 1
    #         # Mark all completed tasks as done
    #         for _ in range(i):
    #             completed_tasks.task_done()
    #
    #         while not completed_tasks.empty():
    #             self._q_in.put(completed_tasks.get())

    def flush_queue(self) -> NoReturn:
        while not self._q_in.empty():
            self._q_in.get_nowait()

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
        super().autoscale(arrival_rate, avg_queue_time, avg_service_time)
