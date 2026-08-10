from group import Group
from typing import Any, TypeVar, Generic, Protocol
from gravity import GravityMode
from pygame import Surface, Vector2, Color
import pygame as pg

# Type Hints Declaration
type Point = tuple[int, int]

# Placeholder
class PlaceHolder(Protocol):
    held: bool
    pos: Vector2
    v: Vector2
    radius: float
    @property
    def mass(self) -> float: ...
    def draw(self, screen: Surface, fbdMode: bool): ...
    def update(self, width: int, height: int, world: Any, dt: float, mousePos: Vector2): ...
    def remap(self, originalDimensions: Point, newDimensions: Point): ...
    def tryGrab(self, mousePos: Vector2): ...

# Generic Type
T = TypeVar("T", bound = PlaceHolder)

# World
class World(Generic[T]):
    def __init__(self, gravity: float, friction: float, bounce: float) -> None:

        # Physics
        self.gravity: float = gravity
        self.gravityMode: GravityMode = GravityMode.Down
        self.friction: float = friction
        self.bounce: float = bounce

        # Simulation
        self.fbdMode: bool = False
        
        # Objects
        self.balls: Group[T] = Group()
        self.ballColor: Color = Color(228, 32, 50)
    
    def update(self, width: int, height: int, dt: float, mouseClicks: tuple,
               mouseReleases: tuple, mousePos: Vector2, keyboard: tuple):

        # Ball being held or not
        if mouseClicks[0]:
            for ball in self.balls.members:
                ball.tryGrab(mousePos)  
        elif mouseReleases[0]:
            for ball in self.balls.members:
                if ball.held:
                    ball.held = False
        
        # gravity mode switch
        if mouseClicks[1]:
            self.gravityMode = GravityMode.Mouse
        if keyboard[pg.K_UP]:
            self.gravityMode = GravityMode.Up
        elif keyboard[pg.K_DOWN]:
            self.gravityMode = GravityMode.Down
        elif keyboard[pg.K_LEFT]:
            self.gravityMode = GravityMode.Left
        elif keyboard[pg.K_RIGHT]:
            self.gravityMode = GravityMode.Right
    
        # ball updating
        self.balls.update(width, height, self, dt, mousePos)
        
        # check for collision between balls
        self.handleCollision()

    def draw(self, screen: Surface):
        self.balls.draw(screen, self.fbdMode)

    def handleCollision(self):
        for i in range(len(self.balls.members)):
            for j in range(i + 1, len(self.balls.members)):

                ball1: T = self.balls.members[i]
                ball2: T = self.balls.members[j]

                if ball1 is not ball2:
                    if ball1.pos.distance_to(ball2.pos) <= ball1.radius + ball2.radius:
                        try:
                            normal: Vector2 = (ball2.pos - ball1.pos).normalize()
                        except ValueError:
                            normal: Vector2 = Vector2()
                        
                        # Collision
                        m1 = ball1.mass
                        m2 = ball2.mass

                        vn1: float = ball1.v.dot(normal)
                        vn2: float = ball2.v.dot(normal)

                        e = self.bounce

                        new_vn1 = (vn1 * (m1 - m2 * e) + (1 + e) * m2 * vn2) / (m1 + m2)
                        new_vn2 = (vn2 * (m2 - m1 * e) + (1 + e) * m1 * vn1) / (m1 + m2)

                        ball1.v += (new_vn1 - vn1) * normal
                        ball2.v += (new_vn2 - vn2) * normal

                        # Overlap
                        totalMass: float = m1 + m2

                        overlap: float = ball1.radius + ball2.radius - ball1.pos.distance_to(ball2.pos)

                        correction1: Vector2 = normal * overlap * (m2 / totalMass)
                        correction2: Vector2 = normal * overlap * (m1 / totalMass)

                        ball1.pos -= correction1
                        ball2.pos += correction2
