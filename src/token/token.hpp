#pragma once

enum class MotorTokens
{
    NUL,
    POWER,
    DIRECTION, // clockwise/counter clockwise
    STATE, // low/high
};

enum class TrackedTreadsDirectionTokens
{
    NUL,
    FORWARD,
    BACK,
    LEFT,
    RIGHT,
};

enum class CabinDirectionTokens
{
    NUL,
    LEFT,
    RIGHT,
};

enum class BucketTokens
{
    NUL,
    FORWARD,
    BACK,
};

enum class BoomTokens
{
    NUL,
    UP,
    DOWN,
};

enum class ArmTokens
{
    NUL,
    UP,
    DOWN,
};
