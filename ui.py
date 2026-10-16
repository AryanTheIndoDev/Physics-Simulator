import pygame as pg
from pygame import Surface, Rect, Vector2, Color
from typing import Callable, Protocol, TypeVar

import constants as c
import colors
from floats import SmoothFloat, ClampedFloat
from enums import Easing
from arrow import drawArrow

class PlaceHolder(Protocol):
    paused: bool
    playSpeed: ClampedFloat

    def clearBalls(self) -> None: ...
    def toggleFBD(self) -> bool: ...

# Icons
def playIcon(source: Surface, center: Vector2, sideLength: int, color: Color, dir: int):
    r = sideLength // 2
    leftTop = center + Vector2(-r / 2, -3 * r / 4)
    leftBottom = center + Vector2(-r / 2, 3 * r / 4)
    right = center + Vector2(r / 2, 0)
    
    pg.draw.polygon(source, color, (leftTop, leftBottom, right))

def pauseIcon(source: Surface, center: Vector2, sideLength: int, color: Color, dir: int):
    r = sideLength // 2
    leftRect = Rect(center + Vector2(-3 * r / 4, -3 * r / 4), Vector2(r / 2, 3 * r / 2))
    rightRect = Rect(center + Vector2(r / 4, -3 * r / 4), Vector2(r / 2, 3 * r / 2))

    pg.draw.rect(source, color, leftRect)
    pg.draw.rect(source, color, rightRect)

def speedIcon(source: Surface, center: Vector2, sideLength: int, color: Color, dir: int):
    r = sideLength // 2
    
    outTop = center + Vector2(dir, -r / 2)
    outMiddle = center + Vector2(dir * r / 2, 0)
    outBottom = center + Vector2(dir, r / 2)

    inTop = center + Vector2(dir * -r / 2, -r / 2)
    inMiddle = center + Vector2(-dir , 0)
    inBottom = center + Vector2(dir * -r / 2, r / 2)

    pg.draw.polygon(source, color, (outTop, outMiddle, outBottom))
    pg.draw.polygon(source, color, (inTop, inMiddle, inBottom))

def ballClearIcon(source: Surface, center: Vector2, sideLength: int, color: Color, dir: int):
    r = sideLength // 2

    pg.draw.circle(source, colors.BALLBORDER, center, r / 2)
    pg.draw.circle(source, color, center, r / 2)

    pg.draw.line(source, colors.RED, center + Vector2(-r / 2, -r / 2), center + Vector2(r / 2, r / 2))
    pg.draw.line(source, colors.RED, center + Vector2(-r / 2, r / 2), center + Vector2(r / 2, -r / 2))

def showVectorsOffIcon(source: Surface, center: Vector2, sideLength: int, color: Color, dir: int):
    r = sideLength // 2

    drawArrow(source, center + Vector2(-r / 2, -r / 2), center + Vector2(r / 2, -r / 2),
              colors.YELLOW, 3, 5, 30, True
            )
    drawArrow(source, center + Vector2(-r / 2, -r / 2), center + Vector2(-r / 2, r / 2),
              colors.BRIGHTPURPLE, 3, 5, 30, True
            )

def showVectorsOnIcon(source: Surface, center: Vector2, sideLength: int, color: Color, dir: int):
    r = sideLength // 2

    rect = source.get_rect(center = center)
    pg.draw.rect(source, colors.FAINTWHITE, rect)

    drawArrow(source, center + Vector2(-r / 2, -r / 2), center + Vector2(r / 2, -r / 2),
              colors.YELLOW, 3, 5, 30, True
            )
    drawArrow(source, center + Vector2(-r / 2, -r / 2), center + Vector2(-r / 2, r / 2),
              colors.BRIGHTPURPLE, 3, 5, 30, True
            )

def dropDownIcon(source: Surface, center: Vector2, sideLength: int, color: Color, dir: int):
    r = sideLength // 2

    left = center + Vector2(-r / 2, dir * -r / 4)
    middle = center + Vector2(0, dir * r / 4)
    right = center + Vector2(r / 2, dir * -r / 4)

    pg.draw.polygon(source, color, (left, middle, right))

# Button Functions
def playPause(app: PlaceHolder):
    app.paused = not app.paused

def slowDown(app: PlaceHolder):
    app.playSpeed.update(app.playSpeed.value - 0.1)

def speedUp(app: PlaceHolder):
    app.playSpeed.update(app.playSpeed.value + 0.1)

def ballClear(app: PlaceHolder):
    app.clearBalls()

def showVectors(app: PlaceHolder) -> bool:
    return app.toggleFBD()

# Elements
class Button:
    def __init__(self, width: int, height: int, icon: Callable, action: Callable, dir: int,
                  hasStates: bool = False, activeIcon: Callable = lambda x:None, ) -> None:
        self.width: int = width
        self.height: int = height

        self.rect: Rect = Rect()

        self.dir: int = dir

        self.hovered: bool = False
        self.hasStates: bool = hasStates
        self.action: Callable = action

        if self.hasStates:
            self.active: bool = False
            self.dormantIcon: Callable = icon
            self.activeIcon: Callable = activeIcon

        else:
            self.icon: Callable = icon
        
    def draw(self, source: Surface, center: Vector2):
        self.surf: Surface = Surface((self.width, self.height), pg.SRCALPHA)
        self.rect: Rect = self.surf.get_rect(center = center)

        if self.hovered:
            rect = self.surf.get_rect()
            rect.center = Vector2(self.surf.width // 2, self.surf.height // 2)
            pg.draw.rect(self.surf, colors.FAINTWHITE, rect, border_radius = 5)

        self.icon(self.surf, Vector2(self.surf.width // 2, self.surf.height // 2), self.surf.width, colors.WHITE, self.dir)

        source.blit(self.surf, self.rect)

    def update(self, localMousePos: Vector2, mouseJustReleased: tuple, app: PlaceHolder):
        if self.rect.collidepoint(localMousePos):
            self.hovered = True
            if mouseJustReleased[0]:
                if self.hasStates:
                    self.active = self.action(app)
                    if self.active:
                        self.icon = self.activeIcon
                    else:
                        self.icon = self.dormantIcon
                else:
                    self.action(app)
        else:
            self.hovered = False

ballClearButton = Button(32, 32, speedIcon, slowDown, -1)

# Overlay
class UI:
    def __init__(self, width: int, height: int) -> None:
        #region - Overlay
        self.width: int = width
        self.height: int = height

        self.surf: Surface = Surface((width, height), pg.SRCALPHA)
        self.top: SmoothFloat = SmoothFloat(-self.surf.height)

        self.rect: Rect = self.surf.get_rect()

        #endregion

        # state
        self.localMousePos: Vector2 = Vector2()

        self.hovered: bool = False
        self._active: bool = False

        self.elements: list = [ballClearButton]

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool):
        if value != self._active:
            if not self.top.active:
                if value:
                    self.activate()
                else:
                    self.deactivate()

                self._active = value

    def update(self, mousePos: Vector2, mouseJustReleased: tuple, app: PlaceHolder):
        # mouse pos
        self.localMousePos = mousePos - self.rect.topleft

        # smooth floats
        self.top.update()

        # elements
        for element in self.elements:
            if isinstance(element, Button):
                element.update(self.localMousePos, mouseJustReleased, app)
        
        if self.surf.get_rect().collidepoint(self.localMousePos):
            self.hovered = True
        else:
            self.hovered = False


    def draw(self, screen: Surface):
        self.surf: Surface = Surface((self.width, self.height), pg.SRCALPHA)
        self.rect: Rect = self.surf.get_rect(topleft = ((screen.width // 2) - (self.surf.width // 2), self.top.value))

        # fill
        rect: Rect = self.surf.get_rect()
        borderRadius: float = self.surf.height // 2
        pg.draw.rect(self.surf, colors.BLACK, rect,
                     border_bottom_left_radius = borderRadius,
                     border_bottom_right_radius = borderRadius,
                )

        for element in self.elements:
            if isinstance(element, Button):
                element.draw(self.surf, Vector2(self.surf.width // 2, self.surf.height // 2))
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

