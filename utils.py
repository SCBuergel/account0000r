import time

def _exponential_backoff(func, *args, max_wait=20, max_attempts=10, **kwargs):
    """calls any function with any parameters with an expoential backoff on any exception
    You can use this function for e.g. _exponential_backoff(web3.eth.get_block, 1234)
    """

    attempt = 0
    wait_time = 1  # Initial wait time of 1 second

    while True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Function call {func}, {str(func)} with {args} failed: {e}. Retrying in {wait_time} seconds.")
            print(f"RPC provider: {func.__self__.w3.provider}")
            time.sleep(wait_time)
            attempt += 1
            wait_time = min(2 ** attempt, max_wait)  # Exponential backoff with a cap

            if wait_time >= max_wait:
                wait_time = max_wait

            if attempt > max_attempts:
                print(f"attempted to call more than {max_attempts} times. Aborting.")
                raise
