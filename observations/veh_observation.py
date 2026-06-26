# observations/veh_observation.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from agents.agent_enums import AgentType

import math


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

    is_collision: bool

    dis_to_ped_x: float

    dis_to_ped : float


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
            observed_ped.is_collision = self._is_collision(veh,ped)
            observed_ped.dis_to_ped_x = self._calculate_dis_to_ped_x(veh,ped)
            observed_ped.dis_to_ped   = self._get_distance_between_vehicle_and_ped(veh,ped)

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
            is_collision = False,
            dis_to_ped_x = 0.0,
            dis_to_ped = 0.0,
        )
    

    def _is_collision(self, veh, ped) -> bool:
        """
        中心点 + size_x / size_y 的 AABB 碰撞检测。
        """

        veh_left = veh.pos_x - veh.size_x / 2.0
        veh_right = veh.pos_x + veh.size_x / 2.0
        veh_bottom = veh.pos_y - veh.size_y / 2.0
        veh_top = veh.pos_y + veh.size_y / 2.0

        ped_left = ped.pos_x - ped.size_x / 2.0
        ped_right = ped.pos_x + ped.size_x / 2.0
        ped_bottom = ped.pos_y - ped.size_y / 2.0
        ped_top = ped.pos_y + ped.size_y / 2.0

        overlap_x = veh_left <= ped_right and veh_right >= ped_left
        overlap_y = veh_bottom <= ped_top and veh_top >= ped_bottom

        return overlap_x and overlap_y
    

    def _calculate_dis_to_ped_x(self,veh,ped) -> float:

        return float(ped.pos_x - veh.pos_x)
    
    def _get_distance_between_vehicle_and_ped(
        self,
        veh,
        ped,
    ) -> float:
        """
        计算车辆和行人 AABB 边界之间的最短直线距离。
        """

        veh_left = veh.pos_x - veh.size_x / 2.0
        veh_right = veh.pos_x + veh.size_x / 2.0
        veh_bottom = veh.pos_y - veh.size_y / 2.0
        veh_top = veh.pos_y + veh.size_y / 2.0

        ped_left = ped.pos_x - ped.size_x / 2.0
        ped_right = ped.pos_x + ped.size_x / 2.0
        ped_bottom = ped.pos_y - ped.size_y / 2.0
        ped_top = ped.pos_y + ped.size_y / 2.0

        # x 方向的间距
        if veh_right < ped_left:
            dx = ped_left - veh_right
        elif ped_right < veh_left:
            dx = veh_left - ped_right
        else:
            dx = 0.0

        # y 方向的间距
        if veh_top < ped_bottom:
            dy = ped_bottom - veh_top
        elif ped_top < veh_bottom:
            dy = veh_bottom - ped_top
        else:
            dy = 0.0

        return math.sqrt(dx * dx + dy * dy)
