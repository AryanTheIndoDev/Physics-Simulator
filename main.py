import pygame as pg
from pygame import Surface, Clock, Vector2, Color

from world import World
from ball import Ball
from hud import Hud
from preview import Preview
from ui import UI
from enums import MouseMode
from images import svgs
from context import ct

import colors
import constants as c

# Type Hints Declaration
type Point = tuple[int, int]

# Pygame Initialization
pg.init()

# Titling
pg.display.set_caption("Ball Studios")

# Iconing
icon: Surface = Surface((32, 32), pg.SRCALPHA)
pg.draw.circle(icon, colors.RED, (icon.get_width() // 2, icon.get_height() // 2), icon.get_width() // 2)
pg.draw.circle(icon, colors.BALLBORDER, (icon.get_width() // 2, icon.get_height() // 2), icon.get_width() // 2, width = 2)

pg.display.set_icon(icon)

# App State
class AppState:
    def __init__(self) -> None:
        #region - Pygame stuff
        self.width: int = c.STARTWINDOWWIDTH
        self.height: int = c.STARTWINDOWHEIGHT

        self.screen: Surface = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)
        self.clock: Clock = Clock()
        #endregion

        #region - Mouse state
        self.mousePos: Vector2 = Vector2()
        self.previousMousePos: Vector2 = Vector2()
        self.mouseMovement: Vector2 = Vector2()

        self.mouseJustPressed: tuple = pg.mouse.get_just_pressed()
        self.mousePressed: tuple = pg.mouse.get_pressed()
        self.mouseJustReleased: tuple = pg.mouse.get_just_released()
        #endregion

        #region - Keyboard state
        self.keyJustPresses = pg.key.get_just_pressed()
        #endregion

        #region - miscellaneous
        # Options
        self.mode: MouseMode = MouseMode.SummonVariable

        # UI
        self.ui: UI = UI()

        # HUD
        self.hud: Hud = Hud()

        # Time Controls
        self.paused: bool = False

        # Svgs
        svgs.load()
        #endregion

        #region - World
        self.world: World[Ball] = World()

        self.inPreview: bool = False
        self.preview: Preview = Preview(self.mousePos, ct.ballColor)
        #endregion

        #region - Mainloop variables
        self.running: bool = True

        self.targetFPS: int = c.DEFAULTTARGETFPS
        self.dt: float = 1 / self.targetFPS
        #endregion

    # App Methods
    def update(self) -> None:
        dt = self.dt * ct.playSpeed.value

        # Mouse
        self.mouseMovement: Vector2 = getMouseMovement(self)

        self.mousePressed: tuple = pg.mouse.get_pressed()
        self.mouseJustPressed: tuple = pg.mouse.get_just_pressed()
        self.mouseJustReleased: tuple = pg.mouse.get_just_released()

        # Keyboard
        self.keyJustPresses = pg.key.get_just_pressed()

        # UI
        self.ui.update(self.mousePos, self.mouseJustPressed, self.mouseJustReleased, self)

        if not self.paused:
            # Ball dragging
            for ball in self.world.balls.members:
                if ball.held:
                    if dt != 0:
                        ball.v = self.mouseMovement / dt
            
            # Modes:---
            # Add new balls (Variable)
            if self.mode == MouseMode.SummonVariable:
                if self.mouseJustPressed[2]:
                    for ball in self.world.balls.members:
                        if ball.collidesWith(self.mousePos):
                            break
                    else:
                        if self.canSummon():
                            self.preview: Preview = Preview(self.mousePos, ct.ballColor)
                            self.inPreview: bool = True
                        else:
                            self.hud.resetTimer()
                
                if self.inPreview:
                    if self.mousePressed[2]:
                        self.preview.radius = min(int(self.preview.pos.distance_to(self.mousePos)),
                                                int(min(self.width, self.height) * c.MAXPREVIEWSIZERATIO))
                    
                    else:
                        summonBall(self.preview.pos, self.preview.radius, self.preview.color)
                        self.inPreview: bool = False
            elif self.inPreview:
                self.inPreview = False
            # Add new balls (Fixed)
            if self.mode == MouseMode.SummonFixed:
                if self.mouseJustPressed[2]:
                    for ball in self.world.balls.members:
                        if ball.collidesWith(self.mousePos):
                            break
                    else:
                        if self.canSummon():
                            summonBall(self.mousePos, int(ct.ballRadius.value), ct.ballColor)
                        else:
                            self.hud.resetTimer()
            # Remove balls
            if self.mode == MouseMode.Kill:
                if self.mousePressed[2]:
                    for index in range(len(self.world.balls.members) - 1, -1, -1):
                        curBall: Ball = self.world.balls.members[index]
                        if curBall.collidesWith(self.mousePos):
                            self.world.balls.kill(curBall)
                            break  
            # ---------

            # World Update
            self.world.update(self.width, self.height, dt, self.mouseJustPressed,
                            self.mousePressed, self.mousePos, self.keyJustPresses)
        
        # FBD
        if self.keyJustPresses[pg.K_f]:
            ct.update({"showVectors": not ct.showVectors})
        # Pausing
        if self.keyJustPresses[pg.K_SPACE]:
            self.paused = not self.paused
            self.ui.overlay.active = True
        # Overlay
        if self.keyJustPresses[pg.K_TAB]:
            self.ui.overlay.active = not self.ui.overlay.active
        
        # Quit
        if pg.key.get_just_pressed()[pg.K_ESCAPE]:
            self.quit()

    def draw(self) -> None:
        # Background
        self.screen.fill(ct.bgColor)
        
        # Draw World
        self.world.draw(self.screen)

        # Draw Preview
        if self.inPreview:
            self.preview.draw(self.screen)

        # HUD
        if ct.showHUD:
            self.hud.draw(self.screen, self.world, self.mode, self.dt)

        self.ui.draw(self.screen)

        # Mouse Hints
        self.drawMouseMode(self.mousePos)

    def cycleMode(self, direction: int) -> None:
        app.mode = app.mode.cycleMode(-direction)

    def canSummon(self) -> bool:
        return not ct.limitBalls or (len(self.world.balls) < int(ct.maxBalls.value))

    def drawMouseMode(self, mousePos: Vector2) -> None:
        # Draw only when mouse on Window
        if pg.mouse.get_focused():
            if self.mode == MouseMode.SummonVariable:
                ...
            elif self.mode == MouseMode.SummonFixed:
                pg.draw.circle(self.screen, ct.ballColor, mousePos + Vector2(8, -2), 4)
                pg.draw.circle(self.screen, colors.BALLBORDER, mousePos + Vector2(8, -2), 4, 1)

            elif self.mode == MouseMode.Kill:
                pg.draw.line(self.screen, colors.BLACK, mousePos + Vector2(5, -5), mousePos + Vector2(11, 1), 3)
                pg.draw.line(self.screen, colors.BLACK, mousePos + Vector2(5, 1), mousePos + Vector2(11, -5), 3)
        
                pg.draw.line(self.screen, colors.SOLIDRED, mousePos + Vector2(5, -5), mousePos + Vector2(11, 1), 2)
                pg.draw.line(self.screen, colors.SOLIDRED, mousePos + Vector2(5, 1), mousePos + Vector2(11, -5), 2)

    def clearBalls(self) -> None:
        self.world.balls.kill()

    def openSettings(self) -> None:
        self.ui.settings.activate(self)

    def quit(self) -> None:
        self.running: bool = False

app = AppState()

# Helper functions

def getMouseMovement(app: AppState) -> Vector2:
    app.previousMousePos = app.mousePos
    app.mousePos = Vector2(pg.mouse.get_pos())

    return app.mousePos - app.previousMousePos

def summonBall(pos: Vector2, radius: int, color: Color) -> None:
    if app.canSummon():
        app.world.balls.add(Ball(pos, radius, color))

def windowResize(app: AppState, newDimensions: Point) -> None:
    # new dimensions
    newWidth, newHeight = newDimensions
    
    # clamping new dimensions
    newWidth = max(newWidth, c.MINWINDOWWIDTH) 
    newHeight = max(newHeight, c.MINWINDOWHEIGHT)

    # remapping ball pos
    app.world.balls.remap((app.width, app.height), (newWidth, newHeight))

    # updating dimensions
    app.width = newWidth
    app.height = newHeight

    # resize
    if (newWidth, newHeight) != newDimensions:
        app.screen = pg.display.set_mode((app.width, app.height), pg.RESIZABLE)

# Mainloop
while app.running:
    for event in pg.event.get():
        # Resizing
        if event.type == pg.VIDEORESIZE:
            windowResize(app, event.size)
        # Scroll
        if event.type == pg.MOUSEWHEEL:
            app.cycleMode(event.y)
        # Quit
        if event.type == pg.QUIT:
            app.quit()

    # delta time
    app.dt = app.clock.tick(app.targetFPS) / 1000

    # Tasks
    app.draw()
    app.update()

    pg.display.update()

pg.quit()

