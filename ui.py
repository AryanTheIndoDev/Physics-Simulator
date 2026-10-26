import pygame as pg
from pygame import Surface, Rect, Vector2, Color, Font
from typing import Callable, Protocol

import constants as c
import colors
from floats import SmoothFloat
from enums import Easing
from arrow import drawArrow
from images import svgs
from context import ct

pg.font.init()

class PlaceHolder(Protocol):
    paused: bool

    def clearBalls(self) -> None: ...
    def openSettings(self) -> None: ...

def empty(*args):
    ...

# Icons
def playIcon(source: Surface, center: Vector2, sideLength: int, color: Color, dir: int):
    r = sideLength // 2
    leftTop = center + Vector2(-r / 3, -r / 2)
    leftBottom = center + Vector2(-r / 3, r / 2)
    right = center + Vector2(r / 3, 0)
    
    pg.draw.polygon(source, color, (leftTop, leftBottom, right))

def pauseIcon(source: Surface, center: Vector2, sideLength: int, color: Color, dir: int):
    r = sideLength // 2
    leftRect = Rect(center + Vector2(-r / 2, -3 * r / 5), Vector2(r / 4, 6 * r / 5))
    rightRect = Rect(center + Vector2(r / 4, -3 * r / 5), Vector2(r / 4, 6 * r / 5))

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
    
    pg.draw.circle(source, colors.BALLBORDER, center + Vector2(1, 0), r / 2)
    pg.draw.circle(source, color, center + Vector2(1, 0), r / 2)

    pg.draw.line(source, colors.RED, center + Vector2(-r / 2, -r / 2), center + Vector2(r / 2, r / 2), 2)
    pg.draw.line(source, colors.RED, center + Vector2(-r / 2, r / 2), center + Vector2(r / 2, -r / 2), 2)

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
    pg.draw.rect(source, colors.HAZYWHITE, rect, border_radius = 5)

    drawArrow(source, center + Vector2(-r / 2, -r / 2), center + Vector2(r / 2, -r / 2),
              colors.YELLOW, 3, 5, 30, True
            )
    drawArrow(source, center + Vector2(-r / 2, -r / 2), center + Vector2(-r / 2, r / 2),
              colors.BRIGHTPURPLE, 3, 5, 30, True
            )

def settingsIcon(source: Surface, center: Vector2, sideLength: int, color: Color, dir: int):
    r = sideLength // 2

    icon = pg.transform.scale(svgs.settings_surf, (3 * r / 2, 3 * r / 2))
    rect = icon.get_rect(center = center)

    source.blit(icon, rect)

def hideOverlayIcon(source: Surface, center: Vector2, sideLength: int, color: Color, dir: int):
    r = sideLength // 2

    left = center + Vector2(-r / 2, dir * -r / 4)
    middle = center + Vector2(0, dir * r / 4)
    right = center + Vector2(r / 2, dir * -r / 4)

    pg.draw.polygon(source, color, (left, middle, right))

# Button Functions
def playPause(app: PlaceHolder):
    app.paused = not app.paused

def slowDown(app: PlaceHolder):
    ct.update({"playSpeed": ct.playSpeed.value - 0.2})

def speedUp(app: PlaceHolder):
    ct.update({"playSpeed": ct.playSpeed.value + 0.2})

def ballClear(app: PlaceHolder):
    app.clearBalls()

def showVectors(app: PlaceHolder):
    ct.update({"showVectors": not ct.showVectors})

def openSettings(app: PlaceHolder):
    app.openSettings()

def hideOverlay(app):
    app.ui.overlay.active = False

# Elements
class Button:
    def __init__(self, width: int, height: int, icon: Callable, action: Callable, dir: int,
                  hasStates: bool = False, activeIcon: Callable = empty, stateGetter: Callable = empty) -> None:
        self.width: int = width
        self.height: int = height

        self.rect: Rect = Rect()

        self.icon: Callable = icon
        self.dir: int = dir

        self.hovered: bool = False
        self.pressed: bool = False
        self.hasStates: bool = hasStates
        self.action: Callable = action

        if self.hasStates:
            self.active: bool = False
            self.stateGetter: Callable = stateGetter
            self.dormantIcon: Callable = icon
            self.activeIcon: Callable = activeIcon
        
    def draw(self, source: Surface, center: Vector2):
        self.surf: Surface = Surface((self.width, self.height), pg.SRCALPHA)
        self.rect: Rect = self.surf.get_rect(center = center)

        if self.hovered:
            rect = self.surf.get_rect()
            rect.center = Vector2(self.surf.width // 2, self.surf.height // 2)
            pg.draw.rect(self.surf, colors.FAINTWHITE, rect, border_radius = 5)

        self.icon(self.surf, Vector2(self.surf.width // 2, self.surf.height // 2), self.surf.width, colors.WHITE, self.dir)

        source.blit(self.surf, self.rect)

    def update(self, localMousePos: Vector2, mouseJustPressed: tuple, mouseJustReleased: tuple, app: PlaceHolder):
        if self.rect.collidepoint(localMousePos):
            self.hovered = True
            if mouseJustPressed[0]:
                self.pressed = True
            if mouseJustReleased[0]:
                if self.pressed:
                    self.action(app)

        else:
            self.hovered = False

        # resetting pressed state
        if mouseJustReleased[0]:
            self.pressed = False

        # icon changing for state buttons
        if self.hasStates:
            self.active = self.stateGetter(app)
            if self.active:
                self.icon = self.activeIcon
            else:
                self.icon = self.dormantIcon
            
class Label:
    def __init__(self, width: int, height: int, text: str, font: Font):
        self.width: int = width
        self.height: int = height

        self.surf: Surface = Surface((width, height), pg.SRCALPHA)
        self.rect: Rect = self.surf.get_rect()

        self.text: str = text
        self.font: Font = font


    def draw(self, source: Surface, center: Vector2):
        self.surf.fill(colors.TRANSPARENT)
        self.rect.center = center

        surf: Surface = self.font.render(self.text, True, colors.WHITE)
        rect: Rect = surf.get_rect(center = (self.surf.width // 2, self.surf.height // 2))
        self.surf.blit(surf, rect)

        source.blit(self.surf, self.rect)

    def update(self, text: str):
        self.text: str = text

# Overlay
class Overlay:
    def __init__(self, width: int, height: int) -> None:
        #region - overlay
        self.width: int = width
        self.height: int = height

        self.surf: Surface = Surface((width, height), pg.SRCALPHA)
        self.top: SmoothFloat = SmoothFloat(-self.surf.height)

        self.rect: Rect = self.surf.get_rect()
        #endregion

        #region - state
        self.localMousePos: Vector2 = Vector2()

        self._active: bool = False
        #endregion

        # region - elements
        s = c.BUTTONSIDELENGTH

        playButton = Button(s, s, playIcon, playPause, 1, True, pauseIcon, lambda app: app.paused)
        slowDownButton = Button(s, s, speedIcon, slowDown, -1)
        speedUpButton = Button(s, s, speedIcon, speedUp, 1)
        ballClearButton = Button(s, s, ballClearIcon, ballClear, 1)
        showVectorsButton = Button(s, s, showVectorsOffIcon, showVectors, 1, True, showVectorsOnIcon, lambda app: ct.showVectors)
        settingsButton = Button(s, s, settingsIcon, openSettings, 1)
        hideOverlayButton = Button(s, s, hideOverlayIcon, hideOverlay, -1)

        speedLabel = Label(s, s, "", pg.font.SysFont("Cambria Math", 18))

        self.elements: list[Button | Label] = [playButton, slowDownButton, speedLabel, speedUpButton,
                                               ballClearButton, showVectorsButton, settingsButton,
                                               hideOverlayButton]
        #endregion

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

    def update(self, mousePos: Vector2, mouseJustPressed: tuple, mouseJustReleased: tuple, app: PlaceHolder):
        # mouse pos
        self.localMousePos = mousePos - self.rect.topleft

        # smooth floats
        self.top.update()

        # elements
        for element in self.elements:
            if isinstance(element, Button):
                element.update(self.localMousePos, mouseJustPressed, mouseJustReleased, app)
            elif isinstance(element, Label):
                element.update(f"x{ct.playSpeed.value}")
        
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

        # drawing elements
        y = self.surf.height // 2

        xGap = c.ELEMENTGAP
        widths = [element.width for element in self.elements]
        totalWidth = sum(widths, (len(self.elements) - 1) * xGap)

        xOffset = (self.surf.width - totalWidth) / 2

        currentx = xOffset

        for index, element in enumerate(self.elements):
            # left to middle
            currentx += element.width // 2

            # draw
            element.draw(self.surf, Vector2(currentx, y))

            # middle to right
            currentx += element.width // 2

            # right to next left after gap
            if index != len(self.elements) - 1:
                currentx += xGap

        screen.blit(self.surf, self.rect)

    def activate(self):
        self.top.setTarget(0, c.ANIMATIONFRAMES, easing = Easing.EaseOut)

    def deactivate(self):
        self.top.setTarget(-self.surf.height, c.ANIMATIONFRAMES, easing = Easing.EaseIn)
# Settings
class Settings:
    def __init__(self) -> None:
        self.minWidthMargin: int = 20
        self.minHeightMargin: int = 20

        self.maxWidth: int = 500
        self.maxHeight: int = 400
        
        self.localMousePos: Vector2 = Vector2()
        self._active: bool = False

    def activate(self, app: PlaceHolder):
        ...

# UI
class UI:
    def __init__(self) -> None:
        self.overlay = Overlay(c.OVERLAYWIDTH, c.OVERLAYHEIGHT)
        self.settings = Settings()

    def update(self, mousePos: Vector2, mouseJustPressed: tuple, mouseJustReleased: tuple, app: PlaceHolder):
        self.overlay.update(mousePos, mouseJustPressed, mouseJustReleased, app)

    def draw(self, screen: Surface):
        self.overlay.draw(screen)