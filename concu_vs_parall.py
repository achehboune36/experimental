"""
Experimental script to compair multi-threading and multi-processing in a not very thorough way [fibb]
"""

import time
import math
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

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

def fibonacci(n):
    """
    Simple recursive Fibonacci function (CPU-bound).
    For larger n, consider more efficient approaches, but this is fine for a demo.
    """
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

@measure_time
def multi_threaded_fibonacci(numbers):
    """
    Computes Fibonacci for a list of numbers using multi-threading.
    Each number is processed by a thread in the pool.
    """
    results = []
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(fibonacci, numbers))
    return results

@measure_time
def multi_process_fibonacci(numbers):
    """
    Computes Fibonacci for a list of numbers using multi-processing.
    Each number is processed by a separate process in the pool.
    This can circumvent the GIL for CPU-bound tasks.
    """
    results = []
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(fibonacci, numbers))
    return results

def main():
    fib_numbers = [35, 36, 37, 38]  
    
    print("=== Multi-Threading Demo ===")
    thread_results = multi_threaded_fibonacci(fib_numbers)
    print("Thread Results:", thread_results)

    print("\n=== Multi-Processing Demo ===")
    process_results = multi_process_fibonacci(fib_numbers)
    print("Process Results:", process_results)

if __name__ == "__main__":
    main()

