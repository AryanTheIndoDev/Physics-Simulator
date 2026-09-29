import pygame as pg
from pygame import Vector2, Color, Surface

def drawArrow(screen: Surface, startingPoint: Vector2, endingPoint: Vector2, color: Color,
              width: int = 3, headLength: int = 15, headAngle: int = 45, filled: bool = False):
    # the line
    pg.draw.line(screen, color, startingPoint, endingPoint, width)
    
    # backwards normal
    try:
        direction: Vector2 = (endingPoint - startingPoint).normalize()
    except ValueError:
        return
    back: Vector2 = -direction

    # arrowhead lines
    left: Vector2 = back.rotate(-headAngle) * headLength
    right: Vector2 = back.rotate(headAngle) * headLength

    if filled:
        pg.draw.polygon(screen, color, (endingPoint, endingPoint + left, endingPoint + right))
    else:
        pg.draw.line(screen, color, endingPoint, endingPoint + left, width)
        pg.draw.line(screen, color, endingPoint, endingPoint + right, width)