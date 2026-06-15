# agents/agent_enums.py

from enum import Enum
import math


class AgentType(Enum):
    VEHICLE = "veh"
    PEDESTRIAN = "ped"


class Orientation(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class PedStage(Enum):
    INIT = "init"
    WAIT = "wait"
    CROSS = "cross"
    DANGEROUS = "dangerous"
    FINISH = "finish"

class VehStage(Enum):
    INIT = "init"
    RUN = "run"
    INTERACTIVE = "interactive"
    RECOVER = "recover"
    FINISH = "finish"


ORIENTATION_ANGLE = {
    Orientation.RIGHT: 0.0,
    Orientation.DOWN: math.pi / 2,
    Orientation.LEFT: math.pi,
    Orientation.UP: 3 * math.pi / 2,
}

