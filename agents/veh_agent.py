# agents/veh_agent.py

from typing import Any

from agents.base_agent import BaseAgent
from agents.agent_enums import AgentType, Orientation, VehStage
from configs.veh_config import VEH_BASIC_CONFIG, VEH_COMBO_CONFIG

import configs.config as config


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
        # self.seed = seed

        # 车辆没有人格类型，只有实验 combo
        self.combo_id = 0
        # self.combo_name = ""

        self.distance_to_crossroad_m = 0.0
        self.init_speed_mps = 0.0

        # 车辆运动学状态
        self.acceleration = 0.0
        self.jerk = 0.0

        # controller 可以修改这个值
        # agent 自己不做决策，只根据 target_acceleration 更新运动状态
        self.target_acceleration = 0.0

        # 车辆物理限制
        self.max_jerk = 0.0
        self.max_deceleration = 0.0
        self.max_acceleration = 0.0

        # 车辆停止点
        self.stop_x = 0.0

        self.stage = VehStage.INIT

    def init_veh(self, world: Any) -> "VehicleAgent":
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

        self.combo_name = combo_config["combo_name"]
        self.distance_to_crossroad_m = combo_config["distance_to_crossroad_m"]
        self.init_speed_mps = combo_config["init_speed_kmh"] * config.KMH_MPS

        self.speed = self.init_speed_mps

    def _set_spawn_position(self, world: Any) -> None:
        veh_spawn_config = world.get_veh_init_config()

        # "veh_cross_x"
        # "veh_cross_y"
        # "orientation"

        orientation = veh_spawn_config["orientation"]

        veh_cross_x = veh_spawn_config.get("veh_cross_x", 0.0)
        veh_cross_y = veh_spawn_config.get("veh_cross_y", 0.0)

        self.spawn_x = veh_cross_x - self.distance_to_crossroad_m
        self.spawn_y = veh_cross_y

        self.pos_x = self.spawn_x
        self.pos_y = self.spawn_y

        self.stop_x = veh_cross_x

        self.orientation = orientation

    def set_target_acceleration(self, target_acceleration: float) -> None:
        """
        controller 调用这个函数修改车辆目标加速度。

        例如：
            正常行驶: 0.0
            缓慢减速: -1.0
            正常减速: -2.5
            快速减速: -4.0
            紧急制动: -6.0
        """

        if target_acceleration < -self.max_deceleration:
            target_acceleration = -self.max_deceleration

        if target_acceleration > self.max_acceleration:
            target_acceleration = self.max_acceleration

        self.target_acceleration = target_acceleration

    def _update_acceleration_with_jerk_limit(self, dt: float) -> None:
        acc_diff = self.target_acceleration - self.acceleration

        max_acc_change = self.max_jerk * dt

        if acc_diff > max_acc_change:
            acc_change = max_acc_change
        elif acc_diff < -max_acc_change:
            acc_change = -max_acc_change
        else:
            acc_change = acc_diff

        self.jerk = acc_change / dt if dt > 0.0 else 0.0
        self.acceleration += acc_change

        if self.acceleration < -self.max_deceleration:
            self.acceleration = -self.max_deceleration

        if self.acceleration > self.max_acceleration:
            self.acceleration = self.max_acceleration

    def _update_speed(self, dt: float) -> None:
        self.speed += self.acceleration * dt

        if self.speed < 0.0:
            self.speed = 0.0
            self.acceleration = 0.0
            self.jerk = 0.0

    def update(self, dt: float) -> None:
        if self.stage == VehStage.INIT:
            super().update(dt)

        elif self.stage == VehStage.RUN:
            self.set_target_acceleration(0.0)
            self._update_acceleration_with_jerk_limit(dt)
            self._update_speed(dt)
            super().update(dt)

        elif self.stage == VehStage.YIELD:
            self._update_acceleration_with_jerk_limit(dt)
            self._update_speed(dt)
            super().update(dt)

        elif self.stage == VehStage.STOP:
            self.speed = 0.0
            self.acceleration = 0.0
            self.jerk = 0.0

        elif self.stage == VehStage.FINISH:
            self.speed = 0.0
            super().update(dt)
    
    def is_finished(self) -> bool:
        return self.stage == VehStage.FINISH