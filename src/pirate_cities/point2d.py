from dataclasses import dataclass
from typing import Self


@dataclass
class Point2d:
    x: float
    y: float

    def __add__(self, other: Self) -> Self:
        return Point2d(self.x + other.x, self.y + other.y)

    def __iadd__(self, other: Self) -> Self:
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: Self) -> Self:
        return Point2d(self.x - other.x, self.y - other.y)

    def __truediv__(self, other: Self | float) -> Self:
        if isinstance(other, Point2d):
            return Point2d(self.x / other.x, self.y / other.y)
        return Point2d(self.x / other, self.y / other)

    def __mul__(self, other: Self | float) -> Self:
        if isinstance(other, Point2d):
            return Point2d(self.x * other.x, self.y * other.y)
        return Point2d(self.x * other, self.y * other)

    def __rmul__(self, other: Self | float) -> Self:
        if isinstance(other, Point2d):
            return Point2d(self.x * other.x, self.y * other.y)
        return Point2d(self.x * other, self.y * other)

    def as_int(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    def distance_to(self, other: Self) -> float:
        """Compute the Euclidean distance (norm) to another Point2d."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
