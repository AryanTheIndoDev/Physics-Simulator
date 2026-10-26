import pygame as pg
from pygame import Surface, Vector2

from group import Group
from typing import TypeVar, Generic, Protocol
from enums import GravityMode
from context import ct

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
    def draw(self, screen: Surface): ...
    def update(self, width: int, height: int, dt: float, mousePos: Vector2): ...
    def remap(self, originalDimensions: Point, newDimensions: Point): ...
    def tryGrab(self, mousePos: Vector2): ...
    def releaseGrab(self): ...

# Generic Type
T = TypeVar("T", bound = PlaceHolder)

# World
class World(Generic[T]):
    def __init__(self) -> None:

        # Objects
        self.balls: Group[T] = Group()
        
    def update(self, width: int, height: int, dt: float, mouseClicks: tuple,
               mousePresses: tuple, mousePos: Vector2, keyboard: tuple):

        # Ball being held or not
        if mouseClicks[0]:
            for ball in self.balls.members:
                ball.tryGrab(mousePos)  
        elif not mousePresses[0]:
            for ball in self.balls.members:
                ball.releaseGrab()
        
        # gravity mode switch
        if mouseClicks[1]:
            ct.update({"gravityMode": GravityMode.Mouse})
        if keyboard[pg.K_UP]:
            ct.update({"gravityMode": GravityMode.Up})
        elif keyboard[pg.K_DOWN]:
            ct.update({"gravityMode": GravityMode.Down})
        elif keyboard[pg.K_LEFT]:
            ct.update({"gravityMode": GravityMode.Left})
        elif keyboard[pg.K_RIGHT]:
            ct.update({"gravityMode": GravityMode.Right})
    
        # ball updating
        self.balls.update(width, height, dt, mousePos)
        
        # check for collision between balls
        self.handleCollision(width, height)

    def draw(self, screen: Surface):
        self.balls.draw(screen)

    def handleCollision(self, width: int, height: int):
        for i in range(len(self.balls.members)):
            ball1: T = self.balls.members[i]
            pos, v, radius = ball1.pos, ball1.v, ball1.radius

            # ball-wall collision
            yaxis = False
            xaxis = False
            # y-axis
            if pos.y - radius <= 0:
                pos.y = radius
                yaxis = True
            elif pos.y + radius >= height:
                pos.y = height - radius
                yaxis = True
            # resting
            if yaxis:
                v.y = -v.y * ct.bounce.value
                if abs(v.x) < 2:
                    v.x = 0
                if abs(v.y) < 50:
                    v.y = 0
            # x-axis
            if pos.x - radius <= 0:
                pos.x = radius
                xaxis = True
            elif pos.x + radius >= width:
                pos.x = width - radius
                xaxis = True
            # resting
            if xaxis:
                v.x = -v.x * ct.bounce.value
                if abs(v.y) < 2:
                    v.y = 0
                if abs(v.x) < 50:
                    v.x = 0

            # ball-ball collision
            for j in range(i + 1, len(self.balls.members)):
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

                        e = ct.bounce.value

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
