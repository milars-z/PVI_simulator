# records/recorder_fun.py

from __future__ import annotations

import math
from typing import Any


class RecorderFun:
    """
    RecorderFun 只负责计算评价指标。
    不负责保存状态，不负责写 CSV。
    """

    def get_main_vehicle(self, world: Any) -> Any | None:
        veh_list = world.get_veh_list()
        if len(veh_list) == 0:
            return None
        return veh_list[0]

    def get_main_pedestrian(self, world: Any) -> Any | None:
        ped_list = world.get_ped_list()
        if len(ped_list) == 0:
            return None
        return ped_list[0]

    def calculate_center_distance(self, veh: Any, ped: Any) -> float:
        """
        pos_x / pos_y 是中心点，因此直接计算中心点欧氏距离。
        """
        dx = veh.pos_x - ped.pos_x
        dy = veh.pos_y - ped.pos_y

        return math.hypot(dx, dy)

    def is_collision(self, veh: Any, ped: Any) -> bool:
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

    def has_vehicle_reached_crosswalk(self, veh: Any) -> bool:
        """
        判断车辆是否已经到达人行道/冲突点。

        当前 veh.stop_x 是车辆需要停车/穿越的人行道 x 坐标。
        当前默认车辆从左往右走。
        """
        return veh.pos_x >= veh.stop_x

    def is_yield_to_ped(self, veh: Any, ped: Any) -> bool:
        """
        礼让定义：
        车辆第一次到达人行道时，如果行人已经完成过马路，则认为礼让成功。
        """
        if not self.has_vehicle_reached_crosswalk(veh):
            return False

        return ped.is_finished()