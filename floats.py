from enums import Easing
import numpy as np
from pygame.math import clamp

class SmoothFloat:
    def __init__(self, value: float = 0.0, clamped: bool = False, lowerLimit: float = 0.0, upperLimit: float = 1.0, decimals: int = 1) -> None:
        self._value: float = value
        self.startVal: float = value
        self.targetVal: float = value

        self.clamped: bool = clamped
        if clamped:
            self.lowerLimit: float = lowerLimit
            self.upperLimit: float = upperLimit
            self.decimals: int = abs(decimals)

        self.active: bool = False

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, newValue: float):
        self.setTarget(newValue, 60, Easing.EaseOut)

    def setTarget(self, value: float, frames: int, easing: Easing = Easing.EaseOut):
        if self.clamped:
            value = clamp(value, self.lowerLimit, self.upperLimit)
            value = float(f"{value:.{self.decimals}f}")

        if not self.active:
            # values
            self.startVal: float = self._value
            self.targetVal: float = value

            # timings
            self.active: bool = True
            self.curFrame: int = 0
            self.frames: int = frames

            self.t = np.array([i for i in range(1, frames + 1)]) / frames
            if easing == Easing.EaseIn:
                self.t = (self.t)**3
            elif easing == Easing.EaseOut:
                self.t = 1 - (1 - self.t)**3
            elif easing == Easing.EaseInOut:
                firstHalf, secondHalf = np.array_split(self.t, 2)
                firstHalf = 4 * (firstHalf ** 3)
                secondHalf = 1 - 4 * (1 - secondHalf) ** 3
                self.t = np.concat((firstHalf, secondHalf))
        
    def update(self):
        # animation
        if self.active:
            # progess
            self.curFrame += 1
            self._value = self.startVal + self.t[self.curFrame - 1] * (self.targetVal - self.startVal)

            # end
            if self.curFrame == self.frames:
                self._value = self.targetVal
                self.active = False

class ClampedFloat:
    def __init__(self, value: float, lowerLimit: float, upperLimit: float, decimals: int) -> None:
        self._value: float = value
        self.lowerLimit: float = lowerLimit
        self.upperLimit: float = upperLimit
        self.decimals: int = abs(decimals)
        self.update(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, newValue: float):
        self.update(newValue)

    def update(self, newValue: float):
        self._value = float(f"{clamp(newValue, self.lowerLimit, self.upperLimit):.{self.decimals}f}")
