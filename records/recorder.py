from __future__ import annotations

import csv
from pathlib import Path

from agents.ped_agent import PedestrianAgent
from agents.veh_agent import VehicleAgent
from configs.recorder_config import RECORDER_CONFIG, RecorderConfig
from records.recorder_fun import RecorderFun, RecorderValue
from world.world import World


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Record content definition.
# Add, remove, or reorder CSV columns here.
RECORD_FIELDS: list[str] = [
    "epoch_id",
    "round_id",
    "veh_id",
    "veh_spawn_x",
    "veh_spawn_y",
    "veh_init_speed",
    "ped_id",
    "ped_type",
    "ped_speed",
    "is_collision",
    "min_distance",
    "veh_speed_at_min_distance",
    "max_abs_jerk",
    "max_deceleration",
    "veh_mean_speed",
    "interaction_time",
    "is_yield_to_ped",
    "veh_final_speed",
]

FormattedRecorderValue = bool | int | float | str | None


class Recorder:
    def __init__(self) -> None:
        self.config: RecorderConfig = RECORDER_CONFIG
        self.enabled = self.config["enabled"]
        self.output_dir = self._build_output_dir()
        self.csv_path = self.output_dir / str(self.config["csv_filename"])
        self.round_digits = int(self.config["round_digits"])
        self.fieldnames = RECORD_FIELDS

        self.fun = RecorderFun()
        self.current_epoch_id: int | None = None
        self.current_round_id: int | None = None
        self.is_active = False
        self.is_written = False
        self.current_row: dict[str, RecorderValue] = {}

        self._init_output()

    def record(
        self,
        world: World,
        dt: float = 0.0,
    ) -> None:
        if not self.enabled:
            return

        veh = self.fun.get_main_vehicle(world)
        ped = self.fun.get_main_pedestrian(world)

        if veh is None or ped is None:
            return

        if self._is_new_round(world.now_epoch, world.now_round):
            self._start_round(
                veh=veh,
                ped=ped,
                epoch_id=world.now_epoch,
                round_id=world.now_round,
            )

        self._update_running_metrics(veh=veh, ped=ped, dt=dt)

        if world.is_round_finished():
            self._write_round_result(veh)

    def finish_round(
        self,
        world: World,
        dt: float = 0.0,
    ) -> None:
        if not self.enabled:
            return

        veh = self.fun.get_main_vehicle(world)
        ped = self.fun.get_main_pedestrian(world)

        if veh is None or ped is None:
            return

        if self._is_new_round(world.now_epoch, world.now_round):
            self._start_round(
                veh=veh,
                ped=ped,
                epoch_id=world.now_epoch,
                round_id=world.now_round,
            )

        self._update_running_metrics(veh=veh, ped=ped, dt=dt)
        self._write_round_result(veh)

    def _is_new_round(
        self,
        epoch_id: int,
        round_id: int,
    ) -> bool:
        return (
            self.current_epoch_id != epoch_id
            or self.current_round_id != round_id
        )

    def _start_round(
        self,
        veh: VehicleAgent,
        ped: PedestrianAgent,
        epoch_id: int,
        round_id: int,
    ) -> None:
        self.current_epoch_id = epoch_id
        self.current_round_id = round_id
        self.is_active = True
        self.is_written = False
        self.current_row = self.fun.build_initial_row(
            veh=veh,
            ped=ped,
            epoch_id=epoch_id,
            round_id=round_id,
        )

    def _update_running_metrics(
        self,
        veh: VehicleAgent,
        ped: PedestrianAgent,
        dt: float,
    ) -> None:
        if not self.is_active or self.is_written:
            return

        self.fun.update_running_row(
            row=self.current_row,
            veh=veh,
            ped=ped,
            dt=dt,
        )

    def _write_round_result(self, veh: VehicleAgent) -> None:
        if not self.is_active or self.is_written:
            return

        self.fun.finish_row(row=self.current_row, veh=veh)
        self._append_row(self._format_row(self.current_row))
        self.is_written = True
        self.is_active = False

    def _init_output(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if self.csv_path.exists() and self._has_current_header():
            return

        with self.csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()

    def _has_current_header(self) -> bool:
        with self.csv_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)

        return header == self.fieldnames

    def _append_row(self, row: dict[str, FormattedRecorderValue]) -> None:
        self._init_output()

        with self.csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(row)

    def _build_output_dir(self) -> Path:
        output_dir = Path(self.config["output_dir"])

        if output_dir.is_absolute():
            return output_dir

        return PROJECT_ROOT / output_dir

    def _format_row(
        self,
        row: dict[str, RecorderValue],
    ) -> dict[str, FormattedRecorderValue]:
        formatted: dict[str, FormattedRecorderValue] = {}

        for key in self.fieldnames:
            value = row.get(key)

            if isinstance(value, float):
                formatted[key] = self._format_float(value)
            else:
                formatted[key] = value

        return formatted

    def _format_float(self, value: float) -> float | str:
        if value == float("inf"):
            return "inf"

        return round(value, self.round_digits)
