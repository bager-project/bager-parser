# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Enums of tokens

from enum import Enum

class Arm(Enum):
    BOOM = 0,
    STICK = 1,
    BUCKET = 2,

class Movement(Enum):
    FORWARD = 0,
    BACK = 1,
    LEFT = 2,
    RIGHT = 3,

class Motor(Enum):
    pass
