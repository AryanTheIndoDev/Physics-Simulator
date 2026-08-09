import pygame as pg
from pygame import Surface, Color, Vector2

class Preview:
    def __init__(self, pos: Vector2, color: Color) -> None:
        self.pos: Vector2 = pos
        self.color: Color = color

        self._minRadius: int = 10
        self._radius: int = self._minRadius

    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value: int):
        self._radius = max(self._minRadius, value)
    
    def draw(self, screen: Surface):
        pg.draw.circle(screen, "black", self.pos, self.radius)
        pg.draw.circle(screen, self.color, self.pos, self.radius - 2)
            