import threading

def timeout_timer(func=None, seconds=5, error_message='Task timed out.'):
    """ Timeout wrapper, sets a seconds timer on a separate running thread with the join().
        The main key here is setting the daemon flag, so it shuts the thread down when the time passes-
        even though it didnt finish it's task.
    """
    if func is None:
        return lambda f: timeout_timer(f, seconds, error_message)

    def wrapper(*args):
        result = {"task": func.__name__, "args": args}
        def target():
            result["result"] = func(*args)
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(seconds)
        if thread.is_alive():
            result["error"] = error_message
        return result
    return wrapper
