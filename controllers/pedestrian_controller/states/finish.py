from __future__ import annotations

from agents.agent_enums import Orientation
from agents.ped_agent import PedestrianAgent
from observations.ped_observation import PedestrianObservationResult


def handle_finish_state(
    ped: PedestrianAgent,
    ped_obs: PedestrianObservationResult | None,
) -> None:
    ped.is_pass = True


def is_pedestrian_finished(ped: PedestrianAgent) -> bool:
    if ped.orientation == Orientation.UP:
        return ped.pos_y <= ped.finish_line

    if ped.orientation == Orientation.DOWN:
        return ped.pos_y >= ped.finish_line

    return False
