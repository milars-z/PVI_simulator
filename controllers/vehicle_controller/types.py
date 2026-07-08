from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class VehicleControllerState(Enum):
    START = "start"
    INTERACTION = "interaction"
    RECOVERY = "recovery"
    FINISH = "finish"


@dataclass(frozen=True)
class VehicleControlResult:
    jerk: float
    target_deceleration: float
