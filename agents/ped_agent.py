from __future__ import annotations

import random
from typing import TYPE_CHECKING

from agents.agent_enums import AgentType, Orientation
from agents.base_agent import BaseAgent
from configs.pedestrian_config import (
    PED_BASIC_CONFIG,
    PED_DEFAULT_CHARA_CONFIG,
    PED_TYPE_CHARA_CONFIG,
)

if TYPE_CHECKING:
    from world.world import World


class PedestrianAgent(BaseAgent):
    def __init__(
        self,
        ped_id: int,
        seed: int,
    ) -> None:
        super().__init__(
            agent_type=AgentType.PEDESTRIAN,
            spawn_x=0.0,
            spawn_y=0.0,
            size_x=0.0,
            size_y=0.0,
            speed=0.0,
            orientation=Orientation.UP,
        )

        self.ped_id = ped_id
        self.seed = seed

        self.ped_type_id = 0
        self.ped_type = ""
        self.chara_index = 0

        self.ped_speed = 0.0
        self.finish_line = 0.0

        self.is_pass = False

    def init_ped(self, world: "World") -> "PedestrianAgent":
        self._init_basic_para(world)
        self._init_chara_para()
        self._init_random_para()

        return self

    def _init_basic_para(self, world: "World") -> None:
        ped_spawn_config = world.get_ped_init_config()

        self.spawn_x = ped_spawn_config["spawn_x"]
        self.spawn_y = ped_spawn_config["spawn_y"]
        self.finish_line = ped_spawn_config["finish_line"]

        self.pos_x = self.spawn_x
        self.pos_y = self.spawn_y

        self.orientation = ped_spawn_config["orientation"]

        self.size_x = PED_BASIC_CONFIG["size_x"]
        self.size_y = PED_BASIC_CONFIG["size_y"]

        type_list = PED_BASIC_CONFIG["type_list"]
        self.ped_type_id = self.ped_id % len(type_list)
        self.ped_type = type_list[self.ped_type_id]

    def _init_chara_para(self) -> None:
        self._load_default_chara_para()

        type_config = PED_TYPE_CHARA_CONFIG[self.ped_type]
        params_config = type_config["params"]

        type_num = len(PED_BASIC_CONFIG["type_list"])

        for para_name, para_config in params_config.items():
            values = para_config["values"]

            self.chara_index = (self.ped_id // type_num) % len(values)
            value = values[self.chara_index]

            setattr(self, para_name, value)

        self.speed = self.ped_speed

    def _init_random_para(self) -> None:
        type_config = PED_TYPE_CHARA_CONFIG[self.ped_type]
        params_config = type_config["params"]

        rng = random.Random(self.seed + self.ped_id)

        for para_name, para_config in params_config.items():
            noise_std = para_config["noise_std"]

            if noise_std is None:
                continue

            current_value = getattr(self, para_name)

            if current_value is None:
                continue

            noisy_value = current_value + rng.gauss(0.0, noise_std)
            setattr(self, para_name, noisy_value)

        self.speed = self.ped_speed

    def _load_default_chara_para(self) -> None:
        self.ped_speed = PED_DEFAULT_CHARA_CONFIG["ped_speed"]
