import pygame as pg
from pygame import Surface, Font, Rect

from gravity import GravityMode

from typing import TypeVar, Generic, Protocol

class PlaceHolder(Protocol):
    balls: list
    gravityMode: GravityMode
    bounce: float

T = TypeVar("T", bound = PlaceHolder)

class Hud(Generic[T]):
    def __init__(self) -> None:
        self.font: Font = pg.font.SysFont("consolas", 20, bold = True)
        self.color: str = "white"
    
    def draw(self, screen: Surface, world: T, mouseMode: str, fbdMode: bool):
        # Debug Texts
        ball_text: Surface = self.font.render(f"balls   : {len(world.balls)}", True, self.color)
        gravity_text: Surface = self.font.render(f"gravity : {world.gravityMode.name.lower()}", True, self.color)
        mouse_text: Surface = self.font.render(f"mode    : {mouseMode}", True, self.color)
        bounce_text: Surface = self.font.render(f"bounce  : {world.bounce}", True, self.color)
        fbd_text: Surface = self.font.render(f"fbd mode: {str(fbdMode).lower()}", True, self.color)

        # blitting
        screen.blit(mouse_text, (0, 0))
        screen.blit(ball_text, (0, 20))
        screen.blit(bounce_text, (0, 40))
        screen.blit(gravity_text, (0, 60))
        screen.blit(fbd_text, (0, 80))

        