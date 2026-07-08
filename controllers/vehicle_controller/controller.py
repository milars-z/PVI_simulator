from __future__ import annotations

import math

from agents.agent_enums import ORIENTATION_ANGLE
from agents.veh_agent import VehicleAgent
from controllers.vehicle_controller.state_machine import VehicleStateMachine
from controllers.vehicle_controller.types import (
    VehicleControlResult,
    VehicleControllerState,
)
from observations.veh_observation import VehicleObservationResult


FIXED_JERK: float = 0.0
FIXED_TARGET_DECELERATION: float = 0.0


class VehicleController:
    """
    Vehicle controller entry point.

    Behavior logic lives in controllers/vehicle_controller/states.
    """

    def __init__(self) -> None:
        self.state_machine = VehicleStateMachine()

    def update(
        self,
        dt: float,
        veh_list: list[VehicleAgent],
        veh_obs_list: list[VehicleObservationResult],
    ) -> None:
        obs_map = self._build_obs_map(veh_obs_list)

        for veh in veh_list:
            veh_obs = obs_map.get(veh.veh_id)
            state = self.state_machine.update(veh=veh, veh_obs=veh_obs)

            if state == VehicleControllerState.FINISH:
                continue

            control_result = self.control_vehicle(veh=veh, veh_obs=veh_obs)
            self._update_motion(dt=dt, veh=veh, control_result=control_result)
            self.state_machine.update(veh=veh, veh_obs=veh_obs)

    def control_vehicle(
        self,
        veh: VehicleAgent,
        veh_obs: VehicleObservationResult | None,
    ) -> VehicleControlResult:
        return VehicleControlResult(
            jerk=FIXED_JERK,
            target_deceleration=FIXED_TARGET_DECELERATION,
        )

    def are_all_finished(self, veh_list: list[VehicleAgent]) -> bool:
        return all(self.state_machine.is_finished(veh) for veh in veh_list)

    def _build_obs_map(
        self,
        veh_obs_list: list[VehicleObservationResult],
    ) -> dict[int, VehicleObservationResult]:
        return {obs.veh_id: obs for obs in veh_obs_list}

    def _update_motion(
        self,
        dt: float,
        veh: VehicleAgent,
        control_result: VehicleControlResult,
    ) -> None:
        raw_jerk = self._clip(
            value=control_result.jerk,
            min_value=-veh.max_jerk,
            max_value=veh.max_jerk,
        )
        veh.target_acceleration = self._clip(
            value=-control_result.target_deceleration,
            min_value=-veh.max_deceleration,
            max_value=veh.max_acceleration,
        )

        target_acc = veh.acceleration + raw_jerk * dt
        target_acc = self._clip(
            value=target_acc,
            min_value=-veh.max_deceleration,
            max_value=veh.max_acceleration,
        )

        target_speed = veh.speed + target_acc * dt
        target_speed = min(target_speed, veh.init_speed_mps)

        if target_speed < 0.0:
            target_speed = 0.0
            target_acc = 0.0
            raw_jerk = 0.0

        veh.jerk = raw_jerk
        veh.acceleration = target_acc
        veh.speed = target_speed

        angle = ORIENTATION_ANGLE[veh.orientation]
        veh.pos_x += veh.speed * math.cos(angle) * dt
        veh.pos_y += veh.speed * math.sin(angle) * dt

    def _clip(
        self,
        value: float,
        min_value: float,
        max_value: float,
    ) -> float:
        return max(min_value, min(value, max_value))
