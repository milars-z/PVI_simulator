from __future__ import annotations

import math

from agents.agent_enums import ORIENTATION_ANGLE
from agents.ped_agent import PedestrianAgent
from controllers.pedestrian_controller.state_machine import PedestrianStateMachine
from controllers.pedestrian_controller.types import (
    PedestrianControlResult,
    PedestrianControllerState,
)
from observations.ped_observation import PedestrianObservationResult


class PedestrianController:
    """
    Pedestrian controller entry point.

    Behavior logic lives in controllers/pedestrian_controller/states.
    """

    def __init__(self) -> None:
        self.state_machine = PedestrianStateMachine()

    def update(
        self,
        dt: float,
        ped_list: list[PedestrianAgent],
        ped_obs_list: list[PedestrianObservationResult],
    ) -> None:
        obs_map = self._build_obs_map(ped_obs_list)

        for ped in ped_list:
            ped_obs = obs_map.get(ped.ped_id)
            state = self.state_machine.update(ped=ped, ped_obs=ped_obs)

            if state == PedestrianControllerState.FINISH:
                continue

            control_result = self.control_pedestrian(ped=ped, ped_obs=ped_obs)
            self._update_motion(dt=dt, ped=ped, control_result=control_result)
            self.state_machine.update(ped=ped, ped_obs=ped_obs)

    def control_pedestrian(
        self,
        ped: PedestrianAgent,
        ped_obs: PedestrianObservationResult | None,
    ) -> PedestrianControlResult:
        return PedestrianControlResult(speed=ped.ped_speed)

    def are_all_finished(self, ped_list: list[PedestrianAgent]) -> bool:
        return all(self.state_machine.is_finished(ped) for ped in ped_list)

    def _build_obs_map(
        self,
        ped_obs_list: list[PedestrianObservationResult],
    ) -> dict[int, PedestrianObservationResult]:
        return {obs.ped_id: obs for obs in ped_obs_list}

    def _update_motion(
        self,
        dt: float,
        ped: PedestrianAgent,
        control_result: PedestrianControlResult,
    ) -> None:
        ped.speed = max(0.0, control_result.speed)
        angle = ORIENTATION_ANGLE[ped.orientation]
        ped.pos_x += ped.speed * math.cos(angle) * dt
        ped.pos_y += ped.speed * math.sin(angle) * dt
