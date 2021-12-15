import signal


def on_signal(func):
    def wrapper(*args, **kwargs):
        def handler(signum, frame):
            print(f"Caught {signal.Signals(signum).name}")
            func(*args, **kwargs)

        return handler

    return wrapper
