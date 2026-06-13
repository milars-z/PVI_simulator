# observations/veh_observation.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from agents.agent_enums import AgentType


@dataclass
class ObservedPedestrianResult:
    """
    单个车辆视角下，观测到的一个行人信息。
    """

    ped_id: int

    ped_pos_x: float
    ped_pos_y: float

    ped_speed: float

    cross_probability: float
    focus_probability: float
    is_pass: float


@dataclass
class VehicleObservationResult:
    """
    单个车辆的观测结果。

    一个 VehicleObservationResult 对应一辆车。
    observed_pedestrians 中保存该车观测到的所有行人。
    """

    veh_id: int

    has_pedestrian: bool = False
    pedestrian_ids: list[int] = field(default_factory=list)

    observed_pedestrians: list[ObservedPedestrianResult] = field(
        default_factory=list
    )


class VehicleObservation:
    """
    Vehicle observation.

    只负责：
    - 从 world 中读取 veh 和 ped
    - 计算每个 veh 视角下看到的行人信息
    - 返回 VehicleObservationResult list

    当前版本：
    - 车辆只观察行人
    - 不观察其他车辆
    - 不负责修改 veh state
    - 不负责修改 ped state
    - 不负责车辆决策
    """

    def __init__(self) -> None:
        self.results: list[VehicleObservationResult] = []

    def update(self, world) -> list[VehicleObservationResult]:
        self.results.clear()

        ped_list = []
        veh_list = []

        for agent in world.agent_list:
            if agent.type == AgentType.PEDESTRIAN:
                ped_list.append(agent)
            elif agent.type == AgentType.VEHICLE:
                veh_list.append(agent)

        for veh in veh_list:
            result = self._observe_veh(
                veh=veh,
                ped_list=ped_list,
            )
            self.results.append(result)

        return self.results

    def to_dict(
        self,
        results: Optional[list[VehicleObservationResult]] = None,
    ) -> dict[int, VehicleObservationResult]:
        if results is None:
            results = self.results

        return {
            result.veh_id: result
            for result in results
        }

    # --------------------------------------------------
    # Observe one vehicle
    # --------------------------------------------------

    def _observe_veh(
        self,
        veh,
        ped_list,
    ) -> VehicleObservationResult:
        result = VehicleObservationResult(
            veh_id=veh.veh_id,
        )

        if not ped_list:
            return result

        for ped in ped_list:
            observed_ped = self._build_observed_pedestrian_result(ped)

            result.observed_pedestrians.append(observed_ped)
            result.pedestrian_ids.append(ped.ped_id)

        result.has_pedestrian = len(result.observed_pedestrians) > 0

        return result

    def _build_observed_pedestrian_result(
        self,
        ped,
    ) -> ObservedPedestrianResult:
        """
        构建车辆视角下的单个行人观测结果。

        当前直接读取 PedestrianAgent 中已有成员：
        - pos_x
        - pos_y
        - speed
        - cross_probability
        - focus_probability
        - is_pass
        """

        return ObservedPedestrianResult(
            ped_id=ped.ped_id,

            ped_pos_x=ped.pos_x,
            ped_pos_y=ped.pos_y,

            ped_speed=ped.speed,

            cross_probability=ped.cross_probability,
            focus_probability=ped.focus_probability,
            is_pass=ped.is_pass,
        )