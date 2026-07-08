from __future__ import annotations

from typing import TypedDict


class VehicleBasicConfig(TypedDict):
    size_x: float
    size_y: float
    max_jerk: float
    max_deceleration: float
    max_acceleration: float
    init_acceleration: float
    init_jerk: float


class VehicleComboItemConfig(TypedDict):
    distance_to_crossroad_m: float
    init_speed_kmh: float


class VehicleComboConfig(TypedDict):
    combo_list: list[VehicleComboItemConfig]


# Vehicle physical parameters used by the simulator motion update.
# These are not behavior-decision parameters.
VEH_BASIC_CONFIG: VehicleBasicConfig = {
    # Vehicle rectangle size in world coordinates, meters.
    "size_x": 4.5,
    "size_y": 2.0,

    # Motion limits used when applying VehicleControlResult.
    "max_jerk": 4.0,
    "max_deceleration": 6.0,
    "max_acceleration": 2.0,

    # Initial motion state at spawn.
    "init_acceleration": 0.0,
    "init_jerk": 0.0,
}


# Scenario sweep values.
# Each generated combo represents one spawn distance and initial speed pair.
VEH_DISTANCE_TO_CROSSROAD_M_LIST: list[float] = [
    50.0,
    45.0,
    40.0,
    35.0,
    30.0,
]

VEH_INIT_SPEED_KMH_LIST: list[float] = [
    60.0,
    55.0,
    50.0,
    45.0,
    40.0,
    35.0,
    30.0,
]

VEH_COMBO_CONFIG: VehicleComboConfig = {
    "combo_list": [
        {
            "distance_to_crossroad_m": distance_m,
            "init_speed_kmh": speed_kmh,
        }
        for distance_m in VEH_DISTANCE_TO_CROSSROAD_M_LIST
        for speed_kmh in VEH_INIT_SPEED_KMH_LIST
    ],
}
