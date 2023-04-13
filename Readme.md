# Py-ShiftManager
#### v0.1.3

Py-ShiftManager is a Python module that provides a managed queue environment for handling IO and computational tasks, allowing you to easily manage concurrency and multiprocessing without worrying about the details.

## Installation
You can install Py-ShiftManager using pip:
`pip install py-shiftmanager`

## What's new in v0.1.3
This small update is dedicated to my friend Ram Manor :).
#### added in v0.1.1
* ⏲️ Introducing new timeout wrapper: `@timeout_timer()` - import it, decorate your functions, set amount of seconds, get a result for a task that has timed out without blocking your flow. 
* 🔒 Better thread locking system to ensure even smaller chances of getting in a deadlock situation.  
* 🛠️ *ShiftManager_Compute* now initializes the number of workers with the number of CPU's available in the system, by default.  
* 🛠️ *ShiftManager_IO* now initializes the number of workers to `2`, instead of `1`, by default.  
#### added in v0.1.2
* ▶️ New context manager for *ShiftManager* - use the `with` keyword and get all the benefits of *ShiftManager* for a specific set of tasks, for even less lines of code!    
`with ShiftManager_Compute() as manager:`  
`   manager.new_task(lambda x: x**2, 4)`  
`   manager.new_task(lambda x: x**4, 13)`  
then get the results:  
`results = manager.get_results()`  
It's that simple.  
#### added in v0.1.3
* 🛠️ Improved handling of queue exceptions - a better managing solution for large incoming amount of tasks.  
* 🛠️ Improved task submission logic.
* 🔒 Improved encapsulation.
* 🛠️ New method added - `configure()`; read more under *'API'* section.   
* 🛠️ Improved concurrency and parallelism in the IO module.
* ⌫ Deprecated methods - `queue_in_size()`, `queue_out_size()` 

## Usage
Here's an example of how to use Py-ShiftManager to handle IO tasks:  
`from py-shiftmanager import ShiftManager_IO`.  
Now, lets also import *timeout_timer* wrapper:  
`from py-shiftmanager.timeout import timeout_timer`

# Create a new ShiftManager instance with 4 workers
`manager = ShiftManager_IO(num_of_workers=4)`  
By default *ShiftManager* objects init with these values for its attributes:
* num_of_workers = `2`
* daemon = `False`
* input_q_size = `10`
* output_q_size = `15`
 
**Note**: Once initialized, queue size cannot be changed.  

# Add some tasks to the input queue
Assume we have created a function called 'get_status()' that uses *requests* and applied the *@timeout_timer* decorator, with a 3 seconds timeout counter, in case a task takes longer than 3 seconds to complete, like so:  
`import requests`  
`@timeout_timer(seconds=3)`  
`def get_status(url):`  
`   return requests.get(url).status_code`  
We can assign single tasks to the queue:  
`manager.new_task(get_status, "http://www.google.com")`  
`manager.new_task(get_status, "http://www.facebook.com")`  
`manager.new_task(get_status, "http://www.twitter.com")`   
Or we can submit a batch by passing a list of tuples:  
`tasks = [(get_status, "http://www.google.com"),(get_status, "http://www.facebook.com")]`  
`manager.new_batch(tasks)`  
  
**Note**: you can also pass in *lambda* functions.

# Handle the tasks
`manager.handle_work()`  
*ShiftManager* spins up the workers and starts consuming tasks from the input queue.  
Since we applied the *timeout_timer* decorator, if a task takes longer than 3 seconds - it will be terminated, but you'll still recieve a result with the task details, and that it has ran out of time.  

# Wait for the tasks to complete
`manager.end_shift()`  
This method sends a shut-down signal to all workers and waits for them to shut-down gracefully.

**Note**: this does not interfere with retrieving results from the output queue at any time.


And here's an example of how to use Py-ShiftManager to handle computational tasks:

`from py-shiftmanager import ShiftManager_Compute`  

# Create a new ShiftManager instance with 4 workers
`manager = ShiftManager_Compute(num_of_workers=4)`  
But this time we'll increase the number to 5 using simple addition:  
`manager + 1` - now *manager* is set to run 5 workers.   

By default *ShiftManager_Compute* initializes with these default values for its attributes:  
* num_of_workers = *number of CPU's in the system.* 
* daemon = `False`
* input_q_size = `10`
* output_q_size = `15`  

**Note**: Once initialized, queue size cannot be changed.  
# Add some tasks to the input queue
We can assign single tasks, like so:  
`manager.new_task(lambda x: x**2, 3)`  
`manager.new_task(lambda x: x**3, 4)`  
`manager.new_task(lambda x, y: x**4 + y, 5, 9)`  
or submit a batch by passing a list of tuples:  
`tasks = [(lambda x: x**2, 3),(lambda x: x**3, 4)]`
`manager.new_batch(tasks)`

**Note**: Accepting *lambda* functions and normal functions.

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
`ShiftManager_IO(num_of_workers: int = 1, daemon: bool = False, input_q_size: int = 10, output_q_size: int = 15) -> None`  
Creates a new ShiftManager instance with the specified number of workers, daemon status, input queue size and output queue size.

`new_task(func: Callable, task: Any, force: bool = False) -> None`  
Adds a new task to the input queue; you could force it if you want.

`new_batch(tasks: List[tuple], force: bool = False) -> None`  
Adds a list of tasks to the input queue; you could force it if you want.

`handle_work() -> None`  
Handles the tasks in the input queue.

`get_results() -> List`  
Returns the results of the completed tasks from the output queue.

`end_shift() -> None`  
Ends the shift and waits for all tasks to complete.  

`configure(**kwargs) -> None`  
Allows the user to configure the following attributes by passing keyword arguments:  
* `daemon: bool` - reconfigure workers daemon status. 
* `put_timeout: int` - reconfigure timeout (in seconds) for input queue task submission (default is `1` second).
* `num_of_workers: int` - reconfigure number of workers.  

**ShiftManager_Compute**  
`ShiftManager_Compute(num_of_workers: int = 1, daemon: bool = False, input_q_size: int = 10, output_q_size: int = 15) -> None`  
Creates a new ShiftManager instance with the specified number of workers, daemon status, input queue size and output queue size.

`new_task(func: Callable, task: Any) -> None`  
Adds a new task to the input queue.

`new_batch(tasks: List[tuple]) -> None`  
Adds a list of tasks to the input queue.

`handle_work() -> None`  
Handles the tasks in the input queue.

`get_results() -> List`  
Returns the results of the completed tasks from the output queue.

`end_shift() -> None`  
Ends the shift and waits for all tasks to complete.  

`configure(**kwargs) -> None`  
Allows the user to configure the following attributes by passing keyword arguments:  
* `daemon: bool` - reconfigure workers daemon status. 
* `put_timeout: int` - reconfigure timeout (in seconds) for input queue task submission (default is `1` second).
* `num_of_workers: int` - reconfigure number of workers.  

**timeout_timer**  
`@timeout_timer(seconds: int = 5)`  
A decorator that attaches a timeout counter to your methods, use it to set a time limit to tasks in seconds; `5` seconds by default.
