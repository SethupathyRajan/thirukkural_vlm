"""
Benchmarking utilities for measuring time and memory.
"""

import time
import tracemalloc
from typing import Callable, Any, Tuple
from contextlib import contextmanager

@contextmanager
def timer():
    """
    Context manager to measure elapsed time.
    """
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start
    end = time.perf_counter()

@contextmanager
def memory_trace():
    """
    Context manager to measure memory usage.
    """
    tracemalloc.start()
    yield
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current, peak

def benchmark_function(func: Callable, *args, **kwargs) -> Tuple[Any, float]:
    """
    Benchmark a function and return its result and execution time.

    Args:
        func: The function to benchmark.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        Tuple of (result, elapsed_time_in_seconds).
    """
    with timer() as t:
        result = func(*args, **kwargs)
    elapsed = t()
    return result, elapsed

def benchmark_function_with_memory(func: Callable, *args, **kwargs) -> Tuple[Any, float, int, int]:
    """
    Benchmark a function and return its result, execution time, and memory usage.

    Args:
        func: The function to benchmark.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        Tuple of (result, elapsed_time_in_seconds, current_memory, peak_memory).
    """
    tracemalloc.start()
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = end - start
    return result, elapsed, current, peak