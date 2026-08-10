import pygame as pg
from pygame import Vector2, Color, Surface
from math import copysign, sqrt, cbrt

from world import World
from gravity import GravityMode
from arrow import drawArrow

# Type Hints Declaration
type Point = tuple[int, int]

pg.init()

# Classes
class Ball:
    LERPCONSTANT: float = 0.2
    ARROWLENGTHCONSTANT: float = 0.06

    def __init__(self, pos: Vector2, radius: float, color: Color) -> None:
        # Properties
        self.radius: float = radius
        self.color: Color = color

        # Positioning
        self.pos: Vector2 = pos

        # Physical Quantities
        self.v: Vector2 = Vector2()
        self.a: Vector2 = Vector2()

        self.displayMomentum: Vector2 = Vector2()

        # States
        self.onGround: bool = False
        self.held: bool = False
    
    @property
    def mass(self) -> float:
        return self.radius ** 2
    
    @property
    def momentum(self) -> Vector2:
        return self.mass * self.v
    
    def draw(self, screen: Surface, fbdMode: bool) -> None:
        pg.draw.circle(screen, Color(26, 18, 29), self.pos, self.radius)
        pg.draw.circle(screen, self.color, self.pos, self.radius - 2)
        
        pmg: float = self.displayMomentum.magnitude()
        
        if fbdMode and not self.held:
            if self.v.magnitude() != 0 and self.displayMomentum.magnitude() > 5:

                # Main Arrow
                displayMomentumVector: Vector2 = self.displayMomentum.normalize() * (sqrt(pmg + 1) - 1) * self.ARROWLENGTHCONSTANT
                drawArrow(screen, self.pos, self.pos + displayMomentumVector, Color(89, 71, 182), 3, 10, 30)

                # Axis Arrows
                if self.v.magnitude() > 50:
                    if abs(self.v.x) > 10:
                        drawArrow(screen, self.pos, self.pos + Vector2(displayMomentumVector.x, 0), Color("blue"), 3, 10, 30)
                    if abs(self.v.y) > 10:
                        drawArrow(screen, self.pos, self.pos + Vector2(0, displayMomentumVector.y), Color("blue"), 3, 10, 30)

    
    def update(self, width: int, height: int, world: World, dt: float, mousePos: Vector2) -> None:
        # acceleration redefined
        self.a.update(0, 0)
        if not self.held:
            # gravity
            if world.gravityMode == GravityMode.Down:
                if not self.onGround:
                    self.a += Vector2(0, world.gravity)
            elif world.gravityMode == GravityMode.Up:
                if not self.onGround:
                    self.a += Vector2(0, -world.gravity)
            elif world.gravityMode == GravityMode.Left:
                if not self.onGround:
                    self.a += Vector2(-world.gravity, 0)
            elif world.gravityMode == GravityMode.Right:
                if not self.onGround:
                    self.a += Vector2(world.gravity, 0)
            elif world.gravityMode == GravityMode.Mouse:
                try:
                    direction: Vector2 = (mousePos - self.pos).normalize()
                except ValueError:
                    direction: Vector2 = Vector2(0, 0)
                
                epsilon: int = 100
                distance: float = mousePos.distance_to(self.pos)
                G: float = 3e5
                gravitation: Vector2 = direction * (G / (distance + epsilon))

                radialVelocityMag: float = self.v.dot(direction)
                radialVelocity: Vector2 = direction * radialVelocityMag
                tangentialVelocity: Vector2 = self.v - radialVelocity 

                radialDampingCoefficient: float = 3.0 # 3.0
                tangentialDampingCoefficient: float = 0.3 # 0.3
                damping: Vector2 = (-radialVelocity * radialDampingCoefficient) + (-tangentialVelocity * tangentialDampingCoefficient)

                # resting ball if too close and too slow
                if distance < 3 and self.v.length() < 50:
                    self.pos: Vector2 = mousePos
                    self.v.update(0, 0)
                else:
                    self.a += gravitation + damping
            # friction
            friction: Vector2 = self.applyFriction(world.friction, world.gravityMode, dt)
            self.a += friction
    
        # movement
        self.v += self.a * dt
        self.pos += self.v * dt


        # display momentum
        self.displayMomentum: Vector2 = self.displayMomentum.lerp(self.momentum, 0.2)

        # collision
        # y-axis
        if self.pos.y + self.radius >= height:
            self.pos.y = height - self.radius
            self.v.y = -self.v.y * world.bounce
            # rest
            if abs(self.v.x) < 2:
                self.v.x = 0

            if abs(self.v.y) < 50:
                self.v.y = 0
        if self.pos.y - self.radius <= 0:
            self.pos.y = self.radius
            self.v.y = -self.v.y * world.bounce
            # rest
            if abs(self.v.x) < 2:
                self.v.x = 0

            if abs(self.v.y) < 50:
                self.v.y = 0

        # x-axis
        if self.pos.x + self.radius >= width:
            self.pos.x = width - self.radius
            self.v.x = -self.v.x * world.bounce
            # rest
            if abs(self.v.y) < 2:
                self.v.y = 0

            if abs(self.v.x) < 50:
                self.v.x = 0
        if self.pos.x - self.radius <= 0:
            self.pos.x = self.radius
            self.v.x = -self.v.x * world.bounce
            # rest
            if abs(self.v.y) < 2:
                self.v.y = 0

            if abs(self.v.x) < 50:
                self.v.x = 0

        # on Ground check
        self.onGround: bool = self.checkOnGround(world.gravityMode, width, height)

    def collidesWith(self, point: Vector2) -> bool:
        if self.pos.distance_to(point) <= self.radius:
            return True
        else:
            return False

    def tryGrab(self, mousePos: Vector2) -> None:
        if Vector2(mousePos).distance_to(self.pos) <= self.radius:
            self.held = True

    def remap(self, originalDimensions: Point, newDimensions: Point) -> None:
        ox, oy = originalDimensions
        nx, ny = newDimensions

        self.pos.x = pg.math.remap(0, ox, 0, nx, self.pos.x)
        self.pos.y = pg.math.remap(0, oy, 0, ny, self.pos.y)

    def checkOnGround(self, gravityMode: GravityMode, width: int, height: int) -> bool:
        if gravityMode == GravityMode.Up:
            if self.pos.y - self.radius - 1 <= 0:
                return True
        elif gravityMode == GravityMode.Down:
            if self.pos.y + self.radius + 1 >= height:
               return True
        elif gravityMode == GravityMode.Left:
            if self.pos.x - self.radius - 1 <= 0:
               return True
        elif gravityMode == GravityMode.Right:
            if self.pos.x + self.radius + 1 >= width:
               return True
        else:
            return False
        
        return False

    def applyFriction(self, friction: float, gravityMode: GravityMode, dt: float) -> Vector2:
        if self.onGround:
            if gravityMode in [GravityMode.Up, GravityMode.Down]:
                # sliding
                if abs(self.v.y) >= 10:
                    return Vector2(self.v.x * 0.05 / dt, 0) * -1
                # rolling
                else:
                    if abs(self.v.x) <= 1:
                        return Vector2(-self.v.x, 0)
                    else:
                        return Vector2(friction, 0) * -copysign(1, self.v.x)
            if gravityMode in [GravityMode.Left, GravityMode.Right]:
                # sliding
                if abs(self.v.x) >= 10:
                    return Vector2(0, self.v.y * 0.05 / dt) * -1
                # rolling
                else:
                    if abs(self.v.y) <= 1:
                        return Vector2(0, -self.v.y)
                    else:
                        return Vector2(0, friction) * -copysign(1, self.v.y)
        
        return Vector2(0, 0)