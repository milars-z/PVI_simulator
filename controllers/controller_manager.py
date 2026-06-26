# controllers/controller_manager.py

from __future__ import annotations

from typing import Any

from controllers.pedestrian_controller import PedestrianController
from controllers.vehicle_controller import VehicleController


class ControllerManager:
    """
    仿真控制器总入口。

    main.py 只调用 ControllerManager.update()。

    """

    def __init__(self) -> None:
        self.pedestrian = PedestrianController()
        self.vehicle = VehicleController()

    def update(
        self,
        dt: float,
        world: Any,
        observations: dict[str, Any],
    ) -> None:
        """
        更新所有控制器。

        Args:
            dt:
                当前仿真步长。
            world:
                仿真世界对象，用于获取 agent list。
            observations:
                当前 step 的观测结果集合。
        """

        ped_list = world.get_ped_list()
        veh_list = world.get_veh_list()
        

        ped_obs_list = observations.get("pedestrian", [])
        veh_obs_list = observations.get("vehicle", [])

        self.pedestrian.update(
            dt=dt,
            ped_list=ped_list,
            ped_obs_list=ped_obs_list,
        )

        self.vehicle.update(
            dt=dt,
            veh_list=veh_list,
            veh_obs_list=veh_obs_list,
        )

    def save_q_table(self):
        self.vehicle.save_q_table()