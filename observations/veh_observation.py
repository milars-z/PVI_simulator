from __future__ import annotations

from dataclasses import dataclass, field

from agents.ped_agent import PedestrianAgent
from agents.veh_agent import VehicleAgent
from world.world import World


@dataclass(frozen=True)
class ObservedPedestrianResult:
    ped_id: int
    ped_pos_x: float
    ped_pos_y: float
    ped_speed: float
    is_pass: bool


@dataclass
class VehicleObservationResult:
    veh_id: int
    has_pedestrian: bool = False
    observed_pedestrians: list[ObservedPedestrianResult] = field(default_factory=list)


class VehicleObservation:
    """Vehicle-side raw observation collector."""

    def __init__(self) -> None:
        self.results: list[VehicleObservationResult] = []

    def update(self, world: World) -> list[VehicleObservationResult]:
        self.results.clear()

        ped_list = world.get_ped_list()
        veh_list = world.get_veh_list()

        for veh in veh_list:
            self.results.append(
                self._observe_veh(
                    veh=veh,
                    ped_list=ped_list,
                )
            )

        return self.results

    def to_dict(
        self,
        results: list[VehicleObservationResult] | None = None,
    ) -> dict[int, VehicleObservationResult]:
        if results is None:
            results = self.results

        return {result.veh_id: result for result in results}

    def _observe_veh(
        self,
        veh: VehicleAgent,
        ped_list: list[PedestrianAgent],
    ) -> VehicleObservationResult:
        return VehicleObservationResult(
            veh_id=veh.veh_id,
            has_pedestrian=bool(ped_list),
            observed_pedestrians=[
                self._build_observed_pedestrian_result(ped)
                for ped in ped_list
            ],
        )

    def _build_observed_pedestrian_result(
        self,
        ped: PedestrianAgent,
    ) -> ObservedPedestrianResult:
        return ObservedPedestrianResult(
            ped_id=ped.ped_id,
            ped_pos_x=ped.pos_x,
            ped_pos_y=ped.pos_y,
            ped_speed=ped.speed,
            is_pass=ped.is_pass,
        )
