# controllers/vehicle_controller.py

from __future__ import annotations

from typing import Any

from agents.agent_enums import VehStage

from interaction.vehicle_state_discretizer import VehicleStateDiscretizer
from interaction.vehicle_cost import VehicleCostCalculator
from interaction.PVI_controller import PCF
from interaction.action_config import JERK_ACTION_LIST

from observations.veh_observation import ObservedPedestrianResult
from agents.veh_agent import VehicleAgent

class VehicleController:
    """
    车辆控制器。

    负责根据车辆观测到的行人信息，更新车辆速度、加速度、jerk 和行为状态。
    """

    def __init__(self):
        self.dis = VehicleStateDiscretizer()
        self.calculator = VehicleCostCalculator()
        self.controller = PCF(
            dis = self.dis,
            calculator = self.calculator,
            actions = JERK_ACTION_LIST,
        )

    def update(
        self,
        dt: float,
        veh_list: list[Any],
        veh_obs_list: list[Any],
    ) -> None:
        obs_map = self._build_obs_map(veh_obs_list)

        for veh in veh_list:
            veh_obs = obs_map.get(veh.veh_id)

            if veh_obs is None:
                self._update_without_observation(dt, veh)
            else:
                self._update_with_observation(dt, veh, veh_obs)

    def _build_obs_map(self, veh_obs_list: list[Any]) -> dict[int, Any]:
        obs_map: dict[int, Any] = {}

        for obs in veh_obs_list:
            obs_map[obs.veh_id] = obs

        return obs_map

    def _update_without_observation(
        self,
        dt: float,
        veh: Any,
    ) -> None:
        self._update_motion(dt, veh)

    def _update_with_observation(
        self,
        dt: float,
        veh: Any,
        veh_obs: Any,
    ) -> None:
        self._update_decision(dt, veh, veh_obs)
        self._update_motion(dt, veh)

    def _update_decision(
        self,
        dt: float,
        veh: Any,
        veh_obs: Any,
    ) -> None:
        """
        车辆逻辑控制部分
        这一块为车辆控制核心
        目的为根据现有的车辆情况，以及车辆观测到的行人情况来选择性价比最高的决策
        决策为离散的主决策与连续的微调模块组成
        离散主要为几个状态
        分别为：匀速行驶，满减速，稳停减速，急停，速度恢复
        目的是让PVI交互尽量不会影响车辆的速度，在保证速度和效率和交互体验的情况下选取最优的解答

        self.jerk 
        self.target_acceleration 
        self.acceleration
        """

        # 暂时只处理第一个行人
        if veh_obs.has_pedestrian == True:
            obs = veh_obs.observed_pedestrians[0]
        else:
            veh.state = VehStage.FINISH
        
        if veh.stage == VehStage.INIT:
            veh.stage = VehStage.RUN

        if veh.stage == VehStage.RUN:
            
            self._handle_run_stage(dt, veh, obs)

        elif veh.stage == VehStage.INTERACTIVE:
            self._handle_interactive_stage(dt, veh, obs)

        elif veh.stage == VehStage.RECOVER:
            self._handle_recover_stage(dt, veh, obs)

        elif veh.stage == VehStage.FINISH:
            
            self._handle_finish_stage(dt, veh, obs)

        else:
            raise ValueError(f"Unknown vehicle state: {veh.stage}")

          

    def _update_motion(
        self,
        dt: float,
        veh: VehicleAgent,
    ) -> None:
        """
        车辆运动控制部分
        根据jerk和一些内部限制更新speed
        """

        jerk  = veh.jerk * dt
        _acc  = veh.acceleration
        target_acc = _acc + jerk ## jerk为负数

        # 暂时不对acc进行硬约束
        _speed = veh.speed
        target_speed = _speed + target_acc * dt

        if target_speed < 0:
            target_speed = 0

        veh.acceleration = target_acc
        veh.speed = target_speed

        # target_acc = veh.target_acceleration
        # current_acc = veh.acceleration


        # max_delta_acc = abs(veh.jerk) * dt
        # acc_error = target_acc - current_acc

        # if abs(acc_error) <= max_delta_acc:
        #     veh.acceleration = target_acc
        # elif acc_error > 0.0:
        #     veh.acceleration += max_delta_acc
        # else:
        #     veh.acceleration -= max_delta_acc


        # veh.speed += veh.acceleration * dt

        # # 车辆不能倒退
        # if veh.speed < 0.0:
        #     veh.speed = 0.0
        #     veh.acceleration = 0.0
        #     veh.target_acceleration = 0.0

        veh.update(dt) #运动实现，仅依赖speed


    def _handle_run_stage(self,dt, veh, veh_obs):
        veh.stage = VehStage.INTERACTIVE


    def _handle_interactive_stage(self,dt, veh, veh_obs):

        # self.dis.discretize(veh_obs = veh_obs,veh = veh)
        # total_cost = self.calculator.calculate(veh,veh_obs)
        # print(total_cost)
        action = self.controller.get_action(
            veh = veh,
            veh_obs = veh_obs,
            dt = dt,
            k = 5,
        )
        veh.jerk = action.jerk
        print(veh.jerk)
        # veh.jerk = -4.0
        if veh.pos_x >= 70:
            veh.stage = VehStage.FINISH

    # def _handle_recover_stage(self,dt, veh, veh_obs):
    #     if veh.pos_x >= 70:
    #         veh.stage = VehStage.FINISH

    def _handle_finish_stage(self,dt, veh, veh_obs):
        pass



