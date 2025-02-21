# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Enums of tokens

from enum import IntEnum

class Movement(IntEnum):
    FORWARD = 0,
    BACK = 1,
    LEFT = 2,
    RIGHT = 3,

class Arm(IntEnum):
    BOOM = 10,
    STICK = 11,
    BUCKET = 12,

class Body(IntEnum):
    MOVEMENT = 20,
    ROTATION = 21,

ArmMovement = IntEnum("ArmMovement", 
                        {**Movement.__members__, **Arm.__members__})
BodyMovement = IntEnum("BodyMovement", 
                        {**Movement.__members__, **Body.__members__})
