from pygame import Surface, Vector2
from typing import Any, TypeVar, Generic, Protocol

# Type Hints Declaration
type Point = tuple[int, int]

# Placeholder
class PlaceHolder(Protocol):
    def draw(self, screen: Surface, fbdMode: bool): ...
    def update(self, width: int, height: int, world: Any, dt: float, mousePos: Vector2): ...
    def remap(self, originalDimensions: Point, newDimensions: Point): ...

# Generic Type
T = TypeVar("T", bound = PlaceHolder)

# Group class
class Group(Generic[T]):
    def __init__(self) -> None:
        self.members: list[T] = []
    
    def add(self, member: T) -> None:
        self.members.append(member)
    
    def kill(self, member: T) -> None:
        self.members.remove(member)
    
    def draw(self, screen: Surface, fbdMode: bool) -> None:
        for member in self.members:
            member.draw(screen, fbdMode)
    
    def update(self, width: int, height: int, world: Any, dt: float, mousePos: Vector2) -> None:
        for member in self.members:
            member.update(width, height, world, dt, mousePos)

    def remap(self, originalDimensions: Point, newDimensions: Point):
        for member in self.members:
            member.remap(originalDimensions, newDimensions)
    
    def __len__(self):
        return len(self.members)