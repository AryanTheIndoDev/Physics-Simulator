from enum import Enum
from pygame import Vector2

# Declaring Enums
class GravityMode(Enum):
    Up = Vector2(0, -1)
    Down = Vector2(0, 1)
    Left = Vector2(-1, 0)
    Right = Vector2(1, 0)
    Mouse = Vector2(0, 0)

