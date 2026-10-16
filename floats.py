from enums import Easing
import numpy as np
from pygame.math import clamp

class SmoothFloat:
    def __init__(self, value: float = 0.0) -> None:
        self._value: float = value
        self.startVal: float = value
        self.targetVal: float = value

        self.active: bool = False

    @property
    def value(self):
        return self._value

    def setTarget(self, value: float, frames: int, easing: Easing = Easing.EaseOut):
        if not self.active:
            # values
            self.startVal: float = self._value
            self.targetVal: float = value

            # timings
            self.active: bool = True
            self.curFrame: int = 0
            self.frames: int = frames

            self.t = np.array([i for i in range(1, frames + 1)])
            if easing == Easing.EaseIn:
                self.t = (self.t/frames)**3
            elif easing == Easing.EaseOut:
                self.t = 1 - (1 - self.t/frames)**3
        
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
    def __init__(self, value: float, lowerLimit: float, upperLimit: float) -> None:
        self._value: float = value
        self.lowerLimit: float = lowerLimit
        self.upperLimit: float = upperLimit

    @property
    def value(self):
        return self._value

    def update(self, newValue: float):
        self._value = clamp(newValue, self.lowerLimit, self.upperLimit)
