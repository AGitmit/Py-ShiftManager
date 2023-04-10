import threading

def timeout_timer(func=None, seconds=5, error_message='Task timed out.'):
    if func is None:
        return lambda f: timeout_timer(f, seconds, error_message)

    def wrapper(*args):
        result = {"task": func.__name__, "args": args}
        def target():
            result["result"] = func(*args)
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(seconds)
        if thread.is_alive():
            result["error"] = error_message
        return result

    return wrapper
