# observations/ped_observation.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import math

from agents.agent_enums import Orientation
from agents.agent_enums import AgentType


@dataclass
class ObservedVehicleResult:
    """
    单个行人视角下，观测到的一辆车信息。
    """

    veh_id: int

    has_vehicle: bool

    distance: float
    ttc_gap: float
    stopping_ratio: float

    car_speed_view: float

    car_pos_x: float
    car_pos_y: float


@dataclass
class PedestrianObservationResult:
    """
    单个行人的观测结果。
    """

    ped_id: int

    has_vehicle: bool = False
    nearest_vehicle_id: Optional[int] = None

    vehicle_ids: list[int] = field(default_factory=list)

    observed_vehicles: list[ObservedVehicleResult] = field(
        default_factory=list
    )


class PedestrianObservation:
    """
    Pedestrian observation.

    """

    def __init__(self) -> None:
        self.results: list[PedestrianObservationResult] = []

    def update(self, world) -> list[PedestrianObservationResult]:
        self.results.clear()

        ped_list = []
        veh_list = []

        for agent in world.agent_list:
            if agent.type == AgentType.PEDESTRIAN:
                ped_list.append(agent)
            elif agent.type == AgentType.VEHICLE:
                veh_list.append(agent)

        for ped in ped_list:
            result = self._observe_ped(
                ped=ped,
                veh_list=veh_list,
            )
            self.results.append(result)

        return self.results

    def to_dict(
        self,
        results: Optional[list[PedestrianObservationResult]] = None,
    ) -> dict[int, PedestrianObservationResult]:
        if results is None:
            results = self.results

        return {
            result.ped_id: result
            for result in results
        }

    # --------------------------------------------------
    # Observe one pedestrian
    # --------------------------------------------------

    def _observe_ped(
        self,
        ped,
        veh_list,
    ) -> PedestrianObservationResult:
        result = PedestrianObservationResult(
            ped_id=ped.ped_id,
        )

        if not veh_list:
            return result

        observed_vehicles: list[ObservedVehicleResult] = []

        for veh in veh_list:
            observed_vehicle = self._build_observed_vehicle_result(
                ped=ped,
                veh=veh,
            )
            observed_vehicles.append(observed_vehicle)

        if not observed_vehicles:
            return result

        observed_vehicles.sort(
            key=lambda item: item.distance
        )

        result.observed_vehicles = observed_vehicles
        result.vehicle_ids = [
            item.veh_id
            for item in observed_vehicles
        ]

        result.nearest_vehicle_id = observed_vehicles[0].veh_id

        result.has_vehicle = any(
            item.has_vehicle
            for item in observed_vehicles
        )

        return result

    def _build_observed_vehicle_result(
        self,
        ped,
        veh,
    ) -> ObservedVehicleResult:
        """
        构建单个行人视角下的一辆车观测结果。
        """

        return ObservedVehicleResult(
            veh_id=veh.veh_id,

            has_vehicle=self._is_vehicle_in_ped_view(
                ped=ped,
                veh=veh,
            ),

            distance=self._calculate_distance_to_vehicle(
                ped=ped,
                veh=veh,
            ),

            ttc_gap=self._calculate_ttc_gap(
                ped=ped,
                veh=veh,
            ),

            stopping_ratio=self._calculate_stopping_ratio(
                veh=veh,
            ),

            car_speed_view=self._calculate_car_speed_view(
                veh=veh,
            ),

            car_pos_x=veh.pos_x,
            car_pos_y=veh.pos_y,
        )

    # --------------------------------------------------
    # Distance calculation
    # --------------------------------------------------

    def _is_vehicle_in_ped_view(
        self,
        ped,
        veh,
    ) -> bool:
        """
        判断车辆是否在行人视野范围内。

        判断车辆是否可能会阻碍行人过马路。
        当车尾已经穿过行人位置时，返回 False。
        """

        veh_left, veh_right, _, _ = self._get_vehicle_bounds(veh)

        if veh.orientation == Orientation.RIGHT:
            tail_x = veh_left

            if tail_x > ped.pos_x:
                return False

            return True

        if veh.orientation == Orientation.LEFT:
            tail_x = veh_right

            if tail_x < ped.pos_x:
                return False

            return True

        return False

    def _calculate_distance_to_vehicle(
        self,
        ped,
        veh,
    ) -> float:
        """
        计算行人到车身矩形的最近距离。

        当前逻辑：
        - 行人用 ped.pos_x, ped.pos_y 表示一个点
        - 车辆不能用中心点，必须用车身矩形
        - 如果行人点落在车辆矩形内部，距离为 0
        """

        veh_left, veh_right, veh_top, veh_bottom = self._get_vehicle_bounds(veh)

        nearest_x = self._clamp(
            value=ped.pos_x,
            min_value=veh_left,
            max_value=veh_right,
        )

        nearest_y = self._clamp(
            value=ped.pos_y,
            min_value=veh_top,
            max_value=veh_bottom,
        )

        return self._calculate_point_distance(
            x1=ped.pos_x,
            y1=ped.pos_y,
            x2=nearest_x,
            y2=nearest_y,
        )

    def _get_vehicle_bounds(
        self,
        veh,
    ) -> tuple[float, float, float, float]:
        """
        
        返回车辆矩形边界：
            left, right, top, bottom

        """

        half_length = veh.size_x / 2.0
        half_width = veh.size_y / 2.0

        left = veh.pos_x - half_length
        right = veh.pos_x + half_length
        top = veh.pos_y - half_width
        bottom = veh.pos_y + half_width

        return left, right, top, bottom

    def _calculate_point_distance(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> float:
        return math.hypot(x2 - x1, y2 - y1)

    def _clamp(
        self,
        value: float,
        min_value: float,
        max_value: float,
    ) -> float:
        return max(min_value, min(value, max_value))

    # --------------------------------------------------
    # Feature calculation
    # --------------------------------------------------

    def _calculate_ttc_gap(
        self,
        ped,
        veh,
    ) -> float:
        """
        计算车和行人到冲突点的时间差。

        冲突点：
            conflict_x = ped.pos_x
            conflict_y = veh.pos_y

        vehicle_time:
            车辆到达 conflict_x 所需时间

        pedestrian_time:
            行人到达 conflict_y 所需时间

        ttc_gap:
            vehicle_time - pedestrian_time

        如果车辆已经超过冲突点，或者行人已经超过冲突点，
        对应 time 返回 inf，最终 ttc_gap 返回 inf。
        """

        conflict_x = ped.pos_x
        conflict_y = veh.pos_y

        vehicle_time = self._calculate_time_to_conflict_point(
            current_pos=veh.pos_x,
            conflict_pos=conflict_x,
            speed=veh.speed,
            orientation=veh.orientation,
        )

        pedestrian_time = self._calculate_time_to_conflict_point(
            current_pos=ped.pos_y,
            conflict_pos=conflict_y,
            speed=ped.ped_speed,
            orientation=ped.orientation,
        )

        if math.isinf(vehicle_time) or math.isinf(pedestrian_time):
            return float("inf")

        return vehicle_time - pedestrian_time

    def _calculate_time_to_conflict_point(
        self,
        current_pos: float,
        conflict_pos: float,
        speed: float,
        orientation: Orientation,
    ) -> float:
        """
        计算 agent 沿当前方向到达冲突坐标所需时间。

        对于水平运动：
            RIGHT: current_pos < conflict_pos 才说明还没到
            LEFT:  current_pos > conflict_pos 才说明还没到

        对于垂直运动：
            DOWN: current_pos < conflict_pos 才说明还没到
            UP:   current_pos > conflict_pos 才说明还没到

        如果已经超过冲突点，返回 inf。
        """

        if speed <= 0.0:
            return float("inf")

        if orientation == Orientation.RIGHT:
            if current_pos >= conflict_pos:
                return float("inf")

            distance = conflict_pos - current_pos
            return distance / speed

        if orientation == Orientation.LEFT:
            if current_pos <= conflict_pos:
                return float("inf")

            distance = current_pos - conflict_pos
            return distance / speed

        if orientation == Orientation.DOWN:
            if current_pos >= conflict_pos:
                return float("inf")

            distance = conflict_pos - current_pos
            return distance / speed

        if orientation == Orientation.UP:
            if current_pos <= conflict_pos:
                return float("inf")

            distance = current_pos - conflict_pos
            return distance / speed

        return float("inf")

    def _calculate_stopping_ratio(
        self,
        veh,
    ) -> float:
        """
        stopping_ratio = stopping_distance / x_gap

        x_gap:
            车辆沿 x 方向到 veh.stop_x 的剩余距离。

        含义：
            < 1: 当前减速度下，车辆理论上能在停止线前停住
            = 1: 刚好停住
            > 1: 停车距离超过剩余 x 距离，风险更高
            inf: 车辆已经超过停止线，或车辆没有减速
        """

        x_gap = self._calculate_vehicle_x_gap_to_stop_point(
            veh=veh,
        )

        if x_gap <= 0.0:
            return float("inf")

        if veh.acceleration >= 0.0:
            return float("inf")

        deceleration = abs(veh.acceleration)

        if deceleration <= 0.0:
            return float("inf")

        stopping_distance = (veh.speed ** 2) / (2.0 * deceleration)

        return stopping_distance / x_gap

    def _calculate_vehicle_x_gap_to_stop_point(
        self,
        veh,
    ) -> float:
        """
        计算车辆沿 x 方向到 veh.stop_x 的剩余距离。

        veh.stop_x 在车辆初始化时设置，
        表示推荐的车辆停止点。
        """

        if veh.orientation == Orientation.RIGHT:
            if veh.pos_x >= veh.stop_x:
                return float("inf")

            return veh.stop_x - veh.pos_x

        if veh.orientation == Orientation.LEFT:
            if veh.pos_x <= veh.stop_x:
                return float("inf")

            return veh.pos_x - veh.stop_x

        return float("inf")

    def _calculate_car_speed_view(
        self,
        veh,
    ) -> float:
        """
        计算车辆在行人视角下的速度。

        当前直接返回车辆速度，单位 m/s。
        """

        return veh.speed