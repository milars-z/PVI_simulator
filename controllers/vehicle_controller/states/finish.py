from __future__ import annotations

from agents.agent_enums import Orientation
from agents.veh_agent import VehicleAgent
from observations.veh_observation import VehicleObservationResult


def handle_finish_state(
    veh: VehicleAgent,
    veh_obs: VehicleObservationResult | None,
) -> None:
    veh.speed = 0.0
    veh.acceleration = 0.0
    veh.jerk = 0.0


def is_vehicle_finished(veh: VehicleAgent) -> bool:
    if veh.orientation == Orientation.RIGHT:
        return veh.pos_x >= veh.finish_x

    if veh.orientation == Orientation.LEFT:
        return veh.pos_x <= veh.finish_x

    return False
