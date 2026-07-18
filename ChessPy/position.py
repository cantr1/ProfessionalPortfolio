"""Class for holding x / y coords for pieces"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    x_pos: int
    y_pos: int
