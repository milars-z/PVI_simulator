from __future__ import annotations

from agents.veh_agent import VehicleAgent
from controllers.vehicle_controller.states import (
    handle_finish_state,
    handle_interaction_state,
    handle_recovery_state,
    handle_start_state,
    is_vehicle_finished,
)
from controllers.vehicle_controller.types import VehicleControllerState
from observations.veh_observation import VehicleObservationResult


class VehicleStateMachine:
    def __init__(self) -> None:
        self._states: dict[int, VehicleControllerState] = {}

    def update(
        self,
        veh: VehicleAgent,
        veh_obs: VehicleObservationResult | None,
    ) -> VehicleControllerState:
        state = self._states.get(veh.veh_id, VehicleControllerState.START)

        if state == VehicleControllerState.START:
            handle_start_state(veh=veh, veh_obs=veh_obs)
            state = VehicleControllerState.INTERACTION

        elif state == VehicleControllerState.INTERACTION:
            handle_interaction_state(veh=veh, veh_obs=veh_obs)

        elif state == VehicleControllerState.RECOVERY:
            handle_recovery_state(veh=veh, veh_obs=veh_obs)

        elif state == VehicleControllerState.FINISH:
            handle_finish_state(veh=veh, veh_obs=veh_obs)
            self._states[veh.veh_id] = state
            return state

        if is_vehicle_finished(veh):
            state = VehicleControllerState.FINISH
            handle_finish_state(veh=veh, veh_obs=veh_obs)

        self._states[veh.veh_id] = state
        return state

    def is_finished(self, veh: VehicleAgent) -> bool:
        return (
            self._states.get(veh.veh_id)
            == VehicleControllerState.FINISH
        )
