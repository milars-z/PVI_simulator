from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PedestrianControllerState(Enum):
    START = "start"
    INTERACTION = "interaction"
    RECOVERY = "recovery"
    FINISH = "finish"


@dataclass(frozen=True)
class PedestrianControlResult:
    speed: float
