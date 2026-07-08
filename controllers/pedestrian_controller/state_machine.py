from __future__ import annotations

from agents.ped_agent import PedestrianAgent
from controllers.pedestrian_controller.states import (
    handle_finish_state,
    handle_interaction_state,
    handle_recovery_state,
    handle_start_state,
    is_pedestrian_finished,
)
from controllers.pedestrian_controller.types import PedestrianControllerState
from observations.ped_observation import PedestrianObservationResult


class PedestrianStateMachine:
    def __init__(self) -> None:
        self._states: dict[int, PedestrianControllerState] = {}

    def update(
        self,
        ped: PedestrianAgent,
        ped_obs: PedestrianObservationResult | None,
    ) -> PedestrianControllerState:
        state = self._states.get(ped.ped_id, PedestrianControllerState.START)

        if state == PedestrianControllerState.START:
            handle_start_state(ped=ped, ped_obs=ped_obs)
            state = PedestrianControllerState.INTERACTION

        elif state == PedestrianControllerState.INTERACTION:
            handle_interaction_state(ped=ped, ped_obs=ped_obs)

        elif state == PedestrianControllerState.RECOVERY:
            handle_recovery_state(ped=ped, ped_obs=ped_obs)

        elif state == PedestrianControllerState.FINISH:
            handle_finish_state(ped=ped, ped_obs=ped_obs)
            self._states[ped.ped_id] = state
            return state

        if is_pedestrian_finished(ped):
            state = PedestrianControllerState.FINISH
            handle_finish_state(ped=ped, ped_obs=ped_obs)
        else:
            ped.is_pass = False

        self._states[ped.ped_id] = state
        return state

    def is_finished(self, ped: PedestrianAgent) -> bool:
        return (
            self._states.get(ped.ped_id)
            == PedestrianControllerState.FINISH
        )
