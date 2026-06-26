# interaction/vehicle_cost.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from interaction.vehicle_cost_config import (
    VEHICLE_COST_CONFIG,
    VEHICLE_COST_ITEMS,
    VEHICLE_COST_WEIGHTS,
)

from observations.veh_observation import ObservedPedestrianResult
from agents.veh_agent import VehicleAgent


@dataclass(frozen=True)
class VehicleCostResult:
    """
    单帧车辆 cost 结果。

    total_cost:
        加权后的总 cost，用于 Q-table 更新。

    raw_costs:
        每一项未加权 cost，范围通常为 0~1。

    weighted_costs:
        每一项加权后的 cost。
    """

    total_cost: float
    raw_costs: dict[str, float]
    weighted_costs: dict[str, float]


class VehicleCostCalculator:
    """
    车辆单帧 cost 计算器。

    输入：
        veh:
            当前车辆 agent。

        veh_obs:
            当前车辆对某一个行人的观测结果。

    输出：
        VehicleCostResult

    当前包含：
        1. collision_cost
        2. near_speed_cost
        3. ttc_conflict_cost
        4. stopping_feasibility_cost
        5. early_slowdown_cost
        6. jerk_cost
        7. deceleration_cost
    """

    def __init__(
        self
    ) -> None:
        self.cost_items = VEHICLE_COST_ITEMS
        self.cost_weights = VEHICLE_COST_WEIGHTS
        self.config = VEHICLE_COST_CONFIG

        #记录jerk变化
        self.past_jerk = 0.0

    def calculate(
        self,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
    # ) -> VehicleCostResult:
    ) -> float:
        """
        计算当前帧 cost。
        """

        raw_costs: dict[str, float] = {}

        for cost_name in self.cost_items:
            if cost_name == "collision_cost":
                raw_costs[cost_name] = self._collision_cost(veh_obs)

            elif cost_name == "near_speed_cost":
                raw_costs[cost_name] = self._near_speed_cost(veh, veh_obs)

            elif cost_name == "ttc_conflict_cost":
                raw_costs[cost_name] = self._ttc_conflict_cost(veh, veh_obs)

            elif cost_name == "stopping_feasibility_cost":
                raw_costs[cost_name] = self._stopping_feasibility_cost(veh, veh_obs)

            elif cost_name == "early_slowdown_cost":
                raw_costs[cost_name] = self._early_slowdown_cost(veh, veh_obs)

            elif cost_name == "jerk_cost":
                raw_costs[cost_name] = self._jerk_cost(veh, veh_obs)

            elif cost_name == "deceleration_cost":
                raw_costs[cost_name] = self._deceleration_cost(veh, veh_obs)

            else:
                raise ValueError(f"Unknown vehicle cost name: {cost_name}")

        weighted_costs = self._apply_weights(raw_costs)
        total_cost = sum(weighted_costs.values())

        return total_cost

        return VehicleCostResult(
            total_cost=total_cost,
            raw_costs=raw_costs,
            weighted_costs=weighted_costs,
        )

    # ============================================================
    # Cost functions
    # ============================================================

    def _collision_cost(
        self,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        """
        是否碰撞。

        推荐后续在 veh_obs 或 world collision checker 中提供：
            veh_obs.is_collision
        """

        is_collision = veh_obs.is_collision

        return 1.0 if is_collision else 0.0

    def _near_speed_cost(
        self,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        """
        近距离高速 cost。

        含义：
            行人越近，车辆速度越高，cost 越大。

        额外加入 cross_probability：
            如果行人完全没有过马路意愿，则降低该 cost。
        """

        distance_to_ped = veh_obs.dis_to_ped
        veh_speed = veh.speed

        distance_risk = self._normalize_distance_risk(distance_to_ped)

        speed_risk = self._normalize_speed_risk(veh_speed)

        return distance_risk * speed_risk

    def _ttc_conflict_cost(
        self,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        """
        TTC 冲突 cost。

        含义：
            车辆和行人到达冲突点的时间差越小，cost 越高。

        依赖：
            veh_obs.ttc_gap
        """

        speed = max(1e-6,veh.speed)

        ttc_veh = veh_obs.dis_to_ped_x / speed

        ttc_ped = veh.pos_y - veh_obs.ped_pos_y - veh.size_y/2.0

        ttc_gap = ttc_veh - ttc_ped

        if ttc_gap == float("inf"):
            return 0.0
        
        ttc_gap = abs(float(ttc_gap))

        ttc_risk  = self._normalize_ttc_risk(ttc_gap)

        return ttc_risk 

    def _stopping_feasibility_cost(
        self,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        """
        停车可行性 cost。

        cost的设计需要车学会主动减速直到能在碰撞点前停下

        """

        distance_to_stoppoint = veh.stop_x - veh.pos_x  ##距离推荐停车点的距离

        acc = max(1e-6,abs(veh.acceleration))

        ratio = veh.speed * veh.speed / (2.0 * acc * distance_to_stoppoint)

        ratio_risk  = self._normalize_ratio_risk(ratio)

        return ratio_risk


    def _early_slowdown_cost(
        self,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        """
        过早低速 cost。

        限制车辆不要过早停下
        当车辆距离行人距离大于设定值时速度低于设定值会有惩罚

        设计车辆在stop_x处停下,如果超出这个值则会受到惩罚
        """

        veh_speed = veh.speed


        distance_to_stoppoint = veh.pos_x - veh.stop_x

        low_speed_threshold = self.config["low_speed_threshold_mps"]
        early_stop_distance = self.config["early_stop_distance_m"]

        if veh_speed >= low_speed_threshold:
            return 0.0

        if distance_to_stoppoint <= early_stop_distance:
            return 0.0

        return 1.0


    def _jerk_cost(
        self,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        """
        jerk cost。

        只看当前帧 jerk 大小。

        jerk超出限制值会有cost
        jerk变大有惩罚
        """

        cost = 0.0
        jerk = abs(veh.jerk)

        if (self.past_jerk != 0.0)  and jerk > self.past_jerk:
            cost += 1

        self.past_jerk = jerk

        ## 惩罚cost超出阈值

        max_jerk = self.config["max_jerk_mps3"]
        accept_jerk = self.config["accept_jerk_mps3"]

        if jerk > accept_jerk:
            cost = cost + min(1.0,(jerk - accept_jerk) / (max_jerk - accept_jerk))

        return cost

    def _deceleration_cost(
        self,
        veh: VehicleAgent,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        """
        减速度 cost。

        """
        acceleration = veh.acceleration

        if acceleration >= 0.0:
            return 0.0
        
        else:
            acceleration = abs(acceleration)

        max_deceleration = self.config["max_deceleration_mps2"]  ## 4.0
        accept_deceleration = self.config["accept_deceleration_mps2"] ## 2.0

        if acceleration <= accept_deceleration:
            return 0.0
        
        else:
            cost = min(1.0, (acceleration - accept_deceleration) / (max_deceleration - accept_deceleration))
            return cost


    # ============================================================
    # Helper functions
    # ============================================================

    def _apply_weights(
        self,
        raw_costs: dict[str, float],
    ) -> dict[str, float]:
        weighted_costs: dict[str, float] = {}

        for cost_name, raw_value in raw_costs.items():
            weight = self.cost_weights.get(cost_name, 1.0)
            weighted_costs[cost_name] = raw_value * weight

        return weighted_costs


    def _get_distance_to_ped(
        self,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        
        return veh_obs.dis_to_ped_x

    def _get_distance_to_crosswalk(
        self,
        veh: Any,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        """
        优先从 veh 里拿距离人行道/冲突点的距离。
        如果 veh 没有，就尝试从 veh_obs 里拿。

        你现在 veh 里面可能有：
            distance_to_crossroad_m

        后续建议统一命名为：
            distance_to_crosswalk
        """

        value = self._get_value(
            obj=veh,
            names=[
                "distance_to_crosswalk",
                "distance_to_crossroad",
                "distance_to_crossroad_m",
            ],
            default=None,
        )

        if value is not None:
            return abs(float(value))

        value = self._get_value(
            obj=veh_obs,
            names=[
                "distance_to_crosswalk",
                "distance_to_crossroad",
                "distance_to_crossroad_m",
            ],
            default=float("inf"),
        )

        return abs(float(value))

    def _get_cross_probability(
        self,
        veh_obs: ObservedPedestrianResult,
    ) -> float:
        """
        veh_obs.cross_probability:
            行人过马路意愿。

        范围：
            0.0 ~ 1.0
        """

        cross_probability = veh_obs.cross_probability

        return self._clip_01(cross_probability)


    def _get_value(
        self,
        obj: Any,
        names: list[str],
        default: Any = None,
    ) -> Any:
        """
        从对象中按多个可能名字读取属性。

        这样可以兼容你现在还没完全统一的命名。
        """

        for name in names:
            if hasattr(obj, name):
                return getattr(obj, name)

        return default

    def _clip_01(
        self,
        value: float,
    ) -> float:
        return max(0.0, min(float(value), 1.0))
    
    def _normalize_distance_risk(
        self,
        distance_to_ped: float,
    ) -> float:
        """
        距离风险归一化。

        规则：
            distance = 0                  -> risk = 1
            distance = safe_distance      -> risk = 0
            distance > safe_distance      -> risk = 0

        含义：
            距离越近，风险越高。
        """

        safe_distance = float(self.config["safe_distance_m"])

        if safe_distance <= 0.0:
            raise ValueError("safe_distance_m must be greater than 0.0")

        distance = max(0.0, float(distance_to_ped))

        risk = 1.0 - distance / safe_distance

        return max(0.0, min(1.0, risk))
    
    def _normalize_speed_risk(
        self,
        veh_speed: float,
    ) -> float:
        """
        速度风险归一化。

        规则：
            speed <= safe_speed       -> risk = 0
            speed = 2 * safe_speed    -> risk = 1
            speed > 2 * safe_speed    -> risk = 1

        含义：
            超过安全速度后，速度越高，风险越高。
        """

        safe_speed = float(self.config["safe_speed_mps"])

        if safe_speed <= 0.0:
            raise ValueError("safe_speed_mps must be greater than 0.0")

        speed = max(0.0, float(veh_speed))

        risk = (speed - safe_speed) / safe_speed

        return max(0.0, min(1.0, risk))
    
    def _normalize_ttc_risk(
        self,
        ttc: float,
    ) -> float:
        """
        TTC cost 非线性梯度函数。
        """

        min_ttc = float(self.config["min_ttc_s"])
        safe_ttc = float(self.config["safe_ttc_s"])

        if safe_ttc <= min_ttc:
            raise ValueError("safe_ttc_s must be greater than min_ttc_s")

        if ttc <= min_ttc:
            return 1.0

        if ttc >= safe_ttc:
            return 0.0

        linear_cost = (safe_ttc - ttc) / (safe_ttc - min_ttc)

        cost = linear_cost * linear_cost

        return max(0.0, min(1.0, cost))
    
    def _normalize_ratio_risk(
            self,
            ratio:float,
    ) -> float:
        '''
        stop ratio 非线性梯度函数。

        stop ratio = 1 代表刚好能停下
        stop ratio < 1 代表有盈余
        stop ratio > 1 代表速度很危险
        '''

        safe_ratio = float(self.config["safe_stopping_ratio"])
        danger_ratio = float(self.config["danger_stopping_ratio"])

        if ratio < safe_ratio:
            ratio_risk = 0.0

        elif ratio >= danger_ratio:
            ratio_risk = 1.0

        else:
            _ratio_risk = (ratio - safe_ratio) / ( danger_ratio - safe_ratio)
            ratio_risk = _ratio_risk * _ratio_risk

        return max(0.0, min(1.0, ratio_risk))



