from functools import cache


@cache
def fib(n: int) -> int:
    """Return the nth Fibonacci number using an iterative approach."""
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b

    return a


for i in range(100):
    print(f"Index: {i}: {fib(i)}")
