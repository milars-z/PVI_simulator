# agents/ped_agent.py

import random

from agents.base_agent import BaseAgent
from agents.agent_enums import AgentType, Orientation, PedStage
from configs.pedestrian_config import (
    PED_BASIC_CONFIG,
    PED_DEFAULT_CHARA_CONFIG,
    PED_TYPE_CHARA_CONFIG,
)


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
        self.wait_time = 0.0

        self.wait_line = 0.0
        self.finish_line = 0.0

        self.acc_ttc_gap = None
        self.acc_stop_ratio = None
        self.acc_speed = None

        self.cross_probability = 1.0
        self.focus_probability = 1.0
        self.is_pass = True

        self.stage = PedStage.INIT

    def init_ped(self, world) -> "PedestrianAgent":
        self._init_basic_para(world)
        self._init_chara_para()
        self._init_random_para()

        return self

    def _init_basic_para(self, world) -> None:
        ped_spawn_config = world.get_ped_init_config()
        # "spawn_x"
        # "spawn_y"
        # "random_radius" 暂时未使用
        # "orientation"
        # "wait_line"
        # "finish_line"

        self.spawn_x = ped_spawn_config["spawn_x"]
        self.spawn_y = ped_spawn_config["spawn_y"]
        self.wait_line = ped_spawn_config["wait_line"]  #等待坐标，由world配置
        self.finish_line = ped_spawn_config["finish_line"]  #结束坐标，由world配置

        self.pos_x = self.spawn_x
        self.pos_y = self.spawn_y

        self.orientation = ped_spawn_config["orientation"]

        self.size_x = PED_BASIC_CONFIG["size_x"]
        self.size_y = PED_BASIC_CONFIG["size_y"]

        self.cross_probability = PED_BASIC_CONFIG["cross_probability"]
        self.focus_probability = PED_BASIC_CONFIG["focus_probability"]
        self.is_pass = PED_BASIC_CONFIG["is_pass"]

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

        self.acc_ttc_gap = PED_DEFAULT_CHARA_CONFIG["acc_ttc_gap"]
        self.acc_stop_ratio = PED_DEFAULT_CHARA_CONFIG["acc_stop_ratio"]
        self.acc_speed = PED_DEFAULT_CHARA_CONFIG["acc_speed"]

        self.cross_probability = PED_DEFAULT_CHARA_CONFIG["cross_probability"]
        self.focus_probability = PED_DEFAULT_CHARA_CONFIG["focus_probability"]
        self.is_pass = PED_DEFAULT_CHARA_CONFIG["is_pass"]

    def update(self, dt: float) -> None:
        if self.stage == PedStage.INIT:
            super().update(dt)

        elif self.stage == PedStage.WAIT:
            self.wait_time += dt

        elif self.stage == PedStage.CROSS:
            super().update(dt)

        elif self.stage == PedStage.DANGEROUS:
            super().update(dt)

        elif self.stage == PedStage.FINISH:
            pass

    def is_finished(self) -> bool:
        return self.stage == PedStage.FINISH