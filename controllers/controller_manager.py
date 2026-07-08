from __future__ import annotations

from typing import TypedDict

from controllers.pedestrian_controller import PedestrianController
from controllers.vehicle_controller import VehicleController
from observations.ped_observation import PedestrianObservationResult
from observations.veh_observation import VehicleObservationResult
from world.world import World


class SimulationObservations(TypedDict):
    pedestrian: list[PedestrianObservationResult]
    vehicle: list[VehicleObservationResult]


class ControllerManager:
    """
    Simulator controller entry point.

    The manager only routes typed observations into the pedestrian and vehicle
    control adapters.
    """

    def __init__(self) -> None:
        self.pedestrian = PedestrianController()
        self.vehicle = VehicleController()

    def update(
        self,
        dt: float,
        world: World,
        observations: SimulationObservations,
    ) -> None:
        self.pedestrian.update(
            dt=dt,
            ped_list=world.get_ped_list(),
            ped_obs_list=observations["pedestrian"],
        )

        self.vehicle.update(
            dt=dt,
            veh_list=world.get_veh_list(),
            veh_obs_list=observations["vehicle"],
        )

        if self._are_all_agents_finished(world):
            world.mark_round_finished()

    def _are_all_agents_finished(self, world: World) -> bool:
        ped_list = world.get_ped_list()
        veh_list = world.get_veh_list()

        if not ped_list or not veh_list:
            return False

        return (
            self.pedestrian.are_all_finished(ped_list)
            and self.vehicle.are_all_finished(veh_list)
        )
