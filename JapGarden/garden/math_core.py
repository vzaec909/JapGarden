"""Математическая основа: числа Фибоначчи, золотое сечение, спирали."""
import math

# Золотое сечение
PHI = (1 + math.sqrt(5)) / 2
# Золотой угол ≈ 137.507° в радианах
GOLDEN_ANGLE = 2 * math.pi / (PHI * PHI)


def fibonacci(n):
    """Первые n чисел Фибоначчи."""
    fib = [1, 1]
    while len(fib) < n:
        fib.append(fib[-1] + fib[-2])
    return fib[:n]


def is_fibonacci(num):
    """Является ли число числом Фибоначчи."""
    if num < 1:
        return False
    a, b = 1, 1
    while b < num:
        a, b = b, a + b
    return b == num or num == 1


def nearest_fibonacci(num):
    """Ближайшее число Фибоначчи к заданному."""
    if num <= 1:
        return 1
    a, b = 1, 1
    while b < num:
        a, b = b, a + b
    return a if abs(a - num) <= abs(b - num) else b


def golden_spiral_points(n, radius=1.0, rotation=0.0):
    """
    Точки на золотой спирали внутри группы.
    Возвращает список (x, y, r).
    """
    points = []
    for i in range(n):
        r = radius * (PHI ** (i / 3.0)) / (PHI ** (max(n - 1, 1) / 3.0))
        theta = i * GOLDEN_ANGLE + rotation
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        points.append((x, y, r))
    return points