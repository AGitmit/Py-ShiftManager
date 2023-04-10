# Py-ShiftManager
#### v0.1.0

Py-ShiftManager is a Python module that provides a managed queue environment for handling IO and computational tasks, allowing you to easily manage concurrency and multiprocessing without worrying about the details.

## Installation
You can install Py-ShiftManager using pip:
`pip install py-shiftmanager`

## Usage
Here's an example of how to use Py-ShiftManager to handle IO tasks:
`from py-shiftmanager import ShiftManager_IO`.

# Create a new ShiftManager instance with 4 workers
`manager = ShiftManager_IO(num_of_workers=4)`  

**Note**: by default *ShiftManager* objects init with these values for its attributes:
* num_of_workers = `1`
* daemon = `False`
* queue size = `10`    

Also, by default the output queue is sent to 1.5 times the input queue size.
  
# Add some tasks to the input queue
Assume we have created a function, like so:  
`import requests`  
`get_status = lambda url: requests.get(url).status_code`  
We can assign single tasks to the queue:  
`manager.new_task(get_status, "http://www.google.com")`  
`manager.new_task(get_status, "http://www.facebook.com")`  
`manager.new_task(get_status, "http://www.twitter.com")`   
Or we can submit a batch by passing a list of tuples:  
`tasks = [(get_status, "http://www.google.com"),(get_status, "http://www.facebook.com")]`  
`manager.new_batch(tasks)`

# Handle the tasks
`manager.handle_work()`  
*ShiftManager* spins up the workers and starts consuming tasks from the input queue.

# Wait for the tasks to complete
`manager.end_shift()`  
This method sends a shut-down signal to all workers and waits for them to shut-down gracefully.

**Note**: this does not interfere with retrieving results from the output queue at any time.
  

And here's an example of how to use Py-ShiftManager to handle computational tasks:

`from py-shiftmanager import ShiftManager_Compute`  

# Create a new ShiftManager instance with 2 workers
`manager = ShiftManager_Compute(num_of_workers=2)`  
But this time we'll increase the number to 4 using simple addition:  
`manager + 2` - now *manager* is set to run 4 workers.

**Note**: again, same default values for the attributes applied here.

# Add some tasks to the input queue
We can assign single tasks, like so:  
`manager.new_task(lambda x: x**2, 3)`  
`manager.new_task(lambda x: x**3, 4)`  
`manager.new_task(lambda x, y: x**4 + y, 5, 9)`  
or submit a batch by passing a list of tuples:  
`tasks = [(lambda x: x**2, 3),(lambda x: x**3, 4)]`
`manager.new_batch(tasks)`

**Note**: both methods accept *lambda* functions or normal functions.

# Handle the tasks
`manager.handle_work()`  
*ShiftManager* will start the workers and begin performing the calculations.

# Get the results
`results = manager.get_results()`  
`print(results)` # Output: [9, 634, 9, 64, 64]

**Note**: you can retrieve results whenever you want, at any point, since results are stored in a separate queue, and all workers are running concurrently.

# Wait for the tasks to complete
`manager.end_shift()`  
This method sends a shut-down signal to all workers, they will stop gracefully.

## API

**ShiftManager_IO**  
`ShiftManager_IO(num_of_workers: int = 1, daemon: bool = False, queue_size: int = 10) -> None`  
Creates a new ShiftManager instance with the specified number of workers, daemon status, and queue size.

`new_task(func: Callable, task: Any) -> None`  
Adds a new task to the input queue.

`new_batch(tasks: List[tuple]) -> None`  
Adds a list of tasks to the input queue.

`queue_in_size() -> int`  
Returns the current size of the input queue, if implemented, else, exists gracefully.

`queue_out_size() -> int`  
Returns the current size of the output queue, if implemented, else, exists gracefully.

`handle_work() -> None`  
Handles the tasks in the input queue.

`get_results() -> List`  
Returns the results of the completed tasks from the output queue.

`end_shift() -> None`  
Ends the shift and waits for all tasks to complete.

**ShiftManager_Compute**  
`ShiftManager_Compute(num_of_workers: int = 1, daemon: bool = False, queue_size: int = 10) -> None`  
Creates a new ShiftManager instance with the specified number of workers, daemon status, and queue size.

`new_task(func: Callable, task: Any) -> None`  
Adds a new task to the input queue.

`new_batch(tasks: List[tuple]) -> None`  
Adds a list of tasks to the input queue.

`queue_in_size() -> int`  
Returns the current size of the input queue, if implemented, else, exists gracefully.

`queue_out_size() -> int`  
Returns the current size of the output queue, if implemented, else, exists gracefully.

`handle_work() -> None`  
Handles the tasks in the input queue.

`get_results() -> List`  
Returns the results of the completed tasks from the output queue.

`end_shift() -> None`  
Ends the shift and waits for all tasks to complete.
