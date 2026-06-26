# records/recorder.py

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from configs.recorder_config import RECORDER_CONFIG
from records.recorder_fun import RecorderFun


class Recorder:
    """
    pygame画面渲染
    """

    def __init__(self) -> None:
        self.config = RECORDER_CONFIG

        self.csv_path = Path(self.config["csv_path"])
        self.fieldnames = self.config["fieldnames"]
        self.round_digits = self.config["round_digits"]

        self.fun = RecorderFun()

        self.current_epoch_id: int | None = None
        self.current_round_id: int | None = None

        self.is_active = False
        self.is_written = False

        self.current_row: dict[str, Any] = {}

        self._init_csv()

    # --------------------------------------------------
    # public API
    # --------------------------------------------------

    def record(
        self,
        world: Any,
    ) -> None:
        """
        每一帧调用一次。

        只更新当前 round 的过程指标。
        不在这里写 CSV。
        """

        round_id = world.now_round
        epoch_id = world.now_epoch

        veh = self.fun.get_main_vehicle(world)
        ped = self.fun.get_main_pedestrian(world)

        if veh is None or ped is None:
            return

        if self._is_new_round(epoch_id, round_id):
            self._start_round(
                veh=veh,
                ped=ped,
                epoch_id=epoch_id,
                round_id=round_id,
            )

        self._update_running_metrics(veh, ped)

        if self._is_round_finished(world):
            self._write_round_result(veh)

    def finish_round(
        self,
        world: Any,
    ) -> None:
        """
        每个 round 结束时，由外部显式调用一次。

        这个函数负责写入一行 CSV。
        """

        round_id = world.now_round
        epoch_id = world.now_epoch

        veh = self.fun.get_main_vehicle(world)
        ped = self.fun.get_main_pedestrian(world)

        if veh is None or ped is None:
            return

        if self._is_new_round(epoch_id, round_id):
            self._start_round(
                veh=veh,
                ped=ped,
                epoch_id=epoch_id,
                round_id=round_id,
            )

        self._update_running_metrics(veh, ped)
        self._write_round_result(veh)

    # --------------------------------------------------
    # round lifecycle
    # --------------------------------------------------

    def _is_new_round(
        self,
        epoch_id: int,
        round_id: int,
    ) -> bool:
        return (
            self.current_epoch_id != epoch_id
            or self.current_round_id != round_id
        )

    def _is_round_finished(self, world: Any) -> bool:
        if not hasattr(world, "is_round_finished"):
            return False

        return world.is_round_finished()

    def _start_round(
        self,
        veh: Any,
        ped: Any,
        epoch_id: int,
        round_id: int,
    ) -> None:
        self.current_epoch_id = epoch_id
        self.current_round_id = round_id

        self.is_active = True
        self.is_written = False

        self.current_row = {
            "epoch_id": epoch_id,
            "round_id": round_id,

            "veh_id": veh.veh_id,
            "veh_spawn_x": veh.distance_to_crossroad_m,
            "veh_init_speed": veh.init_speed_mps,

            "ped_id": ped.ped_id,
            "ped_type": ped.ped_type,
            "ped_speed": ped.ped_speed,

            "is_collision": False,
            "min_distance": float("inf"),
            "veh_speed_at_min_distance": None,

            # None 表示车还没到达人行道
            # True / False 表示第一次到达人行道时是否礼让成功
            "is_yield_to_ped": None,

            "veh_final_speed": None,
        }

    def _update_running_metrics(self, veh: Any, ped: Any) -> None:
        if not self.is_active:
            return

        if self.is_written:
            return

        current_distance = self.fun.calculate_center_distance(veh, ped)

        if current_distance < self.current_row["min_distance"]:
            self.current_row["min_distance"] = current_distance
            self.current_row["veh_speed_at_min_distance"] = veh.speed

        if self.fun.is_collision(veh, ped):
            self.current_row["is_collision"] = True

        # 只记录车辆第一次到达人行道时的礼让结果
        if self.current_row["is_yield_to_ped"] is None:
            if self.fun.has_vehicle_reached_crosswalk(veh):
                self.current_row["is_yield_to_ped"] = self.fun.is_yield_to_ped(
                    veh,
                    ped,
                )

    def _write_round_result(self, veh: Any) -> None:
        if not self.is_active:
            return

        if self.is_written:
            return

        self.current_row["veh_final_speed"] = veh.speed

        if self.current_row["is_yield_to_ped"] is None:
            self.current_row["is_yield_to_ped"] = False

        row = self._format_row(self.current_row)
        self._append_row(row)

        self.is_written = True
        self.is_active = False

    # --------------------------------------------------
    # csv
    # --------------------------------------------------

    def _init_csv(self) -> None:
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        if self.csv_path.exists():
            return

        with self.csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()

    def _append_row(self, row: dict[str, Any]) -> None:
        with self.csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(row)

    # --------------------------------------------------
    # utils
    # --------------------------------------------------

    def _format_row(self, row: dict[str, Any]) -> dict[str, Any]:
        formatted = {}

        for key in self.fieldnames:
            value = row.get(key)

            if isinstance(value, float):
                if value == float("inf"):
                    formatted[key] = "inf"
                else:
                    formatted[key] = round(value, self.round_digits)
            else:
                formatted[key] = value

        return formatted
