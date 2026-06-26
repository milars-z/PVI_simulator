# interaction/vehicle_cost_config.py

from __future__ import annotations


# ============================================================
# Cost items
# ============================================================

VEHICLE_COST_ITEMS: list[str] = [
    "collision_cost",
    "near_speed_cost",
    "ttc_conflict_cost",
    "stopping_feasibility_cost",
    "early_slowdown_cost",
    "jerk_cost",
    "deceleration_cost",
]


# ============================================================
# Cost weights
# ============================================================

VEHICLE_COST_WEIGHTS: dict[str, float] = {
    # Safety
    "collision_cost": 10.0,
    "near_speed_cost": 3.0,
    "ttc_conflict_cost": 2.5,
    "stopping_feasibility_cost": 2.0,

    # Efficiency
    "early_slowdown_cost": 1.0,

    # Comfort
    "jerk_cost": 0.5,
    "deceleration_cost": 0.8,
}


# ============================================================
# Threshold config
# ============================================================

VEHICLE_COST_CONFIG: dict[str, float] = {
    # -------------------------
    # Safety
    # -------------------------
    # 车辆与行人的安全距离
    "safe_distance_m": 3.0,
    "safe_speed_mps":2.0,

    # TTC gap 小于这个值时风险指数最高
    "min_ttc_s": 1.0,

    # TTC gap 大于该值视为安全
    "safe_ttc_s":5.0,


    # stopping ratio 小于该值认为安全
    "safe_stopping_ratio": 0.8,

    # stopping ratio 大于该值认为危险
    "danger_stopping_ratio": 1.0,

    # 行人过马路意愿阈值
    "cross_probability_threshold": 0.5,

    # -------------------------
    # Efficiency
    # -------------------------
    # 车辆低于该速度认为进入低速状态
    "low_speed_threshold_mps": 2.0,

    # 如果距离人行道超过该值还低速，认为过早减速
    "early_stop_distance_m": 20.0,

    # -------------------------
    # Comfort
    # -------------------------
    "max_jerk_mps3": 2.5,
    "accept_jerk_mps3": 1.5,
    "max_deceleration_mps2": 4.0,
    "accept_deceleration_mps2": 2.0
}