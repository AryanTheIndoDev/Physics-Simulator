import pygame as pg
from pygame import Surface, Rect, Vector2

import constants as c
import colors
from smoothFloat import SmoothFloat
from enums import Easing

# Overlay
class UI:
    def __init__(self, width: int, height: int) -> None:
        #region - Overlay
        self.surf: Surface = Surface((width, height), pg.SRCALPHA)
        self.top: SmoothFloat = SmoothFloat(-self.surf.height)
        self.rect: Rect = self.surf.get_rect()

        # fill
        rect: Rect = self.surf.get_rect()
        borderRadius: float = self.surf.height // 2
        pg.draw.rect(self.surf, colors.SOFTGREY, rect,
                     border_bottom_left_radius = borderRadius,
                     border_bottom_right_radius = borderRadius,
                )
        #endregion

        # state
        self.hovered: bool = False
        self._active: bool = False

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool):
        if not self.top.active:
            if value:
                self.activate()
            else:
                self.deactivate()

            self._active = value

    def update(self, mousePos: Vector2):
        self.top.update()

        if self.rect.collidepoint(mousePos):
            self.hovered = True
        else:
            self.hovered = False

    def draw(self, screen: Surface):
        self.rect.topleft = ((screen.width // 2) - (self.surf.width // 2), self.top.value)

        if self.hovered: 
            self.surf.set_alpha(200)
        else: 
            self.surf.set_alpha(100)

        screen.blit(self.surf, self.rect)

    def activate(self):
        self.top.setTarget(0, c.ANIMATIONFRAMES, easing = Easing.EaseOut)

    def deactivate(self):
        self.top.setTarget(-self.surf.height, c.ANIMATIONFRAMES, easing = Easing.EaseIn)

    def checkCollision(self, point: Vector2):
        if self.rect.collidepoint(point):
            return True
        else:
            return False

