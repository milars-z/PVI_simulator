# controllers/vehicle_controller.py

from __future__ import annotations

from typing import Any

from agents.agent_enums import VehStage

class VehicleController:
    """
    车辆控制器。

    负责根据车辆观测到的行人信息，更新车辆速度、加速度、jerk 和行为状态。
    """

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
        """

        if veh.pos_x >= 70:
            veh.stage = VehStage.FINISH



    def _update_motion(
        self,
        dt: float,
        veh: Any,
    ) -> None:
        """
        车辆运动控制部分
        根据jerk和一些内部限制更新speed
        """

        
        veh.update(dt) #运动实现，仅依赖speed
        # veh.speed += veh.acceleration * dt

        # if veh.speed < 0.0:
        #     veh.speed = 0.0

        # veh.pos_x += veh.speed * dt