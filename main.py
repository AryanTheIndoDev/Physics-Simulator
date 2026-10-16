import pygame as pg
from pygame import Surface, Clock, Vector2, Color

from world import World
from ball import Ball
from hud import Hud
from preview import Preview
from ui import UI
from floats import ClampedFloat

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
        self.modes: list = ["summon (variable)", "summon (fixed)", "kill"]
        self.mode: str = self.modes[0]

        # UI
        self.ui: UI = UI(c.UIWIDTH, c.UIHEIGHT)
        self.bgColor: Color = colors.BACKGROUND

        # HUD
        self.hud: Hud = Hud()
        self.drawHud: bool = False

        # Time Controls
        self.playSpeed: ClampedFloat = ClampedFloat(1.0, 0.1, 2.0)
        self.paused: bool = False
        #endregion

        #region - World
        self.world: World[Ball] = World()

        self.defaultRadius: int = c.DEFAULTBALLRADIUS
        self.inPreview: bool = False
        self.preview: Preview = Preview(self.mousePos, self.world.ballColor)
        #endregion

        #region - Mainloop variables
        self.running: bool = True

        self.targetFPS: int = c.DEFAULTTARGETFPS
        self.dt: float = 1 / self.targetFPS
        #endregion

    # App Methods
    def update(self) -> None:
        self.dt = self.dt * self.playSpeed.value

        # Mouse
        self.mouseMovement: Vector2 = getMouseMovement(self)

        self.mousePressed: tuple = pg.mouse.get_pressed()
        self.mouseJustPressed: tuple = pg.mouse.get_just_pressed()
        self.mouseJustReleased: tuple = pg.mouse.get_just_released()

        # Keyboard
        self.keyJustPresses = pg.key.get_just_pressed()

        # UI
        self.ui.update(self.mousePos, self.mouseJustReleased, self)

        if not self.paused:
            # Ball dragging
            for ball in self.world.balls.members:
                if ball.held:
                    if self.dt != 0:
                        ball.v = self.mouseMovement / self.dt
            
            # Modes:---
            # Add new balls (Variable)
            if self.mode == "summon (variable)":
                if self.mouseJustPressed[2]:
                    for ball in self.world.balls.members:
                        if ball.collidesWith(self.mousePos):
                            break
                    else:
                        self.preview: Preview = Preview(self.mousePos, self.world.ballColor)
                        self.inPreview: bool = True
                
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
            if self.mode == "summon (fixed)":
                if self.mouseJustPressed[2]:
                    for ball in self.world.balls.members:
                        if ball.collidesWith(self.mousePos):
                            break
                    else:
                        summonBall(self.mousePos, self.defaultRadius, self.world.ballColor)
            # Remove balls
            if self.mode == "kill":
                if self.mousePressed[2]:
                    for index in range(len(self.world.balls.members) - 1, -1, -1):
                        curBall: Ball = self.world.balls.members[index]
                        if curBall.collidesWith(self.mousePos):
                            self.world.balls.kill(curBall)
                            break  
            # ---------

            # FBD
            if pg.key.get_just_pressed()[pg.K_f]:
                self.world.fbdMode = not self.world.fbdMode

            # World Update
            self.world.update(self.width, self.height, self.dt, self.mouseJustPressed,
                            self.mouseJustReleased, self.mousePos, self.keyJustPresses)

        # Pausing
        if self.keyJustPresses[pg.K_SPACE]:
            self.paused = not self.paused
            self.ui.active = True
        if self.keyJustPresses[pg.K_TAB]:
            self.ui.active = not self.ui.active
            
        # Quit
        if pg.key.get_just_pressed()[pg.K_ESCAPE]:
            self.quit()

    def draw(self) -> None:
        # Background
        self.screen.fill(self.bgColor)
        
        # Draw World
        self.world.draw(self.screen)

        # Draw Preview
        if self.inPreview:
            self.preview.draw(self.screen)

        # HUD
        if self.drawHud:
            self.hud.draw(self.screen, self.world, self.mode, self.world.fbdMode)

        self.ui.draw(self.screen)

    def cycleMode(self, direction: int) -> None:
        self.mode = self.modes[(self.modes.index(self.mode) - direction) % len(self.modes)]

    def clearBalls(self) -> None:
        self.world.balls.kill()

    def toggleFBD(self) -> bool:
        self.world.fbdMode = not self.world.fbdMode
        return self.world.fbdMode

    def quit(self) -> None:
        self.running: bool = False

app = AppState()

# Helper functions

def getMouseMovement(app: AppState) -> Vector2:
    app.previousMousePos = app.mousePos
    app.mousePos = Vector2(pg.mouse.get_pos())

    return app.mousePos - app.previousMousePos

def summonBall(pos: Vector2, radius: int, color: Color) -> None:
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
    app.update()
    app.draw()

    pg.display.update()

pg.quit()

