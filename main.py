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
pg.draw.circle(icon, Color(230, 0, 60), (icon.get_width() / 2, icon.get_height() / 2), icon.get_width() / 2)
pg.draw.circle(icon, Color(26, 18, 29), (icon.get_width() / 2, icon.get_height() / 2), icon.get_width() / 2, width = 2)

pg.display.set_icon(icon)

# App State
class appState:
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

        # Options
        self.modes: list = ["summon (variable)", "summon (fixed)", "kill"]
        self.mode: str = self.modes[0]

        # Important
        self.running: bool = True

        # HUD
        self.hud: Hud = Hud()

        # World
        self.world: World[Ball] = World(gravity = 1500, friction = 50, bounce = 0.8)
        self.dt: float = 1 / 60
        self.fps: int = 60

        # Ball
        self.defaultRadius: int = 30
        self.inPreview: bool = False
        self.preview: Preview = Preview(self.mousePos, self.world.ballColor)

    # App Methods
    def update(self):
        # Mouse Movement
        self.mouseMovement: Vector2 = getMouseMovement(self)

        # Background
        self.screen.fill("cyan")
                    
        # Ball dragging
        for ball in self.world.balls.members:
            if ball.held:
                ball.v = self.mouseMovement / self.dt
        
        # Draw World
        self.world.draw(self.screen)
        
        # Modes:---
        # Add new balls (Variable)
        if self.mode == "summon (variable)":
            if pg.mouse.get_just_pressed()[2]:
                for ball in self.world.balls.members:
                    if ball.collidesWith(self.mousePos):
                        break
                else:
                    self.preview: Preview = Preview(self.mousePos, self.world.ballColor)
                    self.inPreview: bool = True
            
            if self.inPreview:
                if pg.mouse.get_pressed()[2]:
                    self.preview.radius = min(int(self.preview.pos.distance_to(self.mousePos)),
                                            int(min(self.width, self.height) / 4))
                    self.preview.draw(self.screen)
                
                if pg.mouse.get_just_released()[2]:
                    summonBall(self.preview.pos, self.preview.radius, self.preview.color)
                    self.inPreview: bool = False
        # Add new balls (Fixed)
        if self.mode == "summon (fixed)":
            if pg.mouse.get_just_pressed()[2]:
                for ball in self.world.balls.members:
                    if ball.collidesWith(self.mousePos):
                        break
                else:
                    summonBall(self.mousePos, self.defaultRadius, self.world.ballColor)
        # Remove balls
        if self.mode == "kill":
            if pg.mouse.get_pressed()[2]:
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

    def cycleMode(self, direction: int):
        self.mode = self.modes[(self.modes.index(self.mode) - direction) % len(self.modes)]

    def quit(self) -> None:
        self.running: bool = False

App = appState()

# Helper functions

def getMouseMovement(app: appState) -> Vector2:
    app.previousMousePos = app.mousePos
    app.mousePos = Vector2(pg.mouse.get_pos())

    return app.mousePos - app.previousMousePos

def summonBall(pos: Vector2, radius: int, color: Color) -> None:
    App.world.balls.add(Ball(pos, radius, color))

def windowResize(app: appState, new_dimensions: Point):
    # new dimensions
    new_width, new_height = new_dimensions
    
    # clamping new dimensions
    new_width = max(new_width, MINWIDTH) 
    new_height = max(new_height, MINHEIGHT)

    # remapping ball pos
    app.world.balls.remap((app.width, app.height), (new_width, new_height))

    # updating dimensions
    app.width = new_width
    app.height = new_height

    # resize
    if (new_width, new_height) != event.size:
        app.screen = pg.display.set_mode((app.width, app.height), pg.RESIZABLE)

# Mainloop
while App.running:
    for event in pg.event.get():
        # Resizing
        if event.type == pg.VIDEORESIZE:
            windowResize(App, event.size)
        # Scroll
        if event.type == pg.MOUSEWHEEL:
            App.cycleMode(event.y)
        # Quit
        if event.type == pg.QUIT:
            App.quit()
        
    # Tasks
    App.update()

    pg.display.update()
    App.dt = App.clock.tick(App.fps) / 1000

pg.quit()
