from typing import Any
from pygame import Color

import constants as c
import colors
from enums import GravityMode
from floats import ClampedFloat

class Context:
    def __init__(self) -> None:
        #region - Physics
        self.gravityMode: GravityMode = GravityMode.Down
        self.gravity: ClampedFloat = ClampedFloat(c.DEFAULTGRAVITY, 0.0, 3000.0, 1)
        self.friction: ClampedFloat = ClampedFloat(c.DEFAULTFRICTION, 0.0, 1.0, 2)
        self.bounce: ClampedFloat = ClampedFloat(c.DEFAULTBOUNCE, 0.0, 1.0, 2)
        self.airDensity: ClampedFloat = ClampedFloat(c.DEFAULTAIRDENSITY, 0.0, 5.0, 3)
        self.ballDensity: float = 0.0 #future
        self.doFriction: bool = True
        self.doDrag: bool = True
        self.mouseGravityStrength: ClampedFloat = ClampedFloat(c.DEFAULTMOUSEGRAVITYSTRENGTH, 0.0, 10.0, 1)
        self.dampingCoefficient: ClampedFloat = ClampedFloat(c.DEFAULTDAMPINGCOEFFICIENT, 0.0, 10.0, 1)
        #endregion

        #region - Generic
        self.ballRadius: ClampedFloat = ClampedFloat(c.DEFAULTBALLRADIUS, 10.0, 100.0, 0)
        self.limitBalls: bool = True
        self.maxBalls: ClampedFloat = ClampedFloat(100, 10, 200, 0)
        self.bgColor: Color = Color(colors.BACKGROUND)
        self.ballColor: Color = Color(colors.BALLFILL)
        #endregion

        #region - Display
        self.showHUD: bool = True
        self.showVectors: bool = True
        self.momentumVector: bool = True
        self.gravityVector: bool = True
        self.normalVector: bool = True
        self.frictionVector: bool = True
        self.dragVector: bool = True
        self.arrowScale: ClampedFloat = ClampedFloat(c.ARROWCONSTANT, 0.01, 0.10, 2)
        self.arrowSmoothing: ClampedFloat = ClampedFloat(c.LERPCONSTANT, 0.01, 0.50, 2)
        self.fixedArrowWidth: bool = False
        self.playSpeed: ClampedFloat = ClampedFloat(1.0, 0.2, 3.0, 1)
        self.showBallInfo: bool = True #future
        #endregion

        #region - Advanced
        self.dragCoefficient: ClampedFloat = ClampedFloat(c.DEFAULTDRAGCOEFFICIENT, 0.0, 1.0, 3)
        self.slidingFrictionRatio: ClampedFloat = ClampedFloat(c.DEFAULTSLIDINGFRICTIONRATIO, 0.0, 10.0, 1)
        #endregion

    def update(self, values: dict[str, Any]):
        for name, value in values.items():
            if not hasattr(self, name):
                raise KeyError(f"'{name}' is an unknown setting")
            cur = getattr(self, name)
            if isinstance(cur, ClampedFloat):
                cur.update(value)
            elif isinstance(cur, Color):
                cur.update(value)
            else:
                setattr(self, name, value)

    def reset(self):
        for name, fresh in vars(Context()).items():
            cur = getattr(self, name)
            if isinstance(cur, ClampedFloat):
                cur.update(fresh.value)
            elif isinstance(cur, Color):
                cur.update(fresh)
            else:
                setattr(self, name, fresh)


ct = Context()

# customizations = {
#     "gravity": 9.81,
#     "friction": 0.8,
#     "bounce": 0.6,
#     "airDensity": 1.225,
#     "mouseGravityStrength": 5.0,
#     "dampingCoefficient": 0.1,
#     "bgColor": (30, 30, 30),
#     "showHUD": False,
# }

# def print_context_values(context: Context):
#     for var, val in vars(context).items():
#         if isinstance(val, (ClampedFloat, SmoothFloat)):
#             print(f"{var}: {val.value}")
#         else:
#             print(f"{var}: {val}")

# print("Before update:")
# print_context_values(ct)
# print("\nUpdating context with customizations...\n")

# ct.update(customizations)

# print("After update:")
# print_context_values(ct)

# print("\nReverting context to default values...\n")

# ct.reset()

# print("After reverting:")
# print_context_values(ct)

