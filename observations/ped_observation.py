from __future__ import annotations

from dataclasses import dataclass, field

from agents.ped_agent import PedestrianAgent
from agents.veh_agent import VehicleAgent
from world.world import World


@dataclass(frozen=True)
class ObservedVehicleResult:
    veh_id: int
    car_speed_view: float
    car_pos_x: float
    car_pos_y: float


@dataclass
class PedestrianObservationResult:
    ped_id: int
    has_vehicle: bool = False
    observed_vehicles: list[ObservedVehicleResult] = field(default_factory=list)


class PedestrianObservation:
    """Pedestrian-side raw observation collector."""

    def __init__(self) -> None:
        self.results: list[PedestrianObservationResult] = []

    def update(self, world: World) -> list[PedestrianObservationResult]:
        self.results.clear()

        ped_list = world.get_ped_list()
        veh_list = world.get_veh_list()

        for ped in ped_list:
            self.results.append(
                self._observe_ped(
                    ped=ped,
                    veh_list=veh_list,
                )
            )

        return self.results

    def to_dict(
        self,
        results: list[PedestrianObservationResult] | None = None,
    ) -> dict[int, PedestrianObservationResult]:
        if results is None:
            results = self.results

        return {result.ped_id: result for result in results}

    def _observe_ped(
        self,
        ped: PedestrianAgent,
        veh_list: list[VehicleAgent],
    ) -> PedestrianObservationResult:
        return PedestrianObservationResult(
            ped_id=ped.ped_id,
            has_vehicle=bool(veh_list),
            observed_vehicles=[
                self._build_observed_vehicle_result(veh)
                for veh in veh_list
            ],
        )

    def _build_observed_vehicle_result(
        self,
        veh: VehicleAgent,
    ) -> ObservedVehicleResult:
        return ObservedVehicleResult(
            veh_id=veh.veh_id,
            car_speed_view=veh.speed,
            car_pos_x=veh.pos_x,
            car_pos_y=veh.pos_y,
        )
