import pygame as pg
from pygame import Vector2, Color, Surface
from math import copysign, sqrt, cbrt

from world import World
from gravity import GravityMode
from arrow import drawArrow

import colors
import constants as c

# Type Hints Declaration
type Point = tuple[int, int]

pg.init()

# Classes
class Ball:
    LERPCONSTANT: float = 12.5

    def __init__(self, pos: Vector2, radius: float, color: Color) -> None:
        # Properties
        self.radius: float = radius
        self.color: Color = color

        # Positioning
        self.pos: Vector2 = Vector2(pos)

        # Physical Quantities
        self.v: Vector2 = Vector2()
        self.a: Vector2 = Vector2()
        self.forces: dict[str, Vector2] = {}

        self.displayMomentum: Vector2 = Vector2()
        self.displayGravity: Vector2 = Vector2()
        self.displayFriction: Vector2 = Vector2()
        self.displayNormal: Vector2 = Vector2()

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
        pg.draw.circle(screen, colors.SOFTGREY, self.pos, self.radius)
        pg.draw.circle(screen, self.color, self.pos, self.radius - 2)
        
        pmg: float = self.displayMomentum.magnitude()
        
        if fbdMode:
            # momentum
            if not self.held:
                if self.v.magnitude() != 0 and self.displayMomentum.magnitude() > 5:

                    displayMomentumVector: Vector2 = self.displayMomentum.normalize() * (sqrt(pmg + 1) - 1) * c.MOMENTUMARROWCONSTANT
                    drawArrow(screen, self.pos, self.pos + displayMomentumVector, colors.BRIGHTPURPLE,
                            3, min(int(displayMomentumVector.magnitude() / 2), 10), 30, True)

            # forces
            # 1. gravity
            gravity = self.displayGravity
            if gravity.magnitude() > 0 and self.displayGravity.magnitude() > 5:
                displayGravityVector: Vector2 = gravity.normalize() * (sqrt(gravity.magnitude())) * c.GRAVITYARROWCONSTANT
                drawArrow(screen, self.pos, self.pos + displayGravityVector, colors.BLACK, 3, 10, 30, True)

            # 2. normal
            normal = self.displayNormal
            if normal.magnitude() > 0 and self.displayNormal.magnitude() > 5:
                displayNormalVector: Vector2 = normal.normalize() * (sqrt(normal.magnitude())) * c.NORMALARROWCONSTANT
                drawArrow(screen, self.pos, self.pos + displayNormalVector, colors.SOFTGREEN, 3, 10, 30, True)

            # 3. friction
            friction = self.displayFriction
            if friction.magnitude() > 0 and self.displayFriction.magnitude() > 5:
                displayFrictionVector: Vector2 = friction.normalize() * (sqrt(friction.magnitude())) * c.FRICTIONARROWCONSTANT
                if displayFrictionVector.magnitude() > 5:
                    drawArrow(screen, self.pos, self.pos + displayFrictionVector, colors.YELLOW, 3, 10, 30, True)


    def update(self, width: int, height: int, world: World, dt: float, mousePos: Vector2) -> None:
        # forces redefined
        self.forces = {}

        # all forces
        # 1. gravity
        if world.gravityMode == GravityMode.Mouse:
            if not self.held:
                try:
                    direction: Vector2 = (mousePos - self.pos).normalize()
                except ValueError:
                    direction: Vector2 = Vector2(0, 0)
                
                distance: float = mousePos.distance_to(self.pos)
                gravitation: Vector2 = direction * (c.G / (distance + c.GRAVITYEPSILON))

                radialVelocityMag: float = self.v.dot(direction)
                radialVelocity: Vector2 = direction * radialVelocityMag
                tangentialVelocity: Vector2 = self.v - radialVelocity 

                damping: Vector2 = (-radialVelocity * c.RADIALDAMPINGCOEFFICIENT) + (-tangentialVelocity * c.TANGENTIALDAMPINGCOEFFICIENT)

                # resting ball if too close and too slow
                if distance < 3 and self.v.magnitude() < 50:
                    self.pos: Vector2 = Vector2(mousePos)
                    self.v.update(0, 0)
                else:
                    gravitation = self.mass * (gravitation + damping)
                    self.forces["gravity"] = gravitation
            else:
                gravitation = Vector2(0, 0)
        else:
            gravitation = self.mass * world.gravityMode.value * world.gravity
            self.forces["gravity"] = gravitation

        # 2. normal
        if self.held or self.onGround:
            normal: Vector2 = -gravitation
            if normal.magnitude() > 0: self.forces["normal"] = normal

        # 3. friction
        if self.onGround:
            friction: Vector2 = self.applyFriction(world.friction, normal, world.gravityMode, dt)
            if friction.magnitude() > 0: self.forces["friction"] = friction
    
        # movement
        self.a.update(0, 0)
        print(self.forces)
        netForce = Vector2()
        for force in self.forces.values():
            netForce += force

        self.a = netForce / self.mass

        self.v += self.a * dt
        self.pos += self.v * dt

        # display vectors
        if "normal" not in self.forces:
            normal = Vector2(0, 0)
        if "friction" not in self.forces:
            friction = Vector2(0, 0)

        self.displayMomentum: Vector2 = self.displayMomentum.lerp(self.momentum, min(self.LERPCONSTANT * dt, 1))
        self.displayGravity: Vector2 = self.displayGravity.lerp(gravitation, min(self.LERPCONSTANT * dt, 1))
        self.displayNormal: Vector2 = self.displayNormal.lerp(normal, min(self.LERPCONSTANT * dt, 1))
        self.displayFriction: Vector2 = self.displayFriction.lerp(friction, min(self.LERPCONSTANT * dt, 1))

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

    def applyFriction(self, friction: float, normal: Vector2, gravityMode: GravityMode, dt: float) -> Vector2:
        if self.onGround:
            # gravity on y-axis
            if gravityMode in [GravityMode.Up, GravityMode.Down]:
                # sliding
                if abs(self.v.y) >= 10:
                    return Vector2((abs(self.v.x) / dt) * c.SLIDINGFRICTIONRATIO, 0) * -copysign(1, self.v.x)
                # rolling
                else:
                    if abs(self.v.x) <= 1:
                        return Vector2(-self.v.x, 0)
                    else:
                        return Vector2(friction * normal.magnitude(), 0) * -copysign(1, self.v.x)
            # gravity on x-axis
            if gravityMode in [GravityMode.Left, GravityMode.Right]:
                # sliding
                if abs(self.v.x) >= 10:
                    return Vector2(0, (abs(self.v.y) / dt) * c.SLIDINGFRICTIONRATIO) * -copysign(1, self.v.y)
                # rolling
                else:
                    if abs(self.v.y) <= 1:
                        return Vector2(0, -self.v.y)
                    else:
                        return Vector2(0, friction * normal.magnitude()) * -copysign(1, self.v.y)
        
        return Vector2(0, 0)
    