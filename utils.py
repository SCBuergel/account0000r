import time


def deep_get(d, *keys, default=None):
    """Safely traverse nested dicts: deep_get(obj, "a", "b", "c", default=0)"""
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, default)
        if d is default:
            return default
    return d


def _exponential_backoff(func, *args, max_wait=20, max_attempts=10, **kwargs):
    """calls any function with any parameters with an exponential backoff on any exception
    You can use this function for e.g. _exponential_backoff(web3.eth.get_block, 1234)
    """

    attempt = 0
    wait_time = 1  # Initial wait time of 1 second

    while True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            try:
                provider_info = f" (provider: {func.__self__.w3.provider})"
            except AttributeError:
                provider_info = ""
            print(f"Function call {func} with {args} failed: {e}{provider_info}. Retrying in {wait_time}s.")
            time.sleep(wait_time)
            attempt += 1
            wait_time = min(2 ** attempt, max_wait)

            if attempt > max_attempts:
                print(f"attempted to call more than {max_attempts} times. Aborting.")
                raise
