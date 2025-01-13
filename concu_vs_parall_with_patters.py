import time
import math
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import lru_cache

def measure_time(func):
    """
    Decorator to measure the time it takes for a function to execute.
    Prints the elapsed time in seconds.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"Function '{func.__name__}' took {elapsed:.4f} seconds to complete.")
        return result
    return wrapper

# --------------------------------------------------------------
# 1) Naive Recursive Fibonacci
# --------------------------------------------------------------
def fibonacci_naive(n):
    """
    Simple recursive Fibonacci function (CPU-bound).
    This is the same naive version you already use.
    """
    if n <= 1:
        return n
    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)

# --------------------------------------------------------------
# 2) Memoized Fibonacci (design pattern: memoization)
# --------------------------------------------------------------
@lru_cache(maxsize=None)
def fibonacci_memo(n):
    """
    Fibonacci with memoization using Python's built-in lru_cache.
    Significantly faster for repeated calls on overlapping subproblems.
    """
    if n <= 1:
        return n
    return fibonacci_memo(n - 1) + fibonacci_memo(n - 2)

# --------------------------------------------------------------
# Multi-Threading versions
# --------------------------------------------------------------
@measure_time
def multi_threaded_fibonacci_naive(numbers):
    """
    Computes naive Fibonacci for a list of numbers using multi-threading.
    """
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(fibonacci_naive, numbers))
    return results

@measure_time
def multi_threaded_fibonacci_memo(numbers):
    """
    Computes memoized Fibonacci for a list of numbers using multi-threading.
    """
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(fibonacci_memo, numbers))
    return results

# --------------------------------------------------------------
# Multi-Processing versions
# --------------------------------------------------------------
# NOTE: When using memoization (via lru_cache), the cache is
# not automatically shared across multiple processes. Each 
# process will have its own memory space and its own cache.
# So there's less of a benefit in multi-processing for memoization
# if each process only handles one or few calls. For repeated calls
# in the same process, memoization helps drastically.
@measure_time
def multi_process_fibonacci_naive(numbers):
    """
    Computes naive Fibonacci for a list of numbers using multi-processing.
    """
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(fibonacci_naive, numbers))
    return results

@measure_time
def multi_process_fibonacci_memo(numbers):
    """
    Computes memoized Fibonacci for a list of numbers using multi-processing.
    However, since processes do not share state, each process must
    build its own cache. This is still CPU-bound, but might show improvements
    if each process handles multiple calls.
    """
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(fibonacci_memo, numbers))
    return results

# --------------------------------------------------------------
# Main runner
# --------------------------------------------------------------
def main():
    fib_numbers = [35, 36, 37, 38]

    print("=== Multi-Threading with Naive Fibonacci ===")
    thread_results_naive = multi_threaded_fibonacci_naive(fib_numbers)
    print("Thread Results (Naive):", thread_results_naive)

    print("\n=== Multi-Threading with Memoized Fibonacci ===")
    thread_results_memo = multi_threaded_fibonacci_memo(fib_numbers)
    print("Thread Results (Memo):", thread_results_memo)

    print("\n=== Multi-Processing with Naive Fibonacci ===")
    process_results_naive = multi_process_fibonacci_naive(fib_numbers)
    print("Process Results (Naive):", process_results_naive)

    print("\n=== Multi-Processing with Memoized Fibonacci ===")
    process_results_memo = multi_process_fibonacci_memo(fib_numbers)
    print("Process Results (Memo):", process_results_memo)

if __name__ == "__main__":
    main()

