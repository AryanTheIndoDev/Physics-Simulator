from enum import Enum, auto
from pygame import Vector2

# Declaring Enums
class MouseMode(Enum):
    SummonVariable = auto()
    SummonFixed = auto()
    Kill = auto()

    def cycleMode(self, dir: int):
        members: list = list(self.__class__)
        index: int = members.index(self)

        return members[(index + dir) % len(MouseMode)]

class GravityMode(Enum):
    Up = Vector2(0, -1)
    Down = Vector2(0, 1)
    Left = Vector2(-1, 0)
    Right = Vector2(1, 0)
    Mouse = Vector2(0, 0)

class Easing(Enum):
    EaseIn = auto()
    EaseOut = auto()
    EaseInOut = auto()
