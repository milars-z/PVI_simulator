from __future__ import annotations

import math
from collections.abc import Callable

from agents.ped_agent import PedestrianAgent
from agents.veh_agent import VehicleAgent
from world.world import World


RecorderValue = bool | int | float | str | None
RunningUpdateStep = Callable[
    [dict[str, RecorderValue], VehicleAgent, PedestrianAgent, float],
    None,
]
FinalUpdateStep = Callable[[dict[str, RecorderValue], VehicleAgent], None]


class RecorderFun:
    """Calculation process used by Recorder."""

    def __init__(self) -> None:
        self.running_update_steps: list[RunningUpdateStep] = [
            self._update_min_distance,
            self._update_operation_summary,
            self._update_interaction_time,
            self._update_collision,
            self._update_yield_result,
        ]
        self.final_update_steps: list[FinalUpdateStep] = [
            self._update_final_speed,
            self._fill_default_yield_result,
        ]

    def get_main_vehicle(self, world: World) -> VehicleAgent | None:
        veh_list = world.get_veh_list()
        if len(veh_list) == 0:
            return None

        return veh_list[0]

    def get_main_pedestrian(self, world: World) -> PedestrianAgent | None:
        ped_list = world.get_ped_list()
        if len(ped_list) == 0:
            return None

        return ped_list[0]

    def build_initial_row(
        self,
        veh: VehicleAgent,
        ped: PedestrianAgent,
        epoch_id: int,
        round_id: int,
    ) -> dict[str, RecorderValue]:
        return {
            "epoch_id": epoch_id,
            "round_id": round_id,
            "veh_id": veh.veh_id,
            "veh_spawn_x": veh.distance_to_crossroad_m,
            "veh_spawn_y": veh.spawn_y,
            "veh_init_speed": veh.init_speed_mps,
            "ped_id": ped.ped_id,
            "ped_type": ped.ped_type,
            "ped_speed": ped.ped_speed,
            "is_collision": False,
            "min_distance": float("inf"),
            "veh_speed_at_min_distance": None,
            "max_abs_jerk": 0.0,
            "max_deceleration": 0.0,
            "veh_mean_speed": 0.0,
            "_veh_speed_time_sum": 0.0,
            "_veh_speed_duration": 0.0,
            "interaction_time": 0.0,
            "is_yield_to_ped": None,
            "veh_final_speed": None,
        }

    def update_running_row(
        self,
        row: dict[str, RecorderValue],
        veh: VehicleAgent,
        ped: PedestrianAgent,
        dt: float,
    ) -> None:
        for step in self.running_update_steps:
            step(row, veh, ped, dt)

    def finish_row(
        self,
        row: dict[str, RecorderValue],
        veh: VehicleAgent,
    ) -> None:
        for step in self.final_update_steps:
            step(row, veh)

    def _update_min_distance(
        self,
        row: dict[str, RecorderValue],
        veh: VehicleAgent,
        ped: PedestrianAgent,
        dt: float,
    ) -> None:
        current_distance = self.calculate_edge_distance(veh, ped)
        min_distance = self._get_float(row, "min_distance")

        if current_distance < min_distance:
            row["min_distance"] = current_distance
            row["veh_speed_at_min_distance"] = veh.speed

    def _update_operation_summary(
        self,
        row: dict[str, RecorderValue],
        veh: VehicleAgent,
        ped: PedestrianAgent,
        dt: float,
    ) -> None:
        row["max_abs_jerk"] = max(
            self._get_float(row, "max_abs_jerk"),
            abs(veh.jerk),
        )
        row["max_deceleration"] = max(
            self._get_float(row, "max_deceleration"),
            max(0.0, -veh.acceleration),
        )

        duration = max(0.0, dt)
        if duration <= 0.0:
            return

        speed_time_sum = (
            self._get_float(row, "_veh_speed_time_sum")
            + veh.speed * duration
        )
        speed_duration = self._get_float(row, "_veh_speed_duration") + duration

        row["_veh_speed_time_sum"] = speed_time_sum
        row["_veh_speed_duration"] = speed_duration
        row["veh_mean_speed"] = speed_time_sum / speed_duration

    def _update_interaction_time(
        self,
        row: dict[str, RecorderValue],
        veh: VehicleAgent,
        ped: PedestrianAgent,
        dt: float,
    ) -> None:
        row["interaction_time"] = self._get_float(row, "interaction_time") + max(
            0.0,
            dt,
        )

    def _update_collision(
        self,
        row: dict[str, RecorderValue],
        veh: VehicleAgent,
        ped: PedestrianAgent,
        dt: float,
    ) -> None:
        if self.is_collision(veh, ped):
            row["is_collision"] = True

    def _update_yield_result(
        self,
        row: dict[str, RecorderValue],
        veh: VehicleAgent,
        ped: PedestrianAgent,
        dt: float,
    ) -> None:
        if row["is_yield_to_ped"] is None and self.has_vehicle_reached_crosswalk(veh):
            row["is_yield_to_ped"] = self.is_yield_to_ped(veh, ped)

    def _update_final_speed(
        self,
        row: dict[str, RecorderValue],
        veh: VehicleAgent,
    ) -> None:
        row["veh_final_speed"] = veh.speed

    def _fill_default_yield_result(
        self,
        row: dict[str, RecorderValue],
        veh: VehicleAgent,
    ) -> None:
        if row["is_yield_to_ped"] is None:
            row["is_yield_to_ped"] = False

    def calculate_center_distance(
        self,
        veh: VehicleAgent,
        ped: PedestrianAgent,
    ) -> float:
        dx = veh.pos_x - ped.pos_x
        dy = veh.pos_y - ped.pos_y

        return math.hypot(dx, dy)

    def calculate_edge_distance(
        self,
        veh: VehicleAgent,
        ped: PedestrianAgent,
    ) -> float:
        veh_left = veh.pos_x - veh.size_x / 2.0
        veh_right = veh.pos_x + veh.size_x / 2.0
        veh_bottom = veh.pos_y - veh.size_y / 2.0
        veh_top = veh.pos_y + veh.size_y / 2.0

        ped_left = ped.pos_x - ped.size_x / 2.0
        ped_right = ped.pos_x + ped.size_x / 2.0
        ped_bottom = ped.pos_y - ped.size_y / 2.0
        ped_top = ped.pos_y + ped.size_y / 2.0

        if veh_right < ped_left:
            dx = ped_left - veh_right
        elif ped_right < veh_left:
            dx = veh_left - ped_right
        else:
            dx = 0.0

        if veh_top < ped_bottom:
            dy = ped_bottom - veh_top
        elif ped_top < veh_bottom:
            dy = veh_bottom - ped_top
        else:
            dy = 0.0

        return math.hypot(dx, dy)

    def is_collision(
        self,
        veh: VehicleAgent,
        ped: PedestrianAgent,
    ) -> bool:
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

    def has_vehicle_reached_crosswalk(self, veh: VehicleAgent) -> bool:
        return veh.pos_x >= veh.stop_x

    def is_yield_to_ped(
        self,
        veh: VehicleAgent,
        ped: PedestrianAgent,
    ) -> bool:
        if not self.has_vehicle_reached_crosswalk(veh):
            return False

        return ped.is_pass

    def _get_float(
        self,
        row: dict[str, RecorderValue],
        key: str,
    ) -> float:
        value = row[key]
        if not isinstance(value, float):
            raise TypeError(f"Recorder field {key} must be a float.")

        return value
