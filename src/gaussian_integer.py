"""Exact Gaussian-integer amplitudes; real values stay ordinary Python ints."""

from dataclasses import dataclass
from math import gcd


def parts(value):
    if type(value) is int:
        return value, 0
    if isinstance(value, Gaussian):
        return value.real, value.imag
    raise TypeError("Expected an integer or Gaussian integer")


def gaussian(real, imag=0):
    return Gaussian(real, imag) if imag else real


@dataclass(frozen=True)
class Gaussian:
    real: int
    imag: int

    def __post_init__(self):
        if type(self.real) is not int or type(self.imag) is not int:
            raise TypeError("Gaussian components must be Python integers")

    def __add__(self, other):
        a, b = parts(other)
        return gaussian(self.real+a, self.imag+b)

    __radd__ = __add__

    def __neg__(self):
        return gaussian(-self.real, -self.imag)

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        a, b = parts(other)
        return gaussian(self.real*a-self.imag*b, self.real*b+self.imag*a)

    __rmul__ = __mul__

    def __floordiv__(self, divisor):
        if type(divisor) is not int or self.real % divisor or self.imag % divisor:
            raise ArithmeticError("Gaussian integer division must be exact")
        return gaussian(self.real//divisor, self.imag//divisor)

    def __bool__(self):
        return bool(self.real or self.imag)

    def __str__(self):
        return f"{self.real}{'+' if self.imag >= 0 else ''}{self.imag}i"


def conjugate(value):
    return value if type(value) is int else gaussian(value.real, -value.imag)


def abs_squared(value):
    return value*value if type(value) is int else value.real*value.real+value.imag*value.imag


def real_part(value):
    return value if type(value) is int else value.real


def imag_part(value):
    return 0 if type(value) is int else value.imag


def phase(value, power):
    a, b = parts(value)
    return (value, gaussian(-b, a), -value, gaussian(b, -a))[power % 4]


def content(values):
    result = 0
    for value in values:
        a, b = parts(value)
        result = gcd(result, gcd(abs(a), abs(b)))
    return result


def exact_divide(left, right):
    a, b = parts(left*conjugate(right))
    d = abs_squared(right)
    if not d or a % d or b % d:
        raise ArithmeticError("Inexact Gaussian division")
    return gaussian(a//d, b//d)


def gaussian_gcd(left, right):
    while right:
        a, b = parts(left*conjugate(right))
        d = abs_squared(right)
        # Round rational coordinates to nearest integer, avoiding floats.
        q = gaussian((2*a+d)//(2*d), (2*b+d)//(2*d))
        left, right = right, left-q*right
    return left


def to_complex(value):
    a, b = parts(value)
    return complex(a, b)
