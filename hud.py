import pygame as pg
from pygame import Surface, Font

from enums import GravityMode, MouseMode
from context import ct

from typing import TypeVar, Generic, Protocol

class PlaceHolder(Protocol):
    balls: list

T = TypeVar("T", bound = PlaceHolder)

class Hud(Generic[T]):
    def __init__(self) -> None:
        self.font: Font = pg.font.SysFont("consolas", 20, bold = True)
        self.color: str = "white"

        self.timer: float = 0.0

    def resetTimer(self):
        if self.timer == 0.0:
            self.timer: float = 0.4

    def draw(self, screen: Surface, world: T, mouseMode: MouseMode, dt: float):
        # Update timer
        if self.timer > 0.0:
            self.timer -= dt

            # ball text fill
            if 0.3 <= self.timer <= 0.4:
                ballTextFill = "red"
            elif 0.1 <= self.timer <= 0.2:
                ballTextFill = "red"
            else:
                ballTextFill = self.color
        else:
            self.timer = 0.0
            ballTextFill = self.color

        # Debug Texts
        arrows = {
            GravityMode.Up: "↑",
            GravityMode.Left: "←",
            GravityMode.Down: "↓",
            GravityMode.Right: "→",
            GravityMode.Mouse: "○",
        }
        mouses = {
            MouseMode.SummonVariable: "+ var",
            MouseMode.SummonFixed: "+ fix",
            MouseMode.Kill: "- kill",
        }

        arrow = arrows[ct.gravityMode]
        mouse = mouses[mouseMode]

        if ct.limitBalls:
            ballText = f"[ ● {len(world.balls)} / {int(ct.maxBalls.value)} ] "
        else:
            ballText = f"[ ● {len(world.balls)} ] "

        restText = f"[ {arrow} {ct.gravity.value} ] [ {mouse} ]"
        
        ballSurf = self.font.render(ballText, True, ballTextFill)
        restSurf = self.font.render(restText, True, self.color)

        ballRect = ballSurf.get_rect(bottomleft = (0, screen.height))
        restRect = restSurf.get_rect(bottomleft = (ballRect.w, screen.height))

        # blitting
        screen.blit(ballSurf, ballRect)
        screen.blit(restSurf, restRect)
        