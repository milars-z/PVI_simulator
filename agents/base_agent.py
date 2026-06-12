# agents/base_agent.py

import math
from .agent_enums import ORIENTATION_ANGLE, Orientation, AgentType


class BaseAgent:
    def __init__(
        self,
        agent_type: AgentType,
        spawn_x: float,
        spawn_y: float,
        size_x: float,
        size_y: float,
        speed: float,
        orientation: Orientation,
    ) -> None:
        self.type = agent_type

        self.spawn_x = spawn_x
        self.spawn_y = spawn_y

        self.pos_x = spawn_x
        self.pos_y = spawn_y

        self.size_x = size_x
        self.size_y = size_y

        self.speed = speed
        self.orientation = orientation

    def update(self, dt: float) -> None:
        angle = ORIENTATION_ANGLE[self.orientation]

        self.pos_x += self.speed * math.cos(angle) * dt
        self.pos_y += self.speed * math.sin(angle) * dt