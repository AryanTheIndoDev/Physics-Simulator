import pygame as pg
from pygame import Surface, Clock, Vector2, Color

from world import World
from ball import Ball
from hud import Hud
from preview import Preview

# Global Variables
MINWIDTH = 400
MINHEIGHT = 300

# Type Hints Declaration
type Point = tuple[int, int]

# Pygame Initialization
pg.init()

# Titling
pg.display.set_caption("Ball Studios")

# Iconing
icon: Surface = Surface((32, 32), pg.SRCALPHA)
pg.draw.circle(icon, Color(230, 0, 60), (icon.get_width() // 2, icon.get_height() // 2), icon.get_width() // 2)
pg.draw.circle(icon, Color(26, 18, 29), (icon.get_width() // 2, icon.get_height() // 2), icon.get_width() // 2, width = 2)

pg.display.set_icon(icon)

# App State
class AppState:
    def __init__(self) -> None:

        # Pygame stuff
        self.width: int = 600
        self.height: int = 400

        self.screen: Surface = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)
        self.clock: Clock = Clock()

        # mouse
        self.mousePos: Vector2 = Vector2()
        self.previousMousePos: Vector2 = Vector2()
        self.mouseMovement: Vector2 = Vector2()

        self.mouseJustPressed: tuple = pg.mouse.get_just_pressed()
        self.mousePressed: tuple = pg.mouse.get_pressed()
        self.mouseJustReleased: tuple = pg.mouse.get_just_released()

        # Options
        self.modes: list = ["summon (variable)", "summon (fixed)", "kill"]
        self.mode: str = self.modes[0]

        # Mainloop variables
        self.running: bool = True

        self.dt: float = 1 / 60
        self.fps: int = 60

        # UI
        self.bgColor: Color = Color(43, 160, 205)

        # HUD
        self.hud: Hud = Hud()

        # World
        self.world: World[Ball] = World(gravity = 1500, friction = 50, bounce = 0.8)

        # Ball
        self.defaultRadius: int = 30
        self.inPreview: bool = False
        self.preview: Preview = Preview(self.mousePos, self.world.ballColor)

    # App Methods
    def update(self) -> None:
        # Mouse
        self.mouseMovement: Vector2 = getMouseMovement(self)

        self.mousePressed: tuple = pg.mouse.get_pressed()
        self.mouseJustPressed: tuple = pg.mouse.get_just_pressed()
        self.mouseJustReleased: tuple = pg.mouse.get_just_released()

        # Background
        self.screen.fill(self.bgColor)
                    
        # Ball dragging
        for ball in self.world.balls.members:
            if ball.held:
                ball.v = self.mouseMovement / self.dt
        
        # Draw World
        self.world.draw(self.screen)
        
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
                                            int(min(self.width, self.height) / 4))
                    self.preview.draw(self.screen)
                
                if self.mouseJustReleased[2]:
                    summonBall(self.preview.pos, self.preview.radius, self.preview.color)
                    self.inPreview: bool = False
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
        self.world.update(self.width, self.height, self.dt, pg.mouse.get_just_pressed(),
                          pg.mouse.get_just_released(), self.mousePos, pg.key.get_just_pressed())

        # HUD
        self.hud.draw(self.screen, self.world, self.mode, self.world.fbdMode)

        # Quit
        if pg.key.get_just_pressed()[pg.K_ESCAPE]:
            self.quit()

    def cycleMode(self, direction: int) -> None:
        self.mode = self.modes[(self.modes.index(self.mode) - direction) % len(self.modes)]

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
    newWidth = max(newWidth, MINWIDTH) 
    newHeight = max(newHeight, MINHEIGHT)

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
    app.dt = app.clock.tick(app.fps) / 1000

    # Tasks
    app.update()

    pg.display.update()

pg.quit()

