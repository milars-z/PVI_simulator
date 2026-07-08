from __future__ import annotations

from typing import TYPE_CHECKING

import configs.config as config
from agents.agent_enums import AgentType, Orientation
from agents.base_agent import BaseAgent
from configs.veh_config import VEH_BASIC_CONFIG, VEH_COMBO_CONFIG

if TYPE_CHECKING:
    from world.world import World


class VehicleAgent(BaseAgent):
    def __init__(
        self,
        veh_id: int,
        seed: int,
    ) -> None:
        super().__init__(
            agent_type=AgentType.VEHICLE,
            spawn_x=0.0,
            spawn_y=0.0,
            size_x=0.0,
            size_y=0.0,
            speed=0.0,
            orientation=Orientation.RIGHT,
        )

        self.veh_id = veh_id
        self.seed = seed

        self.combo_id = 0
        self.distance_to_crossroad_m = 0.0

        self.init_speed_mps = 0.0
        self.acceleration = 0.0
        self.jerk = 0.0
        self.target_acceleration = 0.0

        self.max_jerk = 0.0
        self.max_deceleration = 0.0
        self.max_acceleration = 0.0

        self.stop_x = 0.0
        self.finish_x = 0.0

    def init_veh(self, world: "World") -> "VehicleAgent":
        self._init_basic_para()
        self._init_combo_para()
        self._set_spawn_position(world)

        return self

    def _init_basic_para(self) -> None:
        self.size_x = VEH_BASIC_CONFIG["size_x"]
        self.size_y = VEH_BASIC_CONFIG["size_y"]
        self.max_jerk = VEH_BASIC_CONFIG["max_jerk"]
        self.max_deceleration = VEH_BASIC_CONFIG["max_deceleration"]
        self.max_acceleration = VEH_BASIC_CONFIG["max_acceleration"]
        self.acceleration = VEH_BASIC_CONFIG["init_acceleration"]
        self.jerk = VEH_BASIC_CONFIG["init_jerk"]
        self.target_acceleration = self.acceleration

    def _init_combo_para(self) -> None:
        combo_list = VEH_COMBO_CONFIG["combo_list"]
        self.combo_id = self.veh_id % len(combo_list)
        combo_config = combo_list[self.combo_id]

        self.distance_to_crossroad_m = combo_config["distance_to_crossroad_m"]
        self.init_speed_mps = combo_config["init_speed_kmh"] * config.KMH_MPS
        self.speed = self.init_speed_mps

    def _set_spawn_position(self, world: "World") -> None:
        veh_spawn_config = world.get_veh_init_config()
        veh_cross_x = veh_spawn_config["veh_cross_x"]
        veh_cross_y = veh_spawn_config["veh_cross_y"]

        self.spawn_x = veh_cross_x - self.distance_to_crossroad_m
        self.spawn_y = veh_cross_y
        self.pos_x = self.spawn_x
        self.pos_y = self.spawn_y
        self.stop_x = veh_cross_x
        self.finish_x = veh_spawn_config["finish_x"]
        self.orientation = veh_spawn_config["orientation"]
