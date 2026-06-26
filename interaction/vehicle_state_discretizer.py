# interaction/vehicle_state_discretizer.py

from __future__ import annotations

from typing import Any

import csv
from pathlib import Path

# from interaction.bin_cutter import BinCutter
from interaction.bin_cutter import bin_cut
from interaction.vehicle_state_bin_config import VEHICLE_STATE_BIN_RULES

from observations.veh_observation import ObservedPedestrianResult
from agents.veh_agent import VehicleAgent


class VehicleStateDiscretizer:
    """

    """

    def __init__(
        self,
        csv_path: str = "records/discrete_state.csv",
    ) -> None:
        self.csv_path = Path(csv_path)
        self._init_csv()

    def discretize(
        self,
        veh_obs: ObservedPedestrianResult,
        veh: VehicleAgent,
    ) -> list[int]:
        state_data = self.extract_state_data(
            veh_obs=veh_obs,
            veh=veh,
        )

        discrete_state: list[int] = []

        for rule in VEHICLE_STATE_BIN_RULES:
            if rule.key not in state_data:
                raise KeyError(
                    f"Missing state data for key: {rule.key}"
                )

            value = float(state_data[rule.key])

            discrete_value = bin_cut(
                value=value,
                bins=rule.bins,
            )

            discrete_state.append(discrete_value)

        # self._write_discrete_state(discrete_state)

        return discrete_state

    def _init_csv(self) -> None:
        """

        """
        self.csv_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if self.csv_path.exists():
            return

        with self.csv_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)

            header = [
                f"state_{i}"
                for i in range(len(VEHICLE_STATE_BIN_RULES))
            ]

            writer.writerow(header)


    def _write_discrete_state(
        self,
        discrete_state: list[int],
    ) -> None:
        """
        将离散状态 list 写入 CSV。

        example:
            [5, 3, 4, 2, 0, 5, 0]
        """
        with self.csv_path.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)
            writer.writerow(discrete_state)


    def extract_state_data(
        self,
        veh_obs: ObservedPedestrianResult,
        veh: VehicleAgent,
    ) -> dict[str, float | int]:
        """
        观测量提取
        """

        distance_x = self._calculate_distance_x(
            veh_obs=veh_obs,
            veh=veh,
        )

        distance_y = self._calculate_distance_y(
            veh_obs=veh_obs,
            veh=veh,
        )

        veh_speed = self._get_veh_speed(veh)
        ped_speed = self._get_ped_speed(veh_obs)
        ped_persona = self._get_ped_persona(veh_obs)
        veh_acc = self._get_veh_acc(veh)

        stopping_ratio = self._calculate_stopping_ratio(
            veh_obs=veh_obs,
            veh=veh,
        )

        return {
            "distance_x": distance_x,
            "distance_y": distance_y,
            "veh_speed": veh_speed,
            "ped_speed": ped_speed,
            "ped_persona": ped_persona,
            "veh_acc": veh_acc,
            "stopping_ratio": stopping_ratio,
        }

    # --------------------------------------------------
    # Distance calculation
    # --------------------------------------------------

    def _calculate_distance_x(
        self,
        veh_obs: ObservedPedestrianResult,
        veh: VehicleAgent,
    ) -> float:
        """
        车辆距离碰撞点的距离
        """

        return float(veh_obs.ped_pos_x - veh.pos_x)

    def _calculate_distance_y(
        self,
        veh_obs: ObservedPedestrianResult,
        veh: VehicleAgent,
    ) -> float:
        """
        行人距离碰撞点的距离
        """

        dis = veh_obs.ped_pos_y - veh.pos_y - veh.size_y/2

        return dis

    # --------------------------------------------------
    # Raw value getters
    # --------------------------------------------------

    def _get_veh_speed(
        self,
        veh: VehicleAgent,
    ) -> float:
        
        speed  = veh.speed

        return speed

    def _get_ped_speed(
        self,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        
        ped_speed = veh_obs.ped_speed

        return ped_speed

    def _get_ped_persona(
        self,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        """
        不同人格配置,暂时设计为0,测试单一人格
        """

        return 0

    def _get_veh_acc(
        self,
        veh: VehicleAgent,
    ) -> float:
        
        acc = veh.acceleration

        return acc

    # --------------------------------------------------
    # Derived value
    # --------------------------------------------------

    def _calculate_stopping_ratio(
        self,
        veh_obs: ObservedPedestrianResult,
        veh: VehicleAgent,
    ) -> int:
        """
        判断当前情况下是否可以在正常减速度范围内刹住。

        """

        max_acc = veh.max_deceleration
        
        distance_to_stoppoint = veh.stop_x - veh.pos_x  ##距离推荐停车点的距离

        ## 
        ratio = veh.speed * veh.speed / (2.0 * max_acc * distance_to_stoppoint)

        return ratio
