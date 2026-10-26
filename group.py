from pygame import Surface, Vector2
from typing import Any, TypeVar, Generic, Protocol

# Type Hints Declaration
type Point = tuple[int, int]

# Placeholder
class PlaceHolder(Protocol):
    def draw(self, screen: Surface): ...
    def update(self, width: int, height: int, dt: float, mousePos: Vector2): ...
    def remap(self, originalDimensions: Point, newDimensions: Point): ...

# Generic Type
T = TypeVar("T", bound = PlaceHolder)

# Group class
class Group(Generic[T]):
    def __init__(self) -> None:
        self.members: list[T] = []
    
    def add(self, member: T) -> None:
        self.members.append(member)
    
    def kill(self, member: T | str = "all") -> None:
        if isinstance(member, str):
            self.members: list[T] = []
        else:
            self.members.remove(member)
    
    def draw(self, screen: Surface) -> None:
        for member in self.members:
            member.draw(screen)
    
    def update(self, width: int, height: int, dt: float, mousePos: Vector2) -> None:
        for member in self.members:
            member.update(width, height, dt, mousePos)

    def remap(self, originalDimensions: Point, newDimensions: Point):
        for member in self.members:
            member.remap(originalDimensions, newDimensions)
    
    def __len__(self):
        return len(self.members)